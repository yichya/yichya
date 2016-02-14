---
layout: post
title: 定制 OpenWrt 固件 (1) 透明代理
---

一年一度虐狗节 :)

折腾 OpenWrt 也有些日子了，不过还从来没尝试过自己定制 Rom。今天心血来潮，想把手里目前闲置的一个路由拿去做个中继 + 透明代理。

顺便预告一下：下一次介绍集成 ADBYBY 和 KMS 服务器，当然下一次我会换新买的 7620n SoC 的路由器来演示；之后我会以集成石像鬼 QoS 为例介绍一下 OpenWrt 的 BuildRoot。

### Repeater

现在市面上能买到的很多路由器都支持中继模式，我手里这台 HG556a ver.C 在更新到 OpenWrt Chaos Calmer 正式版之后居然也支持了。实测中继模式运行完美，美滴很。

本来我还不得不插上一个 Atheros 的无线网卡进行中继呢，现在倒是省事了。

### Transparent Proxy

所谓透明代理，就是说，用户完全感受不到代理的存在，但是又能享受代理提供的网络服务。

实际使用时，用户不需要设置代理或者 VPN，就能够达到翻墙等目的。

<!-- more -->

### OpenWrt ImageBuilder

这次我们的定制选择使用 OpenWrt ImageBuilder 进行。因为 Build 的是 Chaos Calmer 正式版映像，没有必要从源代码开始编译。如果是 Trunk 的话，由于内核版本迭代非常快，建议从源代码开始编译。

首先下载 Chaos Calmer 的 ImageBuilder。官方源很不稳定而且速度慢，推荐中科大的镜像源：http://mirrors.ustc.edu.cn/openwrt/

下载时只需确定自己的设备类型就可以，比如我们这次使用的 HG556a ver.C 属于 brcm63xx。

还有一点，brcm63xx 以及很多其他的 BSP 都有 generic 和 smp 两种固件。这是因为 BroadCom 有几个 CPU 为双核心，但是其架构比较特别，比如我们使用的 HG556a 的 BCM6358，两个核心共享同一个 TLB，因此 OpenWrt 官方并不支持在 BCM6358 SoC 上使用双核心。而 BCM6362 和 BCM6368 每个核心拥有独立的 TLB，在这些 SoC 上使用 smp 固件就可以完全释放双核心的潜能。

这里还有一点要说明，BCM6358 的两个核心并不完全相同，Core 0 的 Instruction Cache 比 Core 1 的大一倍，然而 OpenWrt 默认只使用 Core 1。我们可以通过修改 CFE 中部分代码，使系统使用 Core 0。据说可以获得 15-20% 的性能提升。

我们在这里选 generic 和 smp 没有太大区别，干脆也选 smp 吧。那么下载得到的文件就是 OpenWrt-ImageBuilder-15.05-brcm63xx-smp.Linux-x86_64.tar。

解压之后我们可以看到下面这些东西：

{% highlight bash %}
$ ll
总用量 1068
drwxr-xr-x 11 yichya yichya   4096  2月 14 01:38 ./
drwxrwxr-x  4 yichya yichya   4096  2月 13 16:14 ../
drwxrwxr-x  3 yichya yichya   4096  2月 13 15:17 bin/
drwxr-xr-x  3 yichya yichya   4096  9月  4 21:37 build_dir/
-rw-r--r--  1 yichya yichya  98530  9月  4 21:37 .config
drwxrwxr-x  2 yichya yichya  12288  2月 13 23:04 dl/
drwxr-xr-x  3 yichya yichya   4096  9月  4 21:38 include/
-rw-r--r--  1 yichya yichya   5239  7月 24  2015 Makefile
-rw-r--r--  1 yichya yichya 686463  9月  4 21:13 .packageinfo
drwxr-xr-x  3 yichya yichya   4096  2月 13 15:17 packages/
-rw-r--r--  1 yichya yichya   1211  2月 13 16:57 repositories.conf
-rw-r--r--  1 yichya yichya  10680  7月 24  2015 rules.mk
drwxr-xr-x  4 yichya yichya   4096  7月 24  2015 scripts/
drwxr-xr-x  3 yichya yichya   4096  9月  4 21:37 staging_dir/
drwxr-xr-x  3 yichya yichya   4096  9月  4 21:37 target/
-rw-r--r--  1 yichya yichya 223540  9月  4 21:13 .targetinfo
drwxrwxr-x  2 yichya yichya   4096  2月 13 15:15 tmp/
{% endhighlight %}

