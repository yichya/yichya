---
layout: post
title:  Gevent（3）调度核心：gevent.hub 
categories:
  - Technology
tags:
  - gevent
  - python
  - libev
---

Gevent 技术分享系列。

目录：

* 协程核心：Greenlet
* gevent.core 与事件模型 libev
* 调度核心：gevent.hub 
* 典型应用：gevent.socket

ref:

* https://www.xncoding.com/2016/01/02/python/gevent.html
* http://ju.outofmemory.cn/entry/111432
* http://sdiehl.github.io/gevent-tutorial/


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

前面我们分析了 gevent 对 libev 的封装以及一个事件具体的触发流程是什么样的。那么 `ev_loop` 运行在哪里呢？从 `ev_loop` 取得的数据如何准确的发送到对应的 Greenlet 上呢？在 gevent 里面 Hub 就起到这个作用。

## Waiter

Greenlet 存在一个缺陷：除了在 switch 的时候提供参数，或者 throw 一个异常到 Greenlet 中之外，并没有更好的方法在 Greenlet 之间传递参数。Gevent 利用 switch 和 throw 实现了一个名为 Waiter 的机制。

```py
class Waiter(object):
    """
    A low level communication utility for greenlets.

    Waiter is a wrapper around greenlet's ``switch()`` and ``throw()`` calls that makes them somewhat safer:

    * switching will occur only if the waiting greenlet is executing :meth:`get` method currently;
    * any error raised in the greenlet is handled inside :meth:`switch` and :meth:`throw`
    * if :meth:`switch`/:meth:`throw` is called before the receiver calls :meth:`get`, then :class:`Waiter`
      will store the value/exception. The following :meth:`get` will return the value/raise the exception.

    The :meth:`switch` and :meth:`throw` methods must only be called from the :class:`Hub` greenlet.
    The :meth:`get` method must be called from a greenlet other than :class:`Hub`.
    ...
```

Waiter 可以暂存一个 Value 值，等待 Hub 将其取出并发送到正确的接受者。Waiter 本身也是一个 Greenlet。该类的实例有一个 `value` 属性, 一个 `_exception` 属性, 一个 `get` 方法, 一个 `switch` 方法，他们的行为是这样的：

* `get` 当在一个协程中调用 `get` 方法时, 它会先检查 `_exception` 的值, 如果不为默认的 `_NONE`，那么它就会根据 `value` 属性的值来决定是返回 value 的值还是抛出异常，如果 `_exception` 为默认值, 它会设置 `greenlet` 属性为当前的协程对象，接着就会切换到 `hub` 协程，等待之后切换回来并取得 Hub 传来的值。

```py
    def get(self):
        """If a value/an exception is stored, return/raise it. Otherwise until switch() or throw() is called."""
        if self._exception is not _NONE:
            if self._exception is None:
                return self.value
            else:
                getcurrent().throw(*self._exception)
        else:
            if self.greenlet is not None:
                raise ConcurrentObjectUseError('This Waiter is already used by %r' % (self.greenlet, ))
            self.greenlet = getcurrent()
            try:
                return self.hub.switch()
            finally:
                self.greenlet = None
```

* `switch` 实际就是调用 Waiter 对象的 `greenlet` 属性的 `switch` 方法，这样就切换到了对应的协程，一般会注册到某个 Watcher 的回调函数。如果 `greenlet` 属性为 None，那么意味着 `switch` 在 `get` 之前运行了，那么就简单的设置下 `value` 以及 `_exception` 属性。需要等待的协程调用 `get` 方法，这样该协程就会挂起。当数据可用时，Hub 调用该协程的 `switch` 方法切换到因等待而挂起的协程：

```py
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
```

同时对于有多个 Value 值需要等待的情况，Waiter 中也实现了 iwait（generator）和 _MultipleWaiter。

直接使用 Waiter 是很不安全的，可能会导致某一 Greenlet 彻底失去被轮转到的可能性。Gevent 利用 Waiter 机制实现了我们比较熟悉的 Queue、Event、AsyncResult 等数据结构，我们最好使用 Gevent 提供的我们更喜闻乐见的数据结构来进行跨 Greenlet 的通信。

