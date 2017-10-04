---
layout: post
title: Doufm for Raspberry Pi (v3)
categories:
  - Small Things
tags:
  - raspberrypi
  - python
---
这次折腾的实在是太曲折了。本来觉得不会遇到什么坑，最多难搞，结果遇到了好多好多完全想不到的问题，换了好多种解决方案，最后终于成功。在这里不能全部记录，其实挺遗憾的 :)

上周四，草民购买的一大堆树莓派配件就到货了。

* Nokia 5110 拆机屏幕一个。
* 数字万用表。
* 轻触式按钮
* 若干连线
* 面包板
* ...

后续的两个版本自然就计划用上新买的这些零件，分为两个不同版本，一个做显示部分，另一个做用户控制部分。
我决定先进行屏幕方面的工作，因为这个看起来可能相对简单，同时也更容易看到效果。

<!-- more -->

拿到屏幕，首先搜索如何使用。查到了如下两个链接：

* http://hugozhu.myalert.info/2013/03/24/20-raspberry-pi-drive-nokia-5110.html
* http://www.shumeipai.net/thread-19282-1-1.html

第一个通过调用 RPi.GPIO 库操作屏幕，显示简单的英文字母。

*此处应该有图*

第二个则是一个比较完整的基于 C 语言的应用，可以播放豆瓣电台和本地音乐等，还能显示中文。

*此处应该有图*

看似第二个已经可以满足我的要求，似乎把 API 改一改就能用，然而我按照作者的说明进行测试时……

* 编译始终无法顺利完成，原因是无法顺利的链接上 iconv 开头的几个函数，虽然目录里面明明有一个 libiconv.a。
* 修改编译参数勉强编译成功后运行，屏幕却完全没有反应。

查询得知，树莓派 2B 使用的 SoC 与一代不同，因而操作 GPIO 相关的代码也不再有效。于是，我只能设法应用第二个项目中的中文显示模块，并将其重新封装后与第一个项目结合使用。

首先，这里是作者原来的代码。

<pre>
$ ls -al
total 2761
drwxr-xr-x 1 yichya 197609       0 7月   9  2013 ./
drwxr-xr-x 1 yichya 197609       0 12月  5 13:17 ../
-rw-r--r-- 1 yichya 197609    4010 4月  17  2013 3310LCD_function.c
-rw-r--r-- 1 yichya 197609     410 4月  17  2013 3310LCD_function.h
-rw-r--r-- 1 yichya 197609   18489 8月  29  2012 asc12font.c
-rw-r--r-- 1 yichya 197609   20275 9月  26  2012 bcm2835.c
-rw-r--r-- 1 yichya 197609   41463 9月  26  2012 bcm2835.h
-rw-r--r-- 1 yichya 197609    7515 5月  10  2013 douban_list.c
-rw-r--r-- 1 yichya 197609      85 11月 20  2012 douban_list.h
-rw-r--r-- 1 yichya 197609   14557 5月   9  2013 douban_radio.c
-rw-r--r-- 1 yichya 197609    1123 5月   8  2013 douban_radio.h
-rw-r--r-- 1 yichya 197609    4916 4月  17  2013 english_6x8_pixel.c
-rw-r--r-- 1 yichya 197609     595 4月  25  2013 hardware.conf
-rw-r--r-- 1 yichya 197609    7868 11月 12  2012 http.c
-rw-r--r-- 1 yichya 197609     506 11月 12  2012 http.h
-rw-r--r-- 1 yichya 197609 1177690 7月  29  2012 hz12font.c
-rw-r--r-- 1 yichya 197609     336 4月  27  2013 input.h
-rw-r--r-- 1 yichya 197609    1028 6月  23  2013 irkey.c
-rw-r--r-- 1 yichya 197609   36388 11月 13  2012 JSON_parser.c
-rw-r--r-- 1 yichya 197609    4678 12月  3  2010 JSON_parser.h
-rw-r--r-- 1 yichya 197609    6007 5月  29  2013 lcd_uilt.c
-rw-r--r-- 1 yichya 197609     404 5月  29  2013 lcd_uilt.h
-rw-r--r-- 1 yichya 197609 1356510 4月  21  2013 libiconv.a
-rw-r--r-- 1 yichya 197609   20648 4月  26  2013 liblirc_client.so
-rw-r--r-- 1 yichya 197609    2384 3月  25  2011 lirc_client.h
-rw-r--r-- 1 yichya 197609     997 5月  10  2013 lircd.conf
-rw-r--r-- 1 yichya 197609     468 6月  23  2013 lircrc
-rw-r--r-- 1 yichya 197609     506 7月   9  2013 makefile
-rw-r--r-- 1 yichya 197609    5455 5月   9  2013 menu.c
-rw-r--r-- 1 yichya 197609     110 9月  11  2012 menu.h
-rw-r--r-- 1 yichya 197609    8007 6月  23  2013 music_list.c
-rw-r--r-- 1 yichya 197609     221 5月  10  2013 music_list.h
-rw-r--r-- 1 yichya 197609     674 5月   8  2013 pi_radio.c
-rw-r--r-- 1 yichya 197609     595 5月  10  2013 player_cmd.c
-rw-r--r-- 1 yichya 197609     107 5月  10  2013 player_cmd.h
-rw-r--r-- 1 yichya 197609    2080 5月   9  2013 radio.pls
-rw-r--r-- 1 yichya 197609     199 5月  29  2013 resource.c
-rw-r--r-- 1 yichya 197609      40 5月  29  2013 resource.h
-rw-r--r-- 1 yichya 197609    4053 5月   9  2013 station_list.c
-rw-r--r-- 1 yichya 197609     358 5月   9  2013 station_list.h
-rw-r--r-- 1 yichya 197609    4167 5月  30  2013 web_list.c
-rw-r--r-- 1 yichya 197609      75 11月 27  2012 web_list.h
</pre>