首先我们需要做的事情是，配置 repositories.conf，将 OpenWrt.org 官方源换为 ustc.edu.cn 提供的镜像源。

{% highlight bash %}
## Place your custom repositories here, they must match the architecture and version.
# src/gz chaos_calmer http://downloads.openwrt.org/chaos_calmer/15.05/brcm63xx/smp/packages
# src custom file:///usr/src/openwrt/bin/brcm63xx/packages

## Remote package repositories
src/gz chaos_calmer_base http://mirrors.ustc.edu.cn/openwrt/chaos_calmer/15.05/brcm63xx/smp/packages/base
src/gz chaos_calmer_luci http://mirrors.ustc.edu.cn/openwrt/chaos_calmer/15.05/brcm63xx/smp/packages/luci
src/gz chaos_calmer_packages http://mirrors.ustc.edu.cn/openwrt/chaos_calmer/15.05/brcm63xx/smp/packages/packages
src/gz chaos_calmer_routing http://mirrors.ustc.edu.cn/openwrt/chaos_calmer/15.05/brcm63xx/smp/packages/routing
src/gz chaos_calmer_telephony http://mirrors.ustc.edu.cn/openwrt/chaos_calmer/15.05/brcm63xx/smp/packages/telephony
src/gz chaos_calmer_management http://mirrors.ustc.edu.cn/openwrt/chaos_calmer/15.05/brcm63xx/smp/packages/management

## This is the local package repository, do not remove!
src imagebuilder file:packages
{% endhighlight %}

这样，后面生成映像的速度会有很大提升。

输入 make 命令查看帮助：

{% highlight bash %}
$ make
Available Commands:
	help:	This help text
	info:	Show a list of available target profiles
	clean:	Remove images and temporary build files
	image:	Build an image (see below for more information).

Building images:
	By default 'make image' will create an image with the default
	target profile and package set. You can use the following parameters
	to change that:

	make image PROFILE="<profilename>" # override the default target profile
	make image PACKAGES="<pkg1> [<pkg2> [<pkg3> ...]]" # include extra packages
	make image FILES="<path>" # include extra files from <path>
	make image BIN_DIR="<path>" # alternative output directory for the images
    
{% endhighlight %}

那么我们先看一下这个包中包含的所有 target profile 吧。

{% highlight bash %}
$ make info
Current Target: "brcm63xx (smp)"
Default Packages: base-files libc libgcc busybox dropbear mtd uci opkg netifd fstools swconfig kmod-gpio-button-hotplug dnsmasq iptables ip6tables ppp ppp-mod-pppoe kmod-nf-nathelper firewall odhcpd odhcp6c
Available Profiles:

Default:
	Default Profile
	Packages: kmod-b43 wpad-mini
963281TAN:
	Generic 963281TAN
	Packages: 
96328avng:
	Generic 96328avng
	Packages: 

# ...

HG556a_AB:
	Huawei EchoLife HG556a (version A/B - Atheros)
	Packages: kmod-ath9k wpad-mini kmod-usb2 kmod-usb-ohci kmod-ledtrig-usbdev
HG556a_C:
	Huawei EchoLife HG556a (version C - Ralink)
	Packages: kmod-rt2800-pci wpad-mini kmod-usb2 kmod-usb-ohci kmod-ledtrig-usbdev 
HG655b:
	Huawei HG655b
	Packages: kmod-rt2800-pci wpad-mini kmod-usb2 kmod-usb-ohci kmod-ledtrig-usbdev

# ...
{% endhighlight %}

我们看到 HG556a ver.C 对应的 profile 是 HG556a_C。那么我们直接试着 make image 一下吧。