---
layout: post
title: 定制 OpenWrt 固件 (2) BuildRoot
---

上一次似乎说想用 MT7620A 的路由器来演示更进一步的 ImageBuilder 用法。不过呢，我改主意了。虽然我现在手里有三个 MT7620A 的路由器吧。

至于为什么改主意……一方面是 OpenWrt 官方的 Designated Driver（16.x）版仍然没有正式发布，然而只有这个版本才添加了对极 1s 等国产智能路由器的官方支持。

所以嘛，我们跳过这一步，直接来搞 BuildRoot。

## TL-WR703N Original version

前两天翻数码之家，发现有人卖路由器，极 1s 只要 50 块钱。卖家还有一个不太正常的 WR703N，据说搜不到无线而且有线插上不是 192.168.1.0/24，20 块钱出。因为早就想要一个 WR703N，于是就果断打包入手了。

到手之后极 1s 没怎么折腾就拿去用了（话说居然还有 900 多天才过保，不亏）。既然没过保就不瞎折腾了，插到网内让它安静的提供一下 OpenVPN 服务就行。

这台 WR703N 真的好小，比银行卡的一半稍大一点。直接挂在钥匙上都不是很违和。

![](../assets/images/openwrt-customize-2/wr703n.jpg)

稍微玩了一小会儿。跟卖家说的一样棘手，插上电源之后，看指示灯闪烁的状态，似乎正常启动到了 OpenWrt。然而捅了半天菊花试图恢复出厂设置，无效。这就很尴尬了。进 U-Boot 也分配不到 IP。

上网查过，发现 TP 原装的 U-Boot 并没有自动设置 IP 之类。意思是说，固件挂了，如果没有办法接 TTL 的话，这东西就是一板砖。尼玛。

拆壳，焊 TTL。（从网上借的图，自己的焊盘狗带了一个来不及重拍了。侵删）

【图 1，TTL】

焊点是真 TM 小，倒是难不倒我。有一个迷的问题是 GND 并没有跟各个接口的外壳相连，所以不得不去板子上找一个。

用控制台看了半天固件的默认设置，发现 WIFI 默认被禁用，以太网端口搞了一个特别诡异的配置：固定 IP 192.168.0.100 网关 192.168.0.1……于是把自己电脑 IP 改成 192.168.0.1，顺利访问到路由器的 LuCI 界面。

然后就是刷掉固件解锁 U-Boot，刷 Breed，备份 ART，为后面作死做好准备。 

