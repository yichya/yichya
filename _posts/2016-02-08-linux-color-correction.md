---
layout: post
title: Linux 下的屏幕颜色校正
---

Asus 的渣笔记本渣屏幕，简直让人心累……虽然 Asus 自带一个叫 Splendid Utility 的工具，可以对屏幕颜色进行一些优化，但是……优化过之后严重损失细节……而且，默认状态下，比起联想笔记本的屏幕，色偏严重，整个屏幕泛着幽幽的蓝光。另外，读文本时，文字的锐利度也不够。

## Flux & RedShift

Stanso 推荐我使用这两个工具。RedShift 可以看做是 Flux 的开源版。这个工具通过调整屏幕的色温来改善人眼的观感。

> 色温是可见光在摄影、录像、出版等领域具有重要应用的特征。光源的色温是通过对比它的色彩和理论的热黑体辐射体来确定的。热黑体辐射体与光源的色彩相匹配时的开尔文温度就是那个光源的色温，它直接和普朗克黑体辐射定律相联系。
> 
> --- From Wikipedia

![flux](/assets/images/linux-color-correction/flux-accion.png)

在这里有一张图，可以将色温与辐射颜色简单对应。

![blackbody](/assets/images/linux-color-correction/blackbody.png)

（来自 <http://www.techmind.org/colour/coltemp.html>）

我的屏幕看起来蓝色色光的成分比较重，也就是说屏幕颜色偏冷。将色温调整到 5000K 左右时，屏幕的观感有了明显的改善。相当长的一段时间内，我就一直使用这两个工具维持屏幕色温。

<!-- more -->

## ColorSync

装了黑苹果，瞎玩的时候发现了苹果的显示器颜色校正工具。其实 Windows 也自带一个，但是那个工具基本上等于没有。但是我利用苹果的工具很顺利的将屏幕的颜色调整到了一个颇为顺眼的状态。

之后我将黑苹果下的显示器颜色配置导出为了一个 icc 配置文件，然后导入到 Windows 中。于是，我在 Windows 下也获得了相对正常的颜色响应。

将这一配置文件应用到 Linux 却颇费了些周折。xcalib 工具可以满足我们的需求，但是它会与 nvidia 的闭源驱动产生冲突，因此只能在使用 Intel 集成显卡的时候使用 xcalib 工具。同样，RedShift 工具与 nvidia 闭源驱动的兼容性也相当差劲。*还好我平时几乎不开独立显卡。*

## How about using both tools at the same time?

校正屏幕颜色后，似乎 Flux 也就没有什么用武之地了。不过，Flux 的核心功能在于根据经度计算日出日落时间，然后按照某一算法计算出当前屏幕最适合的色温。这个功能似乎还是挺有用的，在 iOS 的最新版本中也添加了这一功能，苹果还顺便把 Flux 下架了。据说因为这个，苹果还被 Flux 的开发商告上了法庭。

在 Windows 下，Flux 可以非常愉快的与 Windows 自带的颜色管理工具结合工作，按照我们期望的方式调节色温。然而在 Linux 下，RedShift 与 xcalib 并不能愉快的协同工作，RedShift 每次调整屏幕色温时都会导致 xcalib 的屏幕颜色校正失效。

那么，我们如何解决这一问题呢？这一问题的原因又究竟是什么呢？

## Taking a closer look into xcalib

要解决上一节提到的问题，我们就应该先了解 RedShift 和 xcalib 究竟都做了些什么。两个软件都是开源的，可以很容易的找到源代码。

* **xcalib**: <https://github.com/OpenICC/xcalib/>
* **RedShift**: <https://github.com/jonls/redshift/>

我们先来看看 xcalib 是如何读取 ICC 文件并要求系统应用其中的参数吧。

打开 xcalib.c，查看 int main()，跳过所有与 Win32 和 fglrx 相关的部分。

