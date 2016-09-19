---
layout: post
title: DIY NAS Project (1)
---

先扯点儿题外的。

过了软考，期末成功低空飘过，然后去武汉玩了一圈。回家开始搬砖，整个八月填三个坑差点累死，直到开学到了学校终于可以休息了。

累死啥的当然也是有回报的，比如，目前基本进入不缺钱的状态……

不缺钱的一个直接表现就是买一些……奇奇怪怪的东西，比如草民这次要说的 NAS。

# Intro

大概一年前就有过用 HP 瘦客户机代替路由器的想法，原因很简单：x86 架构的 CPU 可以跑普通 linux 发行版，能做的事情比起 MIPS 架构的路由器要多得多。后来也试过用树莓派做路由器，不过也就是刷了 OpenWRT 进去临时充当路由器用而已。顺带一提现在树莓派跟 WR703N 一样都被我扔在包里吃灰了……

后面嘛就一直在用极 1s，x86 软路由之类的事情就扔一边去了。

暑假里面突然在数码之家看到了这么一个小主板。

![](../assets/images/diy-nas-project-1/sv3-26026.jpg)

基本上看到双网卡和 SATA 接口的时候我就有些心动了。仔细了解了下这个主板之后，感觉大概有些意思，于是果断下单。

这块板子概况是这样的：

* Atom N2600
* 2GB DDR3 内存
* 一个 SATA 接口
* 两个 RTL8111 千兆网卡
* 声卡也有，不过 3.5mm 接口得自己接线出来
* 两个 Mini PCI-E 插槽，正面那个支持 3G（带 USB 定义），反面支持 MSATA
* 两个 USB，主板插针还能引出四个
* VGA，LVDS
* 七个 COM 口，一个 LPT 口（果然工控机主板）
* 12V 供电，板载硬盘供电接口

初步计划是在这块板子上装无线网卡当路由器，还有把扔家里吃灰好几年那个 80GB 的老硬盘拿来发挥下余热。两者结合做成一个带路由功能的 NAS。

# Buying Stuff

于是开始凑东西。

* 无线网卡和馈线得买。天线嘛，手里有几根 6dB 的应该是不用再买了。
* 宿舍晚上断电，原来那个 12v 的后备电源容量估计不够，得买个大的。
* 硬盘嘛，买个盘架固定好，顺便也有个地方装主板。另外抽换硬盘也方便一些。

无线网卡不同型号来回挑了好久……看到很多帖子说买了 BroadCom 的无线网卡然后不能用。报告能用的两个好像都是 Realtek RTL8188CUS……这个我没猜错的话应该是用了 USB 定义的吧……

之后我就比较担心这个主板的 Mini PCIE 插槽是不是跟之前搞了一个路由器上的一样只有 USB 定义。很忐忑的选了 Atheros 的一款普通的 PCIE 网卡，当然结果是它完全可以正常工作。

![](../assets/images/diy-nas-project-1/stuff-1.png)

挑无线网卡的时候还看到一家卖 mSATA SSD 超低价促销，价格挺不错，然后还看到有人说某个硬盘的盒子装主板正好装得下……

![](../assets/images/diy-nas-project-1/stuff-2.png)

硬盘还是不错的【可惜现在硬盘已经卖光了】，还送了两颗固定用的螺丝，免得我到处找或者买了。不过后来那个盒子并没用上【心疼三分钟】。

# Let's do this

东西都已经下了单，那什么到了就装什么咯。来吧。

主板到手是这个样子。真的很小，要不是之前买过 8 寸的 Windows 8.1 平板，见过更小的主板的话我估计还真的会吃一惊。

![](../assets/images/diy-nas-project-1/board.webp)

通电看了看，一切正常。

![](../assets/images/diy-nas-project-1/power.webp)

接上硬盘之后。

![](../assets/images/diy-nas-project-1/with-hdd.webp)

![](../assets/images/diy-nas-project-1/boot-hdd.webp)

随手装了个 XP 上去，先看看咋样。

![](../assets/images/diy-nas-project-1/aida64.webp)

跑一波 PT，很愉悦。

![](../assets/images/diy-nas-project-1/utorrent.png)

当时还没决定买盘架。简单想了一下固定方案。某个箱子里面堆了一大堆没人要的星火杯作品，干脆拎出来几个拆零件。最后从一个小车上拆了底盘和一些固定用的亚克力零件、铜柱之类，把主板和硬盘粗暴的固定到了一起。

![](../assets/images/diy-nas-project-1/first-c1.webp)

![](../assets/images/diy-nas-project-1/first-c2.webp)

整理一下线路，看起来还是挺像那么回事的。

![](../assets/images/diy-nas-project-1/first-dorm.webp)

在宿舍里面没显示器，自然就用 RDP 了。

![](../assets/images/diy-nas-project-1/rdp.webp)

后来盘架到了。用类似的方式固定一下，感觉瞬间高大上了很多。

![](../assets/images/diy-nas-project-1/second-c1.webp)

![](../assets/images/diy-nas-project-1/second-c2.webp)

之后是无线网卡。

![](../assets/images/diy-nas-project-1/ar9380.webp)

接好线，初步定型，只差天线了。

![](../assets/images/diy-nas-project-1/final-c1.webp)

XP 还是不太方便，比如承载网络、DLNA 之类的都不太好弄。换 WES7。顺便跑个分【抠鼻】。这 CPU 基本上就是要啥自行车了，不过 SSD 加持下主硬盘分数高到爆表。后面新电源也顺便出了个场。