不难发现，与屏幕显示相关的文件有如下几个：

* lcd_uilt.c/.h（我强烈怀疑作者想写的是 lcd_util）
* 3310LCD_function.c/.h
* bcm2835.c/.h
* asc12font.c 和 hz12font.c 两个字体文件。

简单阅读后，发现作者在 lcd_uilt 中实现屏幕内容的处理并调用了 3310LCD_function.c 和 bcm2835.c 中的代码向屏幕发送控制命令。因此我们只需要保留 lcd_ulit.c/.h、asc12font.c 和 hz12font.c 四个文件就可以了。当然，对 lcd_ulit 进行简单修改也是有必要的。

阅读 lcd_uilt 后，我得到了以下信息：

* 作者在这里实现了 UTF-8 到 GB2312 的编码转换，前面提到的 iconv 便是 Linux 标准库中自带的用于编码转换的库。由此，作者使用的字体应该也是对 GB2312 编码支持最好的。
* 作者定义了一个全局变量 <code>LcdPixelBuffer[6][84]</code> 用于临时存放 LCD 屏幕的像素显示信息，同时还定义了用于清除这一缓冲区的方法。
* 作者将几个函数和上面的全局变量导出，在其他的地方调用，通过几个函数对这个二维数组进行操作后将数组中的数据发送给屏幕完成显示。
* 作者将字库单独作为一个 .c 文件链接，节省了重复编译时消耗的时间【*我个 SB 现在才意识到 = = 还特么硬给人改成了 .h*】
* 作者设计了 2 种绘制文字的方式：正常与反色。【其实好像还有一个迷之模式然而作者并没有明确的写出来，调用时感觉与反色没什么区别】

既然 iconv 总是闹别扭（上网搜索后得知这个库好像并不太好用），转换编码的工作我便决定直接使用 Python 自带的 encode() 函数完成，于是我移除了代码中与编码转换相关的部分。

这些代码处理完之后，就应当着手将它做成可以被 Python 环境调用的模块了。通过搜索很容易找到封装使用的代码：

{% highlight c %}
#include <Python.h>

static PyObject* foo_bar(PyObject* self, PyObject* args) {
	// ...
}

static PyMethodDef ModuleMethods[] = {
	{"bar", foo_bar, METH_NOARGS, NULL},
	{NULL, NULL, 0, NULL}
};

static PyModuleDef ModuleDesc = {
	PyModuleDef_HEAD_INIT,
	"foo",
	"foo",
	-1,
	ModuleMethods
};

