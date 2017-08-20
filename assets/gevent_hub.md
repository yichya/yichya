# Gevent 分享 （3） Gevent 的调度核心：Hub 

目录：

* 协程核心：Greenlet
* gevent.core 与事件模型：libev
* 调度核心：gevent.hub 
* 其他的一些组件

ref:

* https://www.xncoding.com/2016/01/02/python/gevent.html
* http://ju.outofmemory.cn/entry/111432
* http://www.maiziedu.com/course/747/
* http://www.topjishu.com/1711.html
* http://sdiehl.github.io/gevent-tutorial/
* http://www.cnblogs.com/eric-nirnava/p/4614540.html

## gevent.hub 

```
A greenlet that runs the event loop.

It is created automatically by :func:`get_hub`.

**Switching**

Every time this greenlet (i.e., the event loop) is switched *to*, if
the current greenlet has a ``switch_out`` method, it will be called. This
allows a greenlet to take some cleanup actions before yielding control. This method
should not call any gevent blocking functions.
```

既然 gevent 很大程度上依赖 libev，那么势必会需要一个组件用于运行 ev_loop，并且将事件准确分发到不同的 Greenlet 上。在 gevent 里面 Hub 就起到这个作用。

## Waiter

Greenlet 的很大一个问题在于，除了在 switch 的时候提供参数，或者 throw 一个异常到 Greenlet 中之外，并没有更好的方法在 Greenlet 之间传递参数。Gevent 利用 switch 和 throw 实现了一个名为 Waiter 的机制。

```
Waiter is a wrapper around greenlet's ``switch()`` and ``throw()`` calls that makes them somewhat safer:
```

Waiter 可以暂存一个 Value 值，等待 Hub 将其取出并发送到正确的接受者。Waiter 本身也是一个 Greenlet。该类的实例有一个 value 属性, 一个 `_exception` 属性, 一个 `get` 方法, 一个 `switch` 方法，他们的行为是这样的：

* `get` 当你在一个协程中调用get方法时, 它会先检查 `_exception` 的值, 如果不为默 认的 `_NONE`，那么它就会根据 value 属性的值来决定是返回 value 的值还是抛出异常，如果 `_exception` 为默认值, 它会设置 `greenlet` 属性为当前的协程对象，接着就会切换到 `hub` 协程.
* `switch` 实际就是调用 Waiter 对象的 `greenlet` 属性的 `switch` 方法，这样就切换到了对应的协程，一般会注册到某个 Watcher 的回调函数。如果 `greenlet` 属性为 None，那么意味着 `switch` 在 `get` 之前运行了，那么就简单的设置下 `value` 以及 `_exception` 属性。需要等待的协程调用 `get` 方法，这样该协程就会挂起，其他的协程（Hub）调用 `switch` 方法切换到因等待而挂起的协程：

```py
class Hub(greenlet):
    ...
    def wait(self, watcher):
        waiter = Waiter()
        unique = object()
        watcher.start(waiter.switch, unique)
        try:
            result = waiter.get()
            assert result is unique, 'Invalid switch into %s: %r (expected %r)' % (getcurrent(), result, unique)
        finally:
            watcher.stop()
    ...
    def switch(self, value=None):
        """Switch to the greenlet if one's available. Otherwise store the value."""
        greenlet = self.greenlet
        if greenlet is None:
            self.value = value
            self._exception = None
        else:
            assert getcurrent() is self.hub, "Can only use Waiter.switch method from the Hub greenlet"
            switch = greenlet.switch
            try:
                switch(value)
            except: # pylint:disable=bare-except
                self.hub.handle_error(switch, *sys.exc_info())
    ...
```

同时对于有多个 Value 值需要等待的情况，Hub 中也实现了 iwait（generator）和 _MultipleWaiter。

直接使用 Waiter 是很不安全的，可能会导致某一 Greenlet 彻底失去被轮转到的可能性。Gevent 利用 Waiter 机制实现了我们比较熟悉的 Queue、Event、AsyncResult 等数据结构，我们最好使用 Gevent 提供的我们更喜闻乐见的数据结构来进行跨 Greenlet 的通信。

## Gevent 对 Greenlet 的扩展

前面对 Greenlet 的介绍中我们知道，Greenlet 启动的时候会有一个 main Greenlet 作为所有 Greenlet 的 root。对于 Gevent，我们知道 Hub 承担了在所有 Greenlet 之间轮转的任务。

### spawn

gevent.spawn 实际就是 Greenlet 类的 spawn 方法，该方法直接创建一个 Greenlet 实例。注意该实例的 parent 是 hub，而不是默认的主协程。这样的用处是当协程完成退出时，程序会继续执行 hub 的事件循环。

```py
class Greenlet(greenlet):
    def __init__(self, run=None, *args, **kwargs):
        hub = get_hub()
        greenlet.__init__(self, parent=hub)

    @classmethod
    def spawn(cls, *args, **kwargs):
        """Return a new :class:`Greenlet` object, scheduled to start.
        The arguments are passed to :meth:`Greenlet.__init__`.
        """
        g = cls(*args, **kwargs)
        g.start()
        return g
```

### start

start 方法实际上就是把该实例丢到 hub 协程的循环当中，这样这个新建的协程就可以被 hub 调度了。

```py
    def start(self):
        """Schedule the greenlet to run in this loop iteration"""
        if self._start_event is None:
            self._start_event = self.parent.loop.run_callback(self.switch)


    def run_callback(self, func, *args):
        CHECK_LOOP2(self)
        cdef callback cb = callback(func, args)
        self._callbacks.append(cb)
        libev.ev_ref(self._ptr)
        return cb
```
上面的代码先创建一个 `callback` 实例 cb，接着将这个实例放进 `_callbacks` 列表中。在 core 部分我们分析了 `_callbacks` 列表的所有 `callback` 实例都会被 `_prepare` Watcher 的回调函数 `gevent_run_callbacks` 运行，这样实际就是启动了协程.