我们首先发现了这样一个调用：
{% highlight c %}
r_ramp = (unsigned short *) malloc (ramp_size * sizeof (unsigned short));
g_ramp = (unsigned short *) malloc (ramp_size * sizeof (unsigned short));
b_ramp = (unsigned short *) malloc (ramp_size * sizeof (unsigned short));

// ...

if ((i = read_vcgt_internal(in_name, r_ramp, g_ramp, b_ramp, ramp_size)) <= 0) {
    if (i < 0) {
        warning ("Unable to read file '%s'", in_name);
    }
    if (i == 0) {
        warning ("No calibration data in ICC profile '%s' found", in_name);
    }
    
// ...
{% endhighlight %}

前面有一个将 args[] 最后一个元素复制到 in_name 中的操作，那么看来这个 read_vcgt_internal() 大概是与读取文件相关的操作了。

首先我们好奇的应该是，这个函数为什么这么命名？VCGT 是什么意思？

Google 一下得知（<http://wenku.baidu.com/view/5477b9412e3f5727a5e9624a.html>），VCGT = Video Card Gamma Tag，是苹果公司规定的一种格式，其中对 RGB 每个通道都包含了一条 Gamma 校正曲线。系统可以根据这三条曲线生成 LUT（Lookup Table），再根据 LUT 对屏幕显示的颜色进行修正。

那么这个函数应该就是从 ICC 文件中读出 VCGT 节，并且将其复制到上面定义的三个数组中的了。此处的 Ramp 代表对数学上的斜坡函数的重新定义。

查看函数定义：

{% highlight c %}
int read_vcgt_internal(const char * filename, u_int16_t * rRamp, u_int16_t * gRamp, u_int16_t * bRamp, unsigned int nEntries);
{% endhighlight %}

继续阅读代码，对 ICC 文件和文件中 VCGT 数据我们都有了一定的了解。

首先，程序跳过文件的头部 128 字节，然后读取接下来的一个表：

{% highlight c %}
bytesRead = fread(cTmp, 1, 4, fp);
numTags = BE_INT(cTmp);
for (i = 0; i < numTags; i++) {
    bytesRead = fread(cTmp, 1, 4, fp);
    tagName = BE_INT(cTmp);
    bytesRead = fread(cTmp, 1, 4, fp);
    tagOffset = BE_INT(cTmp); 
    bytesRead = fread(cTmp, 1, 4, fp);
    tagSize = BE_INT(cTmp);
   
// ...
{% endhighlight %}

这个表中包含了文件中所有小节的名称、偏移量和长度。

程序在其中搜索 mLUT 和 VCGT 两个小节，如果找到这两个小节，就读出其中的数据并传递给系统。

mLUT 中直接包含了 LUT 信息，可以直接当做 Ramp 传递给系统。

{% highlight c %}
message("mLUT found (Profile Mechanic)\n");
redRamp = (unsigned short *) malloc ((256) * sizeof (unsigned short));
greenRamp = (unsigned short *) malloc ((256) * sizeof (unsigned short));
blueRamp = (unsigned short *) malloc ((256) * sizeof (unsigned short));

for (j = 0; j < 256; j++) {
    bytesRead = fread(cTmp, 1, 2, fp);
    redRamp[j]= BE_SHORT(cTmp);
}
for (j = 0; j < 256; j++) {
    bytesRead = fread(cTmp, 1, 2, fp);
    greenRamp[j]= BE_SHORT(cTmp);
}
for (j = 0; j < 256; j++) {
    bytesRead = fread(cTmp, 1, 2, fp);
    blueRamp[j]= BE_SHORT(cTmp);
}
{% endhighlight %}

而 VCGT 则又不太一样。

VCGT 节中的第一个数据叫做 gammaType，它代表着这个 VCGT 节中数据的类型，分为两种：

* VideoCardGammaFormula，即用公式表示一条曲线
* VideoCardGammaTable，即用一系列点表示一条曲线

对于公式法，程序读出该公式需要的 9 个参数后，带入公式计算得到一条曲线：

{% highlight c %}
for (j = 0; j < nEntries; j++) {
    rRamp[j] = 65536.0 * ((double) pow ((double) j / (double) (nEntries), rGamma * (double) xcalib_state.gamma_cor) * (rMax - rMin) + rMin);
    gRamp[j] = 65536.0 * ((double) pow ((double) j / (double) (nEntries), gGamma * (double) xcalib_state.gamma_cor) * (gMax - gMin) + gMin);
    bRamp[j] = 65536.0 * ((double) pow ((double) j / (double) (nEntries), bGamma * (double) xcalib_state.gamma_cor) * (bMax - bMin) + bMin);
}
{% endhighlight %}

xcalib_state.gamma_cor 如果没有在命令行中特殊指定的话则取默认值 1.0，那么公式就是这样的：

`rRamp[j] = rMin + (rMax - rMin) * (j / 256) ^ rGamma`

为什么是指数关系呢？这个是 CRT 显示器的设计决定的，制定标准时也考虑到了这一点，感兴趣的朋友可以自行 Google 搜索。

用电子表格软件根据这个公式计算得到对应的 768 个点，绘制一下，图像大概是这个样子的：

![curve-1](/assets/images/linux-color-correction/curve-1.png)

其中三条曲线的 Min 均为 0，Max 均为 1，Gamma 从上往下依次为 0.5，1，1.5。

常识告诉我们，Gamma 越低，屏幕看起来显得越黑暗。从这个公式看来，Gamma 值的降低，使对应曲线低亮度的部分所占比重更高，也就使屏幕看起来更黑暗。

一个简单的公式似乎并不能满足对屏幕颜色进行精确校正的需求，那么就需要使用 VideoCardGammaTable 了。

对于 Table，我们要先读出通道数、点数与每一个点的大小。确定这三个值之后，程序就按顺序将后面的表格整体读出来。有时候这个表中记录的数量可能与系统要求的数量不同，程序在后面通过简单的修正获得适合系统的一条曲线。

我手中的这个 ICC 文件中的 VCGT 节就是一个 VideoCardGammaTable。我将其中的数据读出之后，用电子表格软件绘制如图：

![curve-2](/assets/images/linux-color-correction/curve-2.png)

*为什么 LibreOffice Calc 不能改线的颜色……*

三根曲线中，从右侧看最高的一根是 R 通道，中间的是 G 通道，最低的是 B 通道。我试图把三条线的颜色改为对应通道的颜色，但是没能成功。

直接使用 dispcalGUI 中自带的 Curve Viewer 打开对应的 ICC 文件，也可以看到相同的一条曲线，这说明我们的分析是正确的。

![curve-3](/assets/images/linux-color-correction/curve-3.png)

苹果的校正程序整体上调高了我的屏幕的 Gamma 值，强化了 R 通道，弱化了 G 和 B 通道，使屏幕不再明显的泛着蓝光。

读出 VCGT 并处理后我们就得到了 Ramp。再调用一下 X11 提供的一个 API，将 Ramp 发送给 X 服务器，就可以完成显示修正工作。

{% highlight c %}
XF86VidModeSetGammaRamp(dpy, screen, ramp_size, r_ramp, g_ramp, b_ramp);
{% endhighlight %}

这样 xcalib 在 Linux 平台上的整个流程我们就基本上分析完成了。xcalib 还提供了一些命令行参数用于指定每一个通道的 Gamma 修正值、亮度等，全都是简单的数学运算，我们就不再分析了。

## ... and RedShift

分析完了 xcalib，我们该来看看 RedShift 是怎样完成设置屏幕色温的了。

RedShift 比 xcalib 支持的屏幕校正方式更多，不过经过我的测试，能够使用的只有 vidmode 和 randr，drm 无法使用。RedShift 默认使用的方式是 randr，因此，我们从 gamma-randr.c 开始阅读。

很快我们就发现了最下面的一个函数：

{% highlight c %}
int randr_set_temperature(randr_state_t *state, const color_setting_t *setting);
{% endhighlight %}

从命名来看，它应该就是设置屏幕色温的函数了。这个函数又调用了另一个函数：

{% highlight c %}
static int randr_set_temperature_for_crtc(randr_state_t *state, int crtc_num, const color_setting_t *setting);
{% endhighlight %}

在这个函数中，程序先判断 crtc_num 是否有效，然后获取 crtc 对象，再然后我们看到了很熟悉的 Ramp……

{% highlight c %}
xcb_randr_crtc_t crtc = state->crtcs[crtc_num].crtc;
unsigned int ramp_size = state->crtcs[crtc_num].ramp_size;

/* Create new gamma ramps */
uint16_t *gamma_ramps = malloc(3 * ramp_size * sizeof(uint16_t));
if (gamma_ramps == NULL) {
    perror("malloc");
    return -1;
}

uint16_t *gamma_r = &gamma_ramps[0 * ramp_size];
uint16_t *gamma_g = &gamma_ramps[1 * ramp_size];
uint16_t *gamma_b = &gamma_ramps[2 * ramp_size];

if (state->preserve) {
    /* Initialize gamma ramps from saved state */
    memcpy(gamma_ramps, state->crtcs[crtc_num].saved_ramps, 3 * ramp_size * sizeof(uint16_t));
}
else {
    /* Initialize gamma ramps to pure state */
    for (int i = 0; i < ramp_size; i++) {
        uint16_t value = (double)i / ramp_size * (UINT16_MAX + 1);
        gamma_r[i] = value;
        gamma_g[i] = value;
        gamma_b[i] = value;
    }
}

colorramp_fill(gamma_r, gamma_g, gamma_b, ramp_size, setting);

/* Set new gamma ramps */
xcb_void_cookie_t gamma_set_cookie = xcb_randr_set_crtc_gamma_checked(state->conn, crtc, ramp_size, gamma_r, gamma_g, gamma_b);
error = xcb_request_check(state->conn, gamma_set_cookie);

// ...
{% endhighlight %}

程序先获得了 ramp_size，根据 ramp_size 创建数组，然后判断 state->preserve 并决定是使用已有的 Ramp 还是创建新的 Ramp。*在实际使用中，这里似乎总是创建新的 Ramp……*

然后程序调用了 `colorramp_fill()` 函数。色温值就存储在 setting 指向的一个 color_setting_t 结构体中，那么看来，colorramp_fill 函数对 Ramp 进行了某些处理。

最后程序调用 `xcb_randr_set_crtc_gamma_checked()` 函数将 Ramp 传递给系统。

另外，通过查看 gamma-vidmode.c 我们发现，vidmode 模式在这里使用了我们上面提到的 `XF86VidModeSetGammaRamp()` 函数来完成设置 Ramp 的功能。*早知道就直接看 gamma-vidmode.c 了。*

那么，我们就应该仔细的看一看 colorramp_fill 函数究竟做了些什么。它应该就是与色温设置相关运算的核心了。

打开 colorramp.c，最先看到的是一个相当大的数组。

{% highlight c %}
/* Whitepoint values for temperatures at 100K intervals.
   These will be interpolated for the actual temperature.
   This table was provided by Ingo Thies, 2013. See
   the file README-colorramp for more information. */
static const float blackbody_color[] = {
    1.00000000,  0.18172716,  0.00000000, /* 1000K */
    1.00000000,  0.25503671,  0.00000000, /* 1100K */
    1.00000000,  0.30942099,  0.00000000, /* 1200K */
    1.00000000,  0.35357379,  0.00000000, /* ...   */
    1.00000000,  0.39091524,  0.00000000,
    1.00000000,  0.42322816,  0.00000000,

// ... 
{% endhighlight %}

上面提到过：

> 光源的色温是通过对比它的色彩和理论的热黑体辐射体来确定的。

这个数组中就存储了各种色温对应黑体辐射的 gamma 值，每 100K 为一档。

下面有这样的两个函数（其实是三个不过有一个用不上）：

{% highlight c %}

static void interpolate_color(float a, const float *c1, const float *c2, float *c) {
    c[0] = (1.0 - a) * c1[0] + a * c2[0];
    c[1] = (1.0 - a) * c1[1] + a * c2[1];
    c[2] = (1.0 - a) * c1[2] + a * c2[2];
}

/* Helper macro used in the fill functions */
#define F(Y, C)  pow((Y) * setting->brightness * white_point[C], 1.0 / setting->gamma[C])

void colorramp_fill(uint16_t *gamma_r, uint16_t *gamma_g, uint16_t *gamma_b, int size, const color_setting_t *setting) {
    /* Approximate white point */
    float white_point[3];
    float alpha = (setting->temperature % 100) / 100.0;
    int temp_index = ((setting->temperature - 1000) / 100) * 3;
    interpolate_color(alpha, &blackbody_color[temp_index], &blackbody_color[temp_index + 3], white_point);

    for (int i = 0; i < size; i++) {
        gamma_r[i] = F((double)gamma_r[i] / (UINT16_MAX + 1), 0) * (UINT16_MAX + 1);
        gamma_g[i] = F((double)gamma_g[i] / (UINT16_MAX + 1), 1) * (UINT16_MAX + 1);
        gamma_b[i] = F((double)gamma_b[i] / (UINT16_MAX + 1), 2) * (UINT16_MAX + 1);
    }
}

{% endhighlight %}

函数 `interpolate_color()` 是用于处理色温值不是 100 的整数时的情况使用的。它用相邻的两个色温的 Gamma 值进行 Alpha 混合，得到一个过渡的 Gamma 值并赋值给数组 white_point。当色温值已经为整数时，Alpha 混合时对应通道的透明度就已经是 100% 了，可以看做没有进行混合运算。

下面的一个 for 循环就是主要的处理代码了。用人话说，就是这个样子的：

`gamma_r[i] = (gamma_r[i] * brightness * white_point[0]) ^ (1 / gamma)`

其中 brightness 和 gamma 我们可以从 RedShift 的用法说明中看到：

{% highlight bash %}
...

-b DAY:NIGHT   Screen brightness to apply (between 0.1 and 1.0)
-c FILE        Load settings from specified configuration file
-g R:G:B       Additional gamma correction to apply

...
{% endhighlight %}

也就是说 RedShift 提供了参数供我们进行额外的 Gamma 修正。如果不指定的话，这些数值都会取默认 1.0，那么公式可以进一步化简：

`gamma_r[i] = gamma_r[i] * white_point[0]`

也就是说，色温的处理实际上是对三条曲线乘上了一个特定的常数，以改变曲线的形态。

对于我之前读出的那条曲线，可以认为它是 6500K 色温下的曲线。我们将屏幕色温设置为 5000K，重新读一条曲线：

![curve-4](/assets/images/linux-color-correction/curve-4.png)

（对应 5000K 色温的 Gamma 值：`1.00000000,  0.90198230,  0.81465502, /* 5000K */`）

可以很直观的看到，较低的色温在原始曲线的基础上弱化了 G 和 B 通道。这也说明，降低色温确实对修正我的屏幕有一定的正面作用。

RedShift 的核心部分到这里也就分析完成了。它还有一些根据经度确定日出日落时间的功能，我们就不再分析了。

## Do it myself

回到上面提到的问题：为什么 RedShift 不能与 xcalib 协同工作呢？

在分析 RedShift 的代码时，我们看到：

{% highlight c %}
if (state->preserve) {
    /* Initialize gamma ramps from saved state */
    memcpy(gamma_ramps, state->crtcs[crtc_num].saved_ramps, 3 * ramp_size * sizeof(uint16_t));
}
else {
    /* Initialize gamma ramps to pure state */
    for (int i = 0; i < ramp_size; i++) {
        uint16_t value = (double)i / ramp_size * (UINT16_MAX + 1);
        gamma_r[i] = value;
        gamma_g[i] = value;
        gamma_b[i] = value;
    }
}
{% endhighlight %}

如果 state->preserve 的值为 True，程序就不会重新创建一个 Ramp。遗憾的是，这个条件我们无法手工指定，不得不看系统的面子。在 vidmode 模式下，也有一个同样的判断条件，同样我们也无法进行干涉。

既然我们分析清楚了 xcalib 和 RedShift 的运作机制，却又不能改变它，我们干脆自己写一个程序来完成以上的两件事情。

这个程序需要做的事情是这样的：

1. 从 ICC 文件中读取 VCGT 表，获得 Ramp。
2. 对 Ramp 应用色温相关的处理。
3. 将处理后的 Ramp 传递给系统。

程序比较简单，这里就不再赘述了。我用 C++ 重新实现了部分流程，在我的 Ubuntu 15.10 上测试通过。

## NVIDIA Graphics Card Support

Ubuntu 更新到了 16.04，NVIDIA 的闭源显卡驱动也更新了。偶然的尝试之后发现这个显卡驱动现在支持了 X11 协议中的 xcb-randr 扩展，利用 `redshift -m randr -O 5000` 可以成功调整色温。

在我们前面的代码阅读过程中，我们知道 randr 和 vidmode 两种模式是通过不同的 API 将相同的 Ramp 数据传递给显卡的 LUT。于是我们只需要简单的处理一下，就可以顺利调用 xcb-randr 提供的扩展完成针对 NVIDIA 显示核心的色温设置。

首先，编译需要我们手动安装 libxcb-randr。

{% highlight bash %}
sudo apt-get install libxcb-randr
{% endhighlight %}

修改 cmakelists.txt，增加头文件和动态链接库。

{% highlight cmake %}
cmake_minimum_required(VERSION 3.3)
project(iccLoader)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")

set(SOURCE_FILES src/main.cpp src/icc.cpp src/colorramp.cpp src/vidmode.cpp include/icc.h include/ramp.h include/colorramp.h include/vidmode.h src/randr.cpp include/randr.h)
include_directories(include)
link_directories(/usr/X11R6/lib /usr/lib/x86_64-linux-gnu/)
link_libraries(X11 Xxf86vm Xext xcb xcb-randr)
add_executable(iccLoader ${SOURCE_FILES})
{% endhighlight %}

xcb-randr 给我们提供了十分简单易懂的 API 供我们完成设置 ramp 的任务：

* **xcb_connect()** 打开一个到 X11 服务器的连接。
* **xcb_randr_set_crtc_gamma_checked()** 设置 Gamma，并返回一个 xcb_void_cookie_t 类型的数据供我们检查操作是否成功完成。
* **xcb_request_check()** 检查操作是否顺利完成。

调用很简单，直接贴代码。

{% highlight cpp %}
#include <xcb/xcb.h>
#include <xcb/randr.h>

#include "randr.h"

xcb_connection_t* randr_init_display() {
    return xcb_connect(NULL, 0);
}

xcb_generic_error_t* randr_set_new_ramp(xcb_connection_t* conn, xcb_randr_crtc_t crtc, Ramp& _ramp) {
    xcb_void_cookie_t gamma_set_cookie = xcb_randr_set_crtc_gamma_checked(conn, crtc, _ramp.numEntries, _ramp.rRamp, _ramp.gRamp, _ramp.bRamp);
    return xcb_request_check(conn, gamma_set_cookie);
}
{% endhighlight %}

实际调用的过程也比较简单。

{% highlight cpp %}
cout << "Using method randr" << endl;
xcb_connection_t* conn = randr_init_display();
randr_set_new_ramp(conn, 63, new_ramp);
{% endhighlight %}

其中 63 是 CRTC 的编号，我们可以通过修改 redshift 的代码来获得这个数据：

（redshift/src/gamma-randr.c, in randr_set_temperature_for_crtc()）

{% highlight cpp %}
    colorramp_fill(gamma_r, gamma_g, gamma_b, ramp_size, setting);

    /* Set new gamma ramps */
    fprintf(stdout, "crtc %d, ramp_size %d \n", crtc, ramp_size); // add this line to get crtc number.
    xcb_void_cookie_t gamma_set_cookie = xcb_randr_set_crtc_gamma_checked(state->conn, crtc, ramp_size, gamma_r, gamma_g, gamma_b);
    error = xcb_request_check(state->conn, gamma_set_cookie);
{% endhighlight %}

也可以通过调用 xcb-randr 提供的 APIs 来获取，我们直接看 redshift 的源代码：

（redshift/src/gamma-randr.c）

{% highlight c %}
int randr_start(randr_state_t *state)
{
    xcb_generic_error_t *error;

    int screen_num = state->screen_num;
    if (screen_num < 0) screen_num = state->preferred_screen;

    /* Get screen */
    const xcb_setup_t *setup = xcb_get_setup(state->conn);
    xcb_screen_iterator_t iter = xcb_setup_roots_iterator(setup);
    state->screen = NULL;

    for (int i = 0; iter.rem > 0; i++) {
        if (i == screen_num) {
            state->screen = iter.data;
            break;
        }
        xcb_screen_next(&iter);
    }

    if (state->screen == NULL) {
        fprintf(stderr, _("Screen %i could not be found.\n"), screen_num);
        return -1;
    }

    /* Get list of CRTCs for the screen */
    xcb_randr_get_screen_resources_current_cookie_t res_cookie = xcb_randr_get_screen_resources_current(state->conn, state->screen->root);
    xcb_randr_get_screen_resources_current_reply_t *res_reply = xcb_randr_get_screen_resources_current_reply(state->conn, res_cookie, &error);

    if (error) {
        fprintf(stderr, _("`%s' returned error %d\n"), "RANDR Get Screen Resources Current", error->error_code);
        return -1;
    }

    state->crtc_count = res_reply->num_crtcs;
    state->crtcs = calloc(state->crtc_count, sizeof(randr_crtc_state_t));
    if (state->crtcs == NULL) {
        perror("malloc");
        state->crtc_count = 0;
        return -1;
    }

    xcb_randr_crtc_t *crtcs = xcb_randr_get_screen_resources_current_crtcs(res_reply);

    /* Save CRTC identifier in state */
    for (int i = 0; i < state->crtc_count; i++) {
        state->crtcs[i].crtc = crtcs[i];
    }

    free(res_reply);
    
    // ...
{% endhighlight %}

这里通过 `xcb_get_setup()` 得到一个显示设备树，然后利用 `xcb_randr_get_screen_resources_current_reply()` 遍历得到每一个 screen的信息，再利用 `xcb_randr_get_screen_resources_current_crtcs()` 得到每一个 screen 的 crtc 信息。

当然了这些步骤其实跳过也无所谓……虽然并不建议直接跳过。

由于我们添加了一种模式，我们需要启动时能够选择使用的模式，简单的写一个 usage 信息。

{% highlight bash %}
Usage: iccLoader [-r / -v] /path/to/icc/file
Use -r for randr, -v for vidmode. Default is vidmode
{% endhighlight %}

那么现在这个 Project 应该算是比较愉悦的完成了 :)

另外，由于 GitCafe 被收购，代码迁移到 Coding.net。Clone at https://git.coding.net/yichya/IccReader.git