PyMODINIT_FUNC PyInit_libfoo() {
	PyModule_Create(&ModuleDesc);
}
{% endhighlight %}

这是适用于 Python 3.x 的 Cython 模块封装代码。其中包含模块名称、方法的声明和方法的实现。它完成了如下的工作：

* 定义一个名为 libfoo 的模块。
* 声明一个名为 bar 的方法，指向函数 foo_bar，调用时不需要提供任何参数（METH_NOARGS）。

需要注意的是：

* 为使模块正常工作，我们需要**保证** ModuleMethods 数组最后有一个空白的项目：<code>{NULL, NULL, 0, NULL}</code>
* 模块名与最后一个 PyMODINIT_FUNC 的函数名有严格对应关系，比如编译得到的是 libfoo.so，这个函数就必须叫 PyInit_libfoo()。

按照作者原来对于 lcd_ulit 模块的设计，我们的 Python 模块应该也需完成如下工作：

* 初始化缓冲区，清除缓冲区。
* 接收来自 Python 解释器的参数，在预先定义好的缓冲区中绘制文字。
* 将缓冲区中的数据返回给 Python 解释器。

首先创建一个 module.c 文件，并包含 Python.h。 

第一个函数十分简单，只要写一个不包含参数的函数 clear_buffer 并指向 lcd_ulit 中的 LCD_clear_buffer() 即可。

首先，在 ModuleMethods 数组中添加一行：

<code>{"clear_buffer", clear_buffer, METH_NOARGS, NULL},</code>


然后写函数的实现：

{% highlight c %}
extern void LCD_clear_buffer();

static PyObject* clear_buffer(PyObject* self, PyObject* args) {
	LCD_clear_buffer();
}
{% endhighlight %}

第二个函数 print_string 就需要我们传递参数进去了，ModuleMethods[] 中需要带参数 METH_VARARGS：

<code>{"print_string", print_string, METH_VARARGS, NULL},</code>

然后，我们需要考虑这个函数的设计问题。参考 lcd_ulit 中相关函数的设计，我们需要传入的参数应该有这样几个：

* 绘图点的坐标 x 和 y。
* 要绘制的字符串。
* 绘制模式，也就是正常绘制与反色绘制。

直觉上，我们在调用这个函数的时候应该是这样的：<code>print_string(0, 0, "23333333".encode('gb2312'), 1)</code>

那么，参数列表应当是这样的：int, int, byte, int。在 Cython 扩展时，int 自然不必多说就是 int，而 Python 中的 byte 则需要用一个特定的结构体类型 Py_buffer 来处理。

函数设计好了，那么在函数实现中，如何把参数取出来呢？

在 Python 的 C 扩展中，每一个 Python 对象都是一个 PyObject 结构体，所以函数参数中的 PyObject\* args 就是我们需要处理的参数了。查阅 API 后得知，应当使用 PyArg_ParseTuple() 函数进行 args 的解析。

PyArg_ParseTuple 的用法有些像 C 标准库中的 sscanf()，首先是一个 PyObject\* 指针指向 args 参数，然后是格式串，之后是各变量的地址。关于格式串的定义，i 代表 int，y\* 代表不包含 Unicode 字符的 byte 数组，这是 Python 官方文档推荐的传递二进制数据的方式。其他的格式请参考官方文档。

PyArg_ParseTuple 在失败时会返回 0 并在 Python 解释器环境中抛出一个异常。

{% highlight c %}
static PyObject* print_string(PyObject* self, PyObject* args) {
    unsigned char _x = 0, _y = 0, _mode = 0;
    Py_buffer arg_buffer;

    if(!PyArg_ParseTuple(args, "i|i|y*|i", &_x, &_y, &arg_buffer, &_mode)) {
        return NULL;
    }
	
    //...
{% endhighlight %}

利用 Py_buffer 的 buf 成员取得缓冲区中的 byte 数据，并传递给 lcd_uilt 中的对应函数。操作完成后，调用 PyBuffer_Release() 释放掉 Py_buffer 占用的内存。
这里的 LastLength 为导出的全局变量，其值是上次 LCD_display_string() 时绘图的宽度，这里利用 PyLong_FromLong() 转换为 Python 的 long 类型。

{% highlight c %}
    //...

    unsigned char* orig_str_gb2312 = arg_buffer.buf;

    LCD_display_string(_x, _y, orig_str_gb2312, _mode);
    PyBuffer_Release(&arg_buffer);
    return PyLong_FromLong(LastLength);
}
{% endhighlight %}

