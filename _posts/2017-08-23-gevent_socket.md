---
layout: post
title:  Gevent（4）典型应用：gevent.socket
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

这里结合前面介绍的原理，看一看 gevent.socket 的实现。

## 初始化

```py
class socket(object):
    """
    gevent `socket.socket <https://docs.python.org/3/library/socket.html#socket-objects>`_
    for Python 3.

    This object should have the same API as the standard library socket linked to above. Not all
    methods are specifically documented here; when they are they may point out a difference
    to be aware of or may document a method the standard library does not.
    """

    # Subclasses can set this to customize the type of the
    # native _socket.socket we create. It MUST be a subclass
    # of _wrefsocket. (gevent internal usage only)
    _gevent_sock_class = _wrefsocket

    def __init__(self, family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None):
        # Take the same approach as socket2: wrap a real socket object,
        # don't subclass it. This lets code that needs the raw _sock (not tied to the hub)
        # get it. This shows up in tests like test__example_udp_server.
        self._sock = self._gevent_sock_class(family, type, proto, fileno)
        self._io_refs = 0
        self._closed = False
        _socket.socket.setblocking(self._sock, False)
        fileno = _socket.socket.fileno(self._sock)
        self.hub = get_hub()
        io_class = self.hub.loop.io
        self._read_event = io_class(fileno, 1)
        self._write_event = io_class(fileno, 2)
        self.timeout = _socket.getdefaulttimeout()
```

可以看到这里的重点是创建了两个 event watcher，并设置了 timeout（这个也是依赖 libev 的 timer 实现的）。

## recv

```py
def recv(self, *args):
    sock = self._sock  # keeping the reference so that fd is not closed during waiting
    while True:
        try:
            return sock.recv(*args)
        except error:
            ex = sys.exc_info()[1]
            if ex.args[0] != EWOULDBLOCK or self.timeout == 0.0:
                raise
            # QQQ without clearing exc_info test__refcount.test_clean_exit fails
            sys.exc_clear()
        self._wait(self._read_event)
```

recv 直接调用内置模块的 recv 方法，如果发现该调用会阻塞，那么就调用 _wait 方法：

```py
def _wait(self, watcher, timeout_exc=timeout('timed out')):
    """Block the current greenlet until *watcher* has pending events.

    If *timeout* is non-negative, then *timeout_exc* is raised after *timeout* second has passed.
    By default *timeout_exc* is ``socket.timeout('timed out')``.

    If :func:`cancel_wait` is called, raise ``socket.error(EBADF, 'File descriptor was closed in another greenlet')``.
    """
    assert watcher.callback is None, 'This socket is already used by another greenlet: %r' % (watcher.callback, )
    if self.timeout is not None:
        timeout = Timeout.start_new(self.timeout, timeout_exc, ref=False)
    else:
        timeout = None
    try:
        self.hub.wait(watcher)
    finally:
        if timeout is not None:
            timeout.cancel()
```

根据注释我们知道 `_wait` 方法会使当前的协程暂停，直到 watcher 监听的事件就绪。

代码的关键部分是 `self.hub.wait(watcher)`，这个方法在上面已经分析过，只要明白它会阻塞当前的协程切换到 hub 协程，而如果 watcher 监听的事件就绪，它又会切换会当前协程。在 recv 的例子中，一旦 watcher 监听的事件就绪也就意味着 socket 已经处于读就绪状态，所以也就可以调用内置的 socket 模块的 recv 方法来获得数据了。

## send

```py
    def send(self, data, flags=0, timeout=timeout_default):
        if timeout is timeout_default:
            timeout = self.timeout
        try:
            return _socket.socket.send(self._sock, data, flags)
        except error as ex:
            if ex.args[0] != EWOULDBLOCK or timeout == 0.0:
                raise
            self._wait(self._write_event)
            try:
                return _socket.socket.send(self._sock, data, flags)
            except error as ex2:
                if ex2.args[0] == EWOULDBLOCK:
                    return 0
                raise
```

跟上面的 recv 十分类似。先尝试 send，如果发现会阻塞就 wait；当 socket 就绪的时候，切换回当前协程后再尝试 send。