* 解锁了 U-Boot 分区的固件可以在[【这里】](http://pan.baidu.com/s/1dDu0Rgl)下载。
* Breed 可以在[【这里】](http://www.right.com.cn/forum/thread-161906-1-1.html)下载。如何刷入请见贴内教程，其实也就是一个 `mtd -r write /tmp/breed-ar9331.bin u-boot` 而已。
* 我的 ART 可以在[【这里】](../assets/files/openwrt-customize-2/art.bin)下载。

Breed 界面是这个样子的，可以看到这台设备并没有进行硬件改动，仍然是出厂时的 32MB RAM + 4MB Flash 搭配。

【图 2，Breed】

拆 TTL 线的时候就比较悲剧……焊点小也就算了，还特么特别容易掉。虽然我小心小心再小心不过还是手抖毁掉了一个焊盘。不过无所谓了。

搞定之后，我刷的是 lean 定制的自带 ShadowSocksR 和 AdBlock Plus 并优化了 Dnsmasq 的固件，可以在[【这里】](http://www.right.com.cn/forum/thread-186814-1-3.html)下载。

## Challenge

lean 的固件用起来还不错，可以十分愉悦的完成透明代理任务，不过 AdBlock 我反正是没看见……

路由器上有一个 USB 接口，lean 的固件并没有集成任何 USB 相关支持，却加入了一些我觉得并没有什么用的中文翻译、UPNP、动态 DNS 之类的功能。

由于这个路由器非常非常小，小到挂在钥匙上都不太违和，我计划中的使用方式大概是这样：用移动电源给树莓派供电，树莓派某一个 USB 口连接路由器供电口，路由器的 USB 口连接手机，手机打开 USB 网络共享。这样其他设备连接到路由器提供的网络就可以通过手机上网了。

本来计划使用 ImageBuilder 完成映像定制，不过……

* Flash 空间只有 4MB，裁剪的粒度可能比软件包还要小，甚至可能细化到内核的某一个功能特性（事实上也确实如此）
* ShadowSocksR 没有提供上一次搞透明代理那样的第三方软件源（虽然可以配置本地源，所以这其实不算是个什么靠谱的理由）
* 既然有这么个作死的机会，不如……

我们来试试 BuildRoot 吧。

## BuildRoot - Preparation

首先，根据官方的 BuildRoot 教程，我们需要准备以下环境。

* Linux 或者 Mac OS X。重点是 Case-Sensetive Filesystem……所以 Cygwin 不行。
* ToolChains。第一次执行 make 时会检查工具链，如下。
* 靠谱的网络。最好挂好了 VPN 或者配置好了 ShadowSocks 透明代理，或者使用前面提到过的 ProxyChains。

{% highlight bash %}
Checking 'working-make'... ok.
Checking 'case-sensitive-fs'... ok.
Checking 'gcc'... ok.
Checking 'working-gcc'... ok.
Checking 'g++'... ok.
Checking 'working-g++'... ok.
Checking 'ncurses'... ok.
Checking 'zlib'... ok.
Checking 'libssl'... ok.
Checking 'perl-thread-queue'... ok.
Checking 'tar'... ok.
Checking 'find'... ok.
Checking 'bash'... ok.
Checking 'patch'... ok.
Checking 'diff'... ok.
Checking 'cp'... ok.
Checking 'seq'... ok.
Checking 'awk'... ok.
Checking 'grep'... ok.
Checking 'getopt'... ok.
Checking 'stat'... ok.
Checking 'md5sum'... ok.
Checking 'unzip'... ok.
Checking 'bzip2'... ok.
Checking 'wget'... ok.
Checking 'perl'... ok.
Checking 'python'... ok.
Checking 'svn'... ok.
Checking 'git'... ok.
Checking 'file'... ok.
Checking 'openssl'... ok.
Checking 'ldconfig-stub'... ok.
{% endhighlight %}

全都准备好之后，我们就可以开始了。

首先，从 OpenWrt 官方获取源代码。我们这次的定制使用 2016/05/27 的 Trunk 版本。

{% highlight bash %}
git clone git://git.openwrt.org/openwrt.git trunk
{% endhighlight %}

如果需要稳定版，可以加上对应的版本号：

{% highlight bash %}
git clone git://git.openwrt.org/15.05/openwrt.git chaos_calmer
{% endhighlight %}

需要注意的是目前 Chaos Calmer 分支下的稳定版是 15.05.1。

等待一会儿 git clone 完成，cd 进入 trunk 目录。

输入命令

{% highlight bash %}
make menuconfig
{% endhighlight %}

之后，我们就看到了配置菜单。

![](../assets/images/openwrt-customize-2/menu-before-feeds-update.png)

我们发现，这个菜单中包含的项目并不全，甚至连最重要的 LuCI 都没有。在开始前，我们还需要更新 Feeds。

{% highlight bash %}
./scripts/feeds update -a
./scripts/feeds install -a
{% endhighlight %}

更新 Feeds 之后再查看菜单，LuCI 等项目就出现了。

![](../assets/images/openwrt-customize-2/menu-after-feeds-update.png)

我们此时可以测试一下工具链是否正常，方法当然是 Fire。

目前 Target System 已经是我们要的 Atheros AR7xxx/AR9xxx。修改下面的 Target Profile 为 WR703N：

![](../assets/images/openwrt-customize-2/menu-target-profile.png)

返回，保存。

![](../assets/images/openwrt-customize-2/menu-save-config.png)

退出，开始编译：

{% highlight bash %}
make V=99 -j
{% endhighlight %}

其中 V=99 代表显示所有信息。-j 代表允许并行任务（后面可以加一个数字代表线程数，不加代表不限制）

![](../assets/images/openwrt-customize-2/first-make.png)

一次完整的编译，从整个 gcc g++ 到内核再到各种软件包都会从源代码编译出来……简直可怕……

根据网络状况、电脑配置说好的，短的大概 20 分钟，长的可能会有几个小时，我们可以开始等了。这个过程中需要保持网络畅通，同时 CPU 也会狂烧……


