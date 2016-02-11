---
layout: post
title: Linux 下的屏幕颜色校正
---

Asus 的渣笔记本渣屏幕，简直让人心累……虽然 Asus 自带一个叫 Splendid Utility 的工具，可以对屏幕颜色进行一些优化，但是……优化过之后严重损失细节……而且，默认状态下，比起联想笔记本的屏幕，色偏严重，整个屏幕泛着幽幽的蓝光。另外，读文本时，文字的锐利度也不够。

### Flux & RedShift

Stanso 推荐我使用这两个工具。RedShift 可以看做是 Flux 的开源版。这个工具通过调整屏幕的色温来改善人眼的观感。

色温是可见光在摄影、录像、出版等领域具有重要应用的特征。光源的色温是通过对比它的色彩和理论的热黑体辐射体来确定的。热黑体辐射体与光源的色彩相匹配时的开尔文温度就是那个光源的色温，它直接和普朗克黑体辐射定律相联系。

【flux 图】

在这里有一张图，可以将色温与辐射颜色简单对应。

【色温图】

（来自 <http://www.techmind.org/colour/coltemp.html>）

我的屏幕看起来蓝色色光的成分比较重，也就是说屏幕颜色偏冷。将色温调整到 5000K 左右时，屏幕的观感有了明显的改善。相当长的一段时间内，我就一直使用这两个工具维持屏幕色温。

<!-- more -->

### ColorSync

装了黑苹果，瞎玩的时候发现了苹果的显示器颜色校正工具。其实 Windows 也自带一个，但是那个工具基本上等于没有。但是我利用苹果的工具很顺利的将屏幕的颜色调整到了一个颇为顺眼的状态。

之后我将黑苹果下的显示器颜色配置导出为了一个 icc 配置文件，然后导入到 Windows 中。于是，我在 Windows 下也获得了相对正常的颜色响应。

将这一配置文件应用到 Linux 却颇费了些周折。xcalib 工具可以满足我们的需求，但是它会与 nvidia 的闭源驱动产生冲突，因此只能在使用 Intel 集成显卡的时候使用 xcalib 工具。同样，RedShift 工具与 nvidia 闭源驱动的兼容性也相当差劲。*还好我平时几乎不开独立显卡。*

### How about using both tools at the same time?

校正屏幕颜色后，似乎 Flux 也就没有什么用武之地了。不过，Flux 的核心功能在于根据经度计算日出日落时间，然后按照某一算法计算出当前屏幕最适合的色温。这个功能似乎还是挺有用的，在 iOS 的最新版本中也添加了这一功能，苹果还顺便把 Flux 下架了。据说因为这个，苹果还被 Flux 的开发商告上了法庭。

在 Windows 下，Flux 可以非常愉快的与 Windows 自带的颜色管理工具结合工作，按照我们期望的方式调节色温。然而在 Linux 下，RedShift 与 xcalib 并不能愉快的协同工作，RedShift 每次调整屏幕色温时都会导致 xcalib 的屏幕颜色校正失效。

那么，我们如何解决这一问题呢？这一问题的原因又究竟是什么呢？

### Taking a closer look into xcalib

要解决上一节提到的问题，我们就应该先了解 RedShift 和 xcalib 究竟都做了些什么。两个软件都是开源的，可以很容易的找到源代码。

* **xcalib**: <https://github.com/OpenICC/xcalib/>
* **RedShift**: <https://github.com/jonls/redshift/>

我们先来看看 xcalib 是如何读取 ICC 文件并要求系统应用其中的参数吧。

打开 xcalib.c，查看 int main()，跳过所有与 Win32 和 fglrx 相关的部分。

我们首先发现了这样一个调用：
{% highlight c %}

// ...

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
// ...

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