最后一个函数 get_pixel_array 是用于将结果传回给 Python 解释器的，也不需要参数。

<code>{"get_pixel_array", get_pixel_array, METH_NOARGS, NULL},</code>

在这里我们需要把 C 语言中的二维数组转换成 Python 可以识别的二维数组，最简单的办法是用几个 List 嵌套。

我们先定义一个 List，然后再定义 6 个 List 并将他们全部放入第一个 List 中。同时，利用 Py_BuildValue() 将 C 的 int 转换为 Python 的 int。

*这里其实我本来想用数组的，不过可能是学艺不精，总是 Segmentation Fault，于是出此下策……*

{% highlight c %}
static PyObject* get_pixel_array(PyObject* self, PyObject* args) {
    PyObject* return_list_0 = PyList_New(0);
    PyObject* return_list_1 = PyList_New(0);
    PyObject* return_list_2 = PyList_New(0);
    PyObject* return_list_3 = PyList_New(0);
    PyObject* return_list_4 = PyList_New(0);
    PyObject* return_list_5 = PyList_New(0);

    int j = 0;

    for (j = 0; j < 84; j++) {
        PyList_Append(return_list_0, Py_BuildValue("i", LcdPixelBuffer[0][j]));
        PyList_Append(return_list_1, Py_BuildValue("i", LcdPixelBuffer[1][j]));
        PyList_Append(return_list_2, Py_BuildValue("i", LcdPixelBuffer[2][j]));
        PyList_Append(return_list_3, Py_BuildValue("i", LcdPixelBuffer[3][j]));
        PyList_Append(return_list_4, Py_BuildValue("i", LcdPixelBuffer[4][j]));
        PyList_Append(return_list_5, Py_BuildValue("i", LcdPixelBuffer[5][j]));
    }

    PyObject* return_list = PyList_New(0);

    PyList_Append(return_list, return_list_0);
    PyList_Append(return_list, return_list_1);
    PyList_Append(return_list, return_list_2);
    PyList_Append(return_list, return_list_3);
    PyList_Append(return_list, return_list_4);
    PyList_Append(return_list, return_list_5);

    return return_list;
}
{% endhighlight %}

这样将二维数组转换成 Python 可以轻松使用的嵌套 List，然后传回给 Python 解释器就行了。

最后检查一下自己测试时使用的环境，修改最后一个函数。我这里使用了 Cygwin 环境和 CMake 构建工具，因此生成的文件名是 cygxxxxx.dll。照样写好最后一个函数的名称。

{% highlight c %}
static PyModuleDef ModuleDesc = {
    PyModuleDef_HEAD_INIT,
    "Get LCD screen pixel array from a GB2312 string",
    "PiLcdString",
    -1,
    ModuleMethods
};

PyMODINIT_FUNC PyInit_cygPiLcdString_pymod() {
    PyModule_Create(&ModuleDesc);
}
{% endhighlight %}

写上一段 CMake 脚本，自动构建动态链接库。*另外 lcd_ulit 实在是不忍直视……既然是核心代码干脆改名，就叫 PiLcdString 好了。*

{% highlight cmake %}
cmake_minimum_required(VERSION 3.3)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
	
project(PiLcdString_pymod)
include_directories("/usr/include/python3.4m")
link_libraries("/lib/libpython3.4m.dll.a")
add_library(PiLcdString_pymod SHARED module.c PiLcdString.c asc12font.h hz12font.h)
{% endhighlight %}

执行
<pre>
cmake ./CMakeLists.txt
make
</pre>
编译得到 cygPiLcdString_pymod.dll，这个文件我们就可以直接用来 import 了。

<pre>
$ python3
Python 3.4.3 (default, May  5 2015, 17:58:45)
[GCC 4.9.2] on cygwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import cygPiLcdString_pymod
>>> cygPiLcdString_pymod.print_string(0, 0, "2333".encode('gb2312'), 1)
24
>>> cygPiLcdString_pymod.get_pixel_array()
[[0, 8, 132, 68, 36, 24, 0, 8, 4, 36, 36, 216, 0, 8, 4, 36, 36, 216, 0, 8, 4, 36, 36, 216, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 3, 2, 2, 2, 3, 0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
</pre>

顺利的得到了迷之数组。但是这个迷之数组谁看得懂是什么鬼啊？果断上实际屏幕测试。

修改原来屏幕显示使用的代码。
{% highlight python %}
# import ...
data = [
    [0, 8, 132, 68, 36, 24, 0, 8, 4, 36, 36, 216, 0, 8, 4, 36, 36, 216, 0, 8, 4, 36, 36, 216,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 3, 2, 2, 2, 3, 0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

# ...

def display_string():
    gotoxy(0, 0)
    for i in range(6):
        for j in range(84):
            lcd_data(data[i][j])
{% endhighlight %}

直接在树莓派上执行。

*此处应该有图*

相当顺利，大功告成。

把几个文件拖到树莓派上，修改一下 PyInit 函数名。然后装好 CMake，准备重新编译。
{% highlight cmake %}
cmake_minimum_required(VERSION 3.3)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
	
project(PiLcdString_pymod)
include_directories("/usr/include/python3.4m")
link_libraries("/usr/lib/arm-linux-gnueabihf/libpython3.4m.a")
add_library(PiLcdString_pymod SHARED module.c PiLcdString.c asc12font.h hz12font.h)
{% endhighlight %}

挺顺利的得到了一个 .so 文件。先直接在 Python 环境里面跑跑看。
<pre>
pi@raspberrypi:~/Raspi_Chn_lcd$ python3
Python 3.4.3+ (default, Oct 10 2015, 09:15:38) 
[GCC 5.2.1 20151028] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import libPiLcdString_pymod
Segmentation Fault
pi@raspberrypi:~/Raspi_Chn_lcd$ 
</pre>

... Excuse Me？？？

卧槽了。仔细检查了半天，确定代码没有问题；换了自己的 Fedora x64 系统重新编译，模块调用依然正常。

莫非是树莓派上的 Python 3.4 损坏了？重新换了 Python 3.5 重新编译依然是 Segmentation Fault。什么鬼？

没办法，硬着头皮上调试器。拿 faulthandler 和 gdb 瞎鼓捣了半天，也没啥头绪。

查了半天，某仁兄曾经提到“由于 Python Arm 平台的关系，无法直接移植……”，隐约感觉可能是 Python 自身的 bug。反正无论是不是 bug，这问题目测不是我能搞得定的。还好这位哥们又指了另外一条路：Python 的 ctypes 模块。

只好强行涨姿势了。

ctypes 是 Python 提供的用来调用 C/C++ 函数的一个库。利用 ctypes，我们可以直接访问动态链接库，调用其中的方法。ctypes 也封装了对指针的操作，可以处理字符串、数组等数据。

那么现在没有 Python 提供的 C/C++ API 了，我们只能导出 C 标准的接口，然后在 Python 中通过 ctypes 调用。回忆一下上面写了哪些导出函数：

{% highlight c %}
static PyMethodDef ModuleMethods[] = {
    {"clear_buffer", clear_buffer, METH_NOARGS, NULL},
    {"print_string", print_string, METH_VARARGS, NULL},
    {"get_pixel_array", get_pixel_array, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};
{% endhighlight %}

于是我们还是需要导出三个函数：

* clear_buffer
* print_string
* get_pixel_array

前两个函数可以相当方便的利用 ctypes 提供的属性访问，最后一个函数返回的是一个二维数组，由于 Python 在这方面支持并不理想，我干脆换了一种方式。

我定义了一个 <code>get_pixel_status(unsigned char x, unsigned char y)</code>，直接返回 LcdPixelBuffer[][] 对应位置的值，这样处理更加直观，也不会很影响速度。

删掉 module.c，修改 CMake 脚本，去掉所有跟 Python 有关的东西。
{% highlight cmake %}
cmake_minimum_required(VERSION 3.3)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
	
project(PiLcdString)
add_library(PiLcdString SHARED PiLcdString.c asc12font.h hz12font.h)
{% endhighlight %}

编译，顺利得到了 libPiLcdString.so。

如何在 Python 中调用我们得到的这个动态链接库呢？

引入 ctypes，然后加载这个动态链接库。
{% highlight python %}
from ctypes import *

lcd = CDLL("./libPiLcdString.so")

# ...
{% endhighlight %}

这样我们就加载好了这个动态链接库，接下来就可以非常简单的访问导出的函数了。

传递参数时，我们需要利用 ctypes 提供的数据类型来处理 Python 的数据类型。比如，c_char() 表示 C 中的 char，c_char_p 表示 C 中的 char\*。

{% highlight python %} 
# ...

def clear_buffer():
    lcd.clear_buffer()


def print_string(x, y, string_to_print, mode):
    lcd.print_string(c_char(x), c_char(y), c_char_p(string_to_print.encode('gb2312')), c_char(mode))


def get_pixel_array():
    return_array = [None] * 6

    for x in range(6):
        return_array[x] = [None] * 84
        for y in range(84):
            return_array[x][y] = lcd.get_pixel_status(c_char(x), c_char(y))

    return return_array;
	

print_string(0, 0, "2333", 1)
print(get_pixel_array())
{% endhighlight %}

直接利用 Python 执行。

<pre>
pi@raspberrypi:~/Raspi_Chn_lcd$ python3 test.py
[[0, 8, 132, 68, 36, 24, 0, 8, 4, 36, 36, 216, 0, 8, 4, 36, 36, 216, 0, 8, 4, 36, 36, 216, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 3, 2, 2, 2, 3, 0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
</pre>

哈哈，这次顺利了。

修改之前用于显示的 Python 程序，加上我们刚才写的代码。
{% highlight python %}
# import ...
from ctypes import *

lcd = CDLL("./libPiLcdString.so")

def clear_buffer():
    lcd.clear_buffer()


def print_string(x, y, string_to_print, mode):
    lcd.print_string(c_char(x), c_char(y), c_char_p(string_to_print.encode('gb2312')), c_char(mode))


def get_pixel_array():
    return_array = [None] * 6
	
    for x in range(6):
        return_array[x] = [None] * 84
        for y in range(84):
            return_array[x][y] = lcd.get_pixel_status(c_char(x), c_char(y))

        return return_array;

# ...

def display_string():
    gotoxy(0, 0)
    data = get_pixel_array()
    for i in range(6):
        for j in range(84):
            lcd_data(data[i][j])

# ...

print_string(12, 12, "南北西东，", 1)
print_string(12, 24, "寒暑几重。", 1)
display_string()
{% endhighlight %}
*稍微带了点私货 :) 仙六的《刹那灯》这个 DLC 回想起来还真是挺有味道的。*

直接运行，测试。

*此处应有图片*

终于一切正常了！

之后其实就是与 DouFm 之前的版本合并起来，已经没有任何技术难度了。

ps. 在实际使用时发现，转码为 GB2312 的过程中有时会遇到不在这一字符集中的文字，这时会抛出 UnicodeEncodeError 异常。简单捕获处理即可。
{% highlight python %}
def print_string(x, y, string_to_print, mode):
    try:
        byte = string_to_print.encode('gb2312')
    except UnicodeEncodeError:
        byte = "<编码失败>".encode('gb2312')

    lcd.print_string(c_char(x), c_char(y), c_char_p(byte), c_char(mode))
{% endhighlight %}

修改 doufm_raspberry.py:
{% highlight python %}
# import ...
import lcd_display

# ...

while True:
    if music_list.__len__() == 0:
        music_list_temp = get_music_list('52f8ca1d1d41c851663fcbaf', 10)
        for music in music_list_temp:
            music_list.append(music)

    else:
        music = music_list.pop()
        lcd_display.cls()
        print(music['title'])
        lcd_display.print_string(0, 0, "Now Playing", 2)
        lcd_display.print_string(0, 12, music['title'], 1)
        lcd_display.print_string(0, 24, music['album'], 1)
        lcd_display.print_string(0, 36, music['artist'], 1)
        lcd_display.display()

        play(str(DOUFM_API_BASE_URL + music['audio']))
{% endhighlight %}

实际效果：
*此处应有图片*

代码随后上传到 github。

下一个版本就该开始做按钮事件啦，请各位期待。