![](../assets/images/diy-nas-project-1/final-score.webp)

天线到手，硬件齐活。这么着看还是足够有逼格的。

![](../assets/images/diy-nas-project-1/final-antenna.webp)

后面硬件基本没有改动，只有些换铜柱、重新理线之类的小事情。之后会补上一张完全体的图片。

# Select Operating System to start

软件方面感觉比硬件麻烦得多……遇到了各种各样的问题。

当时买 SSD 主要是为了把 OS 装在 SSD 上，并且设置电源管理，减少机械硬盘工作时间。毕竟 3.5 寸机械硬盘工作时耗电量还是十分可观的，而 SSD 的耗电量就小得多了。所以系统装在 SSD 上可以极大减少整个系统的平均耗电量，延长电池模式下的工作时间。

折腾的过程中试用过很多不同的 OS，包括 Windows、Linux、FreeBSD，开源的不开源的都有。最终还是自己编译了 OpenWRT，自己 Debootstrap 了 Ubuntu 14.04 LTS，目前一切愉快。

## Windows Embedded Standard 7

首先选定的是 WES7。除了承载和路由的问题之外，这个基本上是最愉悦的系统。电源模式有些小问题，正确配置之前无线会莫名其妙的罢工，关机还会蓝屏……不过配置完就很愉悦了。

图上是已经开了承载正常使用时的样子。用起来感觉还不错，包括信号啊稳定性之类的都还可以，不过没了透明代理还是不太开心。

![](../assets/images/diy-nas-project-1/net-center.png)

不过据另一位持有同款设备的强者反映，他的魅族手机无法连接承载网络，原因未知。

## Windows Server 2008 R2

因为 Win7 不能同时在两个接口上开网络共享，承载网络又不能桥接，以及一堆各种各样的麻烦比如 Ubuntu Server 死活装不上去之类的……我决定换 Windows 2008 R2。

配了半天路由表、DHCP 之类的，才勉强能用……

![](../assets/images/diy-nas-project-1/server-manager.png)

平时用也并不愉快。

* 跟 WES7 同样不能桥接，还好可以路由，不过总是不如桥接来的方便。
* Routing and Remote Access 服务在开机后很久才能启动，中间会有将近十分钟不能上网。
* 经常莫名其妙的连不上 PPPoE。

总之还是卸了。

## RouterOS

久仰大名的 RouterOS。

起初装的是官方 6.36。不付钱就只有 24 小时试用。然而授权方式是绑定硬盘……这我就不太敢买了……200 块钱一不小心就打了水漂啥的我可受不了。

然后费了大力气找到了破解版的 5.24 ISO。安装的时候有点小麻烦，得关掉 AHCI。装完可以再打开。

初见果然高大上，然而配置比 Server 2008 R2 还麻烦……

> 被 RouterOS 折磨到绝望的某个晚上。
>
> 拿到 RouterOS 设备，想配置好路由需要以下几步：
>
> 恢复默认设置→在终端里为有线网卡 A 指定静态 IP→在有线网卡 A 上配置 DHCP→有线网卡连上电脑，打开 WinBox→把无线网卡改成 AP 模式、2.4 GHz BGN→设置好 SSID 和密码→新建网络桥，将有线网卡 A 和无线网卡桥接→在新的网络桥上配置 DHCP 并禁用原来有线网卡上的 DHCP→重新打开 WinBox，新建 PPPoE 连接→把网线插到有线网卡 B 上，拨号→在路由表里添加到 PPPoE 网关的路由→在防火墙里面配置 NAT 表→嗯，可以上网了 :)
>
> 想想现在随便买个路由器，上面这么多步骤点几下鼠标就能完成，感觉真的很奇妙呢。

![](../assets/images/diy-nas-project-1/routeros-real.png)

RouterOS 的无线性能非常之好。单天线 150MBPS 毫无压力，自带 SMB 共享在信道比较干净（G302 测试）的情况下能达到近 10MB/s 的速度，比较拥挤（宿舍，挑了半天选了最干净的信道 8）大概有 5-6MB/s。 不过比较奇怪的是有线性能只有 30MB/s 左右，差不多只有 Windows 下的 60%。

RouterOS 5.24 内核是 2.6.35。大概是相当有年头的一个 LTS 吧……我没记错的话 Ubuntu 10.10 用的就是这个版本。

我下的这个版本是破解过的，其中除了授权破解之外还有插件破解，也就是支持运行一些 Linux 程序。我在网上下载到了一个基本版的 Debian，成功 chroot 进去。需要注意的是 RouterOS 内核不支持 Swap，不过这个主板 2GB 内存应该也不太容易烧光吧。

原来的 Debian 版本是 squeeze。感觉实在是太老，于是改了下升级到 wheezy。装了 Transmission，下载一切正常。

本来就打算一直用下去了，不过后来发现一个非常迷的问题：重启时会无法挂载硬盘……必须拔出来，开机状态下插进去才能正常使用。这也不成啊……后来我在买正版 RouterOS 和换 OS 之间纠结了半天还是觉得换 OS 吧。

## OPNsense/pfsense

这俩只是装上了，然而无线驱动都是残疾。跳过。

# Final Solution: OpenWRT

嘛，就是当前方案啦。这个我下面会着重说一下。
 