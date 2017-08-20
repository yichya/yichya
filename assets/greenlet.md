# Gevent 分享 （1） 协程核心：Greenlet

目录：

* 协程核心：Greenlet
* gevent.core 与事件模型：libev
* 调度核心：gevent.hub
* 其他的一些组件

ref:

* https://cyrusin.github.io/2016/07/28/greenlet-20150728/

## 线程与协程

简单的说：

* 线程由系统的调度器在内核空间中进行线程之间的轮转
* 协程由用户空间中的程序自行决定何时在协程之间进行轮转。

常见应用：

* Lua
* Go
* 与系统的多路 IO 复用（epoll）或者真·异步 IO（比如 IOCP）协作的 libev/libuv
	* Node.js
	* Gevent
	* Python-libev

引用一张性能测试的图。

![](http://images2015.cnblogs.com/blog/1089769/201702/1089769-20170206161920057-404494008.png)

## Greenlet

Greenlet 是 Python 世界中比较典型的一个协程实现。

```py
from greenlet import greenlet

def test1():
    print 12
    gr2.switch()
    print 34

def test2():
    print 56
    gr1.switch()
    print 78

gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()
print "end"
```

这个程序的运行顺序是：

* 12
* 56
* 34
* end

## Greenlet 如何实现上下文的切换

切换的原理说来并不复杂：

将一个子过程封装进一个 Greenlet 里，而一个 Greenlet 代表了一段 C 的栈内存。
在 Greenlet 里执行 Python 的子过程(通常是个函数)，当要切换出去的时候，保存当前 Greenlet 的栈内存，方法是 `memcpy` 到堆上。
恢复的时候再把堆上的上下文（运行的时候栈内存的内容）拷贝到栈上，然后释放堆上的内存。
恢复栈顶只需要将当前线程的 `top_frame` 修改为恢复的 Greenlet 的 `top_frame`就行。

Greenlet 结构体中保存了这些信息：

```c
typedef struct _greenlet {
	PyObject_HEAD 					// PyObject 公共数据

	char* stack_start;				
	char* stack_stop;				// stack 原本的区域

	char* stack_copy;				
	intptr_t stack_saved;			// 指向堆上保存的 stack 副本（1）

	struct _greenlet* stack_prev;   // 用于 switch() 时候的遍历操作
	struct _greenlet* parent;       // 父 Greenlet（2）
	PyObject* run_info;             // 用于多线程环境下确定某一 Greenlet 是属于哪一个线程
	struct _frame* top_frame;       // Py 虚拟机的 Frame，用于恢复 vm 的执行状态

	int recursion_depth;			// 这个不是很明确……推测是 Greenlet 对递归的支持十分有限，这个是用于判断是否无穷递归的
	
	PyObject* weakreflist;			// 用于 GC

	PyObject* exc_type;
	PyObject* exc_value;
	PyObject* exc_traceback;		// 这个 Greenlet 用于 reraise 的异常

	PyObject* dict;					// __dict__
} PyGreenlet;
```

（1）Stack layout for a greenlet:
```
               |     ^^^       |
               |  older data   |
               |               |
  stack_stop . |_______________|
        .      |               |
        .      | greenlet data |
        .      |   in stack    |
        .    * |_______________| . .  _____________  stack_copy + stack_saved
        .      |               |     |             |
        .      |     data      |     |greenlet data|
        .      |   unrelated   |     |    saved    |
        .      |      to       |     |   in heap   |
 stack_start . |     this      | . . |_____________| stack_copy
               |   greenlet    |
               |               |
               |  newer data   |
               |     vvv       |
```

（2）父 Greenlet：所有的 Greenlet 都有一个父 Greenlet，当前 Greenlet 退出时，只要返回到父 Greenlet 即可。同时一个隐含的 main Greenlet 是这个树形结构的根节点。记得上面 12-56-34 的例子嘛？执行完 56 之后切换回的是 main Greenlet，所以 print(78) 不会运行。

手动指定父子关系可以这样：

```py
from greenlet import greenlet
 
def test1():
    print 12
    gr2.switch()
    print 34
 
def test2():
    print 56
 
gr1 = greenlet(test1)
gr2 = greenlet(test2, gr1)
gr1.switch()
print 78
```

运行结果是：

* 12
* 56
* 34
* 78

## Greenlet 与我们常用的 yield、yield from 的区别

基于 yield 实现的协程往往只能切换回自己的直接或间接调用者，要想在嵌套的调用中切换出去是比较麻烦的。本质上是因为 yield 只能保留栈顶的帧，Python3 对此有改进，可以通过 yield from 嵌套的挂起内层过程调用，但依然不能任意的切换到其他上下文。

而 Greenlet 就可以，只要一个过程被封装进一个 Greenlet，可以认为这个 Greenlet 就成了一个可以随时挂起和恢复的实体。这个过程中不仅仅有 Python vm 的 top frame，同时更多的存储在栈上的信息都会被复制到堆中供后续使用。*Todo 举个例子*


## Greenlet 之间传递消息

switch 函数可以接收参数，并用在 Greenlet 初始化或者是返回值中。

```py
from greenlet import greenlet
 
def test1():
    print 12
    y = gr2.switch(56)
    print y
 
def test2(x):
    print x
    gr1.switch(34)
    print 78
 
gr1 = greenlet(test1)
gr2 = greenlet(test2)
gr1.switch()
```