## Hub

hub 是一个单例，从 get_hub() 的源码就可以看出来：

```py
import _thread
_threadlocal = _thread._local()

def get_hub(*args, **kwargs):
    global _threadlocal
    try:
        return _threadlocal.hub
    except AttributeError:
        hubtype = get_hub_class()
        hub = _threadlocal.hub = hubtype(*args, **kwargs)
        return hub
```

为了方便介绍，下面给出 Hub 类的一个典型使用场景，下面的代码只摘取了关键部分：

```py
# fileobject.py 中:
# 创建一个 io 类型的 watcher
# 用户监视 fileno 这个文件描述符
self._read_event = io(fileno, 1)
##############################################
# fileobject.py 中:
# IO 完成后阻塞，将当前 greenlet 切换到 hub
# 让出控制权
# 等到感兴趣的 IO 事件发生后
# hub 会切换到这个点，继续执行
self.hub.wait(self._read_event)
##############################################
# Hub:
# hub.wait 函数：
        waiter = Waiter()
        unique = object()
        # 这个 watcher 就是 _read_event
        # 下面将 waiter.switch 这个回调函数，绑定到 watcher 上（io 类型的）
        watcher.start(waiter.switch, unique) 
        try:
            # 切换到 hub, 等待 io 事件被触发
            # 然后 hub 切换到被挂起的 greenlet 继续运行
            result = waiter.get()
        finally:
            watcher.stop()
##############################################
# Wait:
# wait.get 函数:
            self.greenlet = getcurrent()
            try:
                # 切换到 hub
                return self.hub.switch()
            finally:
                self.greenlet = None
##############################################
# Hub:
# hub.switch 函数:
        # 切换到 hub
        return greenlet.switch(self)
```

上面代码的功能概括为：

在普通的 greenlet 中（非 Hub）中，创建一个 io 类型的 watcher ，再将这个 watcher 和当前 greenlet 关联起来，最后从当前 greenlet 切换到 Hub，等待 libev 的 loop 检测 socket 上发生的 IO 事件，当事件发生后，从 Hub 切换到刚才被挂起的 greenlet 继续执行。

下面做简要分析：

当 IO 完成并发生阻塞事件时，为了能异步的得到事件通知，调用 `self.hub.wait(self._read_event)` 将 watcher 加入到 libev 的 loop 循环中。调用 `hub.wait` 方法后，会从当前 greenlet 切换到 hub。hub 管理着所有的 greenlet，并将这些 greenlet 和 libev 的 loop 关联起来。这是通过 libev 的 watcher 来关联的。在 hub.wait 中，启动一个 Waiter， 并将 waiter.switch 这个回调函数和 watcher 关联起来。最后执行 `waiter.get` 将当前 greenlet 切换到 Hub。这时 libev 如果检测到发生了 greenlet 感兴趣的事件（前面讲过的 `epoll_wait()` 与回调），就会从 Hub 切换到刚才被挂起的 greenlet，并从挂起处继续执行。

### `init`

`__init__ ` 函数的功能是初始化设置 `loop` 类，并初始化：

```py
loop_class = config('gevent.core.loop', 'GEVENT_LOOP')
...
self.loop = loop_class(flags=loop, default=default)
```

`gevent.core.loop` 是 gevent 的 C 模块 core.so 中的 `loop` 类，也就是我们前面提到的 libev 的 loop 做了一层包装。

### wait

```py
def wait(self, watcher):
    waiter = Waiter()         # 创建 Waiter 类实例
    unique = object()         # object() 是一个唯一的对象，作为从 main greenlet 返回时的跟踪对象
    watcher.start(waiter.switch, unique) # 将 waiter.switch 这个 callback 附加到 watcher 上，参数为 unique
    try:
        result = waiter.get() # 执行 waiter.get 从当前 greenlet 切换到 main greenlet
                              # 当 watcher 感兴趣的事件发生后，触发调度，从 main greenlet 切换回来，代码继续执行
        assert result is unique, 'Invalid...'
    finally:    
        watcher.stop()
```

