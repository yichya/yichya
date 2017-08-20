# Gevent 分享 （2） gevent.core 与事件模型：libev

目录：

* 协程核心：Greenlet
* gevent.core 与事件模型：libev
* 调度核心：gevent.hub
* 典型应用：gevent.socket

ref:

https://yuyang0.github.io/articles/gevent.html

libev 是一个跨平台的事件库，在类 unix 系统上会使用

gevent.core 基本上是对 libev 的封装：

```
This module is a wrapper around libev__ and follower the libev API pretty closely. Note,
that gevent creates an event loop transparently for the user and runs it in a dedicated
greenlet (called hub), so using this module is not necessary. In fact, if you do use it,
chances are that your program is not compatible across different gevent version (gevent.core in
0.x has a completely different interface and 2.x will probably have yet another interface).
```

## libev 的 Watcher 和 Loop

Watcher 实际上是用来封装各种类型的事件的，不同类型的事件会有不同类型的 watcher，比如 `ev_io`、 `ev_timer`。该结构一般会有一个回调函数，当事件触发时就会调用回调函数。Watcher 会有两种函数（注意 TYPE 代表 Watcher 类型，可以是 `io`，`timer`, `signal` 等等）：
* `ev_TYPE_init` 对 Watcher 对象进行初始化。对 IO 而言该函数是 `ev_io_init`，对 timer 而言，该函数是 `ev_timer_init`。
* `ev_TYPE_set` 与 init 系列函数的区别是该函数一般不设置 callback
* `ev_TYPE_start` 将 Watcher 注册到事件循环中，这样就可以监听事件了。

Loop 即是循环，用于检查所有注册在其中的 Watcher 是否获得到事件。

## gevent.core 的 API

gevent.core 对 libev 的这些组件进行了封装。

### Watcher

这是 libev 的 watcher（ev_watcher) 对象的封装，以 io 为例。

```
#define WATCHER_BASE(TYPE)                                            \
    cdef public loop loop                                             \
    cdef object _callback                                             \
    cdef public tuple args                                            \
    cdef readonly int _flags                                          \
    cdef libev.ev_##TYPE _watcher                                     \

cdef public class io(watcher) [object PyGeventIOObject, type PyGeventIO_Type]:

    WATCHER_BASE(io)

    def start(self, object callback, *args, pass_events=False):
        CHECK_LOOP2(self.loop)
        if callback is None:
            raise TypeError('callback must be callable, not None')
        self.callback = callback
        if pass_events:
            self.args = (GEVENT_CORE_EVENTS, ) + args
        else:
            self.args = args
        LIBEV_UNREF
        libev.ev_io_start(self.loop._ptr, &self._watcher)

    def __init__(self, loop loop, int fd, int events, ref=True, priority=None):
        if fd < 0:
            raise ValueError('fd must be non-negative: %r' % fd)
        if events & ~(libev.EV__IOFDSET | libev.EV_READ | libev.EV_WRITE):
            raise ValueError('illegal event mask: %r' % events)
        libev.ev_io_init(&self._watcher, <void *>gevent_callback_io, fd, events)
        self.loop = loop
        if ref:
            self._flags = 0
        else:
            self._flags = 4
        if priority is not None:
            libev.ev_set_priority(&self._watcher, priority)
```

WATCHER_BASE 定义了一系列的属性:

* `loop` 实际是上面分析的 `loop` 类的一个实例
* `_watcher` cwatcher 对象，也就是一个 libev 的 ev_io 对象
* `callback` 回调函数，注意该回调函数是由上层传递进来，它不是由libev直接调用，而是由 libev 的回调函数调用，具体到本例就是被 `gevent_callback_io` 调用。
* `args` 一个元组，传递给回调函数的参数
* `__init__` 该函数会设置 loop 属性，同时初始化 libev 的 io watcher 对象 `_watcher` (主要做两件事: 指定事件类型,指定回调函数), 注意它的回调函数 是 `gevent_callback_io`
* `start` 该函数会设置回调函数以及参数，这里设置的回调函数是上层传入的，不要和libev的回调函数混淆，同时调用 `ev_io_start` 将该Watcher 注册到 libev 的事件循环中。

为了弄明白 libev 事件循环的过程，我接下来分析 `gevent_callback_io`。

`gevent_callback_io`

```
#define GET_OBJECT(PY_TYPE, EV_PTR, MEMBER)                             \
    ((struct PY_TYPE *)(((char *)EV_PTR) - offsetof(struct PY_TYPE, MEMBER)))

static void gevent_callback_io(struct ev_loop *_loop, void *c_watcher, int revents) {
    struct PyGeventIOObject* watcher = GET_OBJECT(PyGeventIOObject, c_watcher, _watcher);
    gevent_callback(watcher->loop, watcher->_callback, watcher->args, (PyObject*)watcher, c_watcher, revents);
}
```

`GET_OBJECT` 的作用是通过结构体中某一个域的指针来获得整个结构体的指针。如果你熟悉 linux 内核就会发现它和 `container_of` 的功能很相似。所以这里实际就是根据 cwatcher 对象 `_watcher` 来获得 watcher 的指针，接着就调用 `gevent_callback`。

```
static void gevent_callback(struct PyGeventLoopObject* loop, PyObject* callback,
                            PyObject* args, PyObject* watcher, void *c_watcher,
                            int revents) {
    ......
    result = PyObject_Call(callback, args, NULL);
    ......
}
```

所以该函数就调用了上层传入的 callback。

下面这些就是对 libev 的 Watcher 的封装：

```
#ifdef _WIN32
    def io(self, libev.vfd_socket_t fd, int events, ref=True, priority=None):
        return io(self, fd, events, ref, priority)
#else
    def io(self, int fd, int events, ref=True, priority=None):
        return io(self, fd, events, ref, priority)
#endif

    def timer(self, double after, double repeat=0.0, ref=True, priority=None):
        return timer(self, after, repeat, ref, priority)

    def signal(self, int signum, ref=True, priority=None):
        return signal(self, signum, ref, priority)

    def idle(self, ref=True, priority=None):
        return idle(self, ref, priority)

    def prepare(self, ref=True, priority=None):
        return prepare(self, ref, priority)

    def check(self, ref=True, priority=None):
        return check(self, ref, priority)

    def fork(self, ref=True, priority=None):
        return fork(self, ref, priority)

    def async(self, ref=True, priority=None):
        return async(self, ref, priority)
```

注意上面是 Cython，上面的一系列方法实际是 libev 中 Watcher 的等价物。比如你调用 `lp.io(fd, 1)`，就创建了一个监听 fd 的 read 事件的 Watcher 对象，至于其它的 api 都是类似，每一个 Watcher 对象都有一个 start 方法，该方法接受一个回调函数以及一系列传递给回调函数的参数，调用该方法就会将 Watcher 对象注册到 libev 的事件循环上。

```
read_watcher = lp.io(fd, 1)
read_watcher.start(cb, args)
```

运行上面的两行代码，那么当 fd 上读就绪时，那么就会调用 cb 函数，并且会把 args 传递给 cb 函数。在 Gevent 中，回调函数一般是协程的 switch 方法，这样一旦调用，那么就切换到另一个协程中去执行。

```



```

### Loop

假设 Loop 代表类，loop 代表实例：

* `loop.run` 启动事件循环
* `loop.run_callback(fun, *args)` 将 `fun` 注册给 `loop` 的 `_prepare watcher`，这样 `fun` 就会在事件循环要阻塞时运行，`spawn` 以及 `rawlink` 都会使用该方法.
* `loop.io` 创建一个 IO watcher 实例，调用该实例的 `start` 方法来注册回调函数，同时将该 `watcher` 放入事件循环。
* `loop.timer` 创建 Timer Watcher 对象
* `loop.signal` 创建 Signal Watcher 对象