wait 方法的作用是挂起当前的协程，直到 watcher 监听的事件就绪。它创建一个 Waiter 实例 waiter，接着将 waiter 的 `switch` 方法注册到 watcher 上。这样当 watcher 监听的事件就绪后就会调用实例的 `switch` 方法，接着就调用 waiter 的 `get` 方法, 根据 watcher 监听的事件就绪的快慢，这里有两种可能：

* `get` 在 `switch` 之前运行：get 会设置 waiter 的 greenlet 属性为当前执行的协程，接着切换到 hub，当将来某个时候事件就绪，那么调用 waiter 的 switch，switch 会调用 greenlet 属性的 switch 方法，这样就切换回了当前运行的协程。
* `get` 在 `switch` 之后运行: 这种情况比较少见，可是也是存在的，这种情况下运行 switch 时，waiter 对象的 greenlet 属性为None, 所以 switch 方法只是简单的设置 waiter 的 value 属性，接着调用 get 会直接返回 value 属性，而不阻塞。

### switch

```py
def switch(self):
    switch_out = getattr(getcurrent(), 'switch_out', None) # 在当前 greenlet 对象中寻找 `switch_out` 属性，如果找到就调用。
    if switch_out is not None:
        switch_out()
    return greenlet.switch(self) # 调用 `greenlet.switch(self)`，切换到 hub。
```

这里的 `greenlet` 是 C 模块的 `greenlet.so` 中 `greenlet` 类的方法，参数 `self` 为当前的 `greenlet` 对象。

### join

`join` 方法的功能是，等待 Event loop 执行完毕，当没有活动的 greenlet、正在运行的 server、超时器、watcher 以后，join 方法会退出。当 `timeout` 参数不为 `None` 时，启动一个超时器，等待 timeout 秒，再切换到 hub。 否则直接切换到 hub。其实 join 方法的核心只是切换到 hub，但为什么切换到 hub 就能等到 Event loop 退出呢？因为切换到 hub 之后，才能由 hub 管理所有的 greenlet，当 watcher 上事件发生时，除了 hub 之外的其他 greenlet 才能有机会运行。当其他所有 greenlet 都运行完毕，Event loop 自然就退出了。看起来有点故弄玄虚的意思，所以其实只需要 switch 到 hub 即可。

```py
def join(self, timeout=None):
    assert getcurrent() is self.parent, "only possible from the MAIN greenlet"
    if self.dead:
        return True
    waiter = Waiter()                # 初始化一个 Waiter 类的实例
    if timeout is not None:
        timeout = self.loop.timer(timeout, ref=False)
        timeout.start(waiter.switch) # 如果提供了 timeout，会启动超时器，等待 timeout 秒后，在切换到 main greenlet
    try:
        try:
            waiter.get()             # 如果未提供 timeout 参数，则直接切换到 main greenlet
        except LoopExit:
            return True
    finally:
        if timeout is not None:
            timeout.stop() 
    return False 
```

### run

```py
def run(self):
    assert self is getcurrent(), 'Do not call Hub.run() directly'
    while True:
        loop = self.loop
        loop.error_handler = self
        try:
            loop.run()
        finally:
            loop.error_handler = None  # break the refcount cycle
        self.parent.throw(LoopExit('This operation would block forever'))
```

`run` 方法是 hub 的核心，由 `run` 方法来启动 libev 的 loop。

## Gevent 对 Greenlet 的扩展

前面对 Greenlet 的介绍中我们知道，Greenlet 启动的时候会有一个 main Greenlet 作为所有 Greenlet 的 root。对于 Gevent，我们知道 Hub 承担了在所有 Greenlet 之间轮转的任务。为了把所有 Greenlet 默认的 Parent 从 main Greenlet 改为 Hub 并且正确完成调度，Gevent 在这里做了一些简单的工作。

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


