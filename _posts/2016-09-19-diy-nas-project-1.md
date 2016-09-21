---
layout: post
title: DIY NAS Project (1)
---

先扯点儿题外的。

过了软考，期末成功低空飘过，然后去武汉玩了一圈。回家开始搬砖，整个八月填三个坑差点累死，直到开学到了学校终于可以休息了。

累死啥的当然也是有回报的，比如，目前基本进入不缺钱的状态……

不缺钱的一个直接表现就是买一些……奇奇怪怪的东西，比如草民这次要说的 NAS。

<!-- more -->

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

# First Hardware Revision

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

因为 Win7 不能同时在两个接口上开网络共享，承载网络又不能桥接，我决定换 Windows 2008 R2。

配了半天路由表、DHCP 之类的，才勉强能用……

![](../assets/images/diy-nas-project-1/server-manager.png)

平时用也并不愉快。

* 跟 WES7 同样不能桥接，还好可以路由，不过总是不如桥接来的方便。
* Routing and Remote Access 服务在开机后很久才能启动，中间会有将近十分钟不能上网。
* 经常莫名其妙的连不上 PPPoE。

总之还是卸了。

## Ubuntu Server & VMware ESXi

其实最初我是希望在上面装 Ubuntu Server，这样之后还能配置透明代理，跑些服务什么的也比较简单，可是死活装不上去。

后来看网上有人折腾用 ESXi 同时带黑群晖和 RouterOS，性能似乎还不错，我也想用 ESXi 来一波虚拟化的，可惜也是完全装不上去。

问题基本上集中在下面几个地方：

* 主板的显示输出默认是 LVDS 而且关不掉。BIOS 里面是有选项的，但是又被屏蔽了。Ubuntu 桌面版和 ESXi 都遇到了这一问题。
* USB 键盘鼠标支持不完善。Ubuntu 桌面版和 ESXi 也都遇到了这一问题。
* 网卡驱动不全。这个主要是 ESXi 遇到了问题。

至于 Ubuntu Server，问题更迷……总之我也是没解决，放弃了。

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

RouterOS 的无线性能非常之好。单天线 150MBPS 毫无压力，自带 SMB 共享在信道比较干净（G302 测试）的情况下能达到近 10MB/s 的速度，比较拥挤的情况下（宿舍，几乎每个信道都被占了，挑了半天选了最干净的信道 8）大概有 5-6MB/s。 不过比较奇怪的是有线性能只有 30MB/s 左右，差不多只有 Windows 下的 60%。

我下的这个版本是破解过的，其中除了授权破解之外还有插件破解，也就是支持运行一些 Linux 程序。我在网上下载到了一个基本版的 Debian，成功 chroot 进去。需要注意的是 RouterOS 内核不支持 Swap，不过这个主板 2GB 内存应该也不太容易烧光吧。

原来的 Debian 版本是 squeeze。感觉实在是太老，于是改了下升级到 wheezy。装了 Transmission，下载一切正常。RouterOS 5.24 内核是 2.6.35。大概是相当有年头的一个 LTS 吧……我没记错的话 Ubuntu 10.10 用的就是这个版本。不太敢再升级 Debian 了……说不定会出现兼容性问题。

本来就打算一直用下去了，不过后来发现一个非常迷的问题：重启时会无法挂载硬盘……必须拔出来，开机状态下插进去才能正常使用。这也不成啊……后来我在买正版 RouterOS 和换 OS 之间纠结了半天还是觉得换 OS 吧。

## OPNsense/pfsense

这俩只是装上了，然而无线驱动都是残疾。

其他的，网络似乎只能划分为 LAN 和 WAN 两个区域，不像 OpenWRT 可以自定义防火墙区域。并不优雅。

总之感觉没啥可说的……跳过吧。

# Final Solution: OpenWRT

嘛，就是当前方案啦。

## Official Edition

先上的是官方版。用起来基本上正常，性能啥的都还不错。

然而，官方版本有很多不是很优雅的地方，比如：

* 内核没有 ACPI 支持，导致系统功耗高的吓人
* overlay 空间太小
* 不便于集成 ShadowSocksR 进行透明代理（当然这个是 ShadowSocksR 的锅，不过总是得处理的）
* 不自带 Atheros 无线网卡驱动（虽然可以装）

除了最后一个都没啥办法，只能自己编译了。

## Add ACPI Support

参考 [https://gist.github.com/huming2207/47b17be9f27eb4b4e908801e31bfa4fe](https://gist.github.com/huming2207/47b17be9f27eb4b4e908801e31bfa4fe) 在 .config 里面添加了一些选项，打开内核的 ACPI 支持。

{% highlight makefile %}
CONFIG_ACPI=y
CONFIG_ACPI_AC=y
CONFIG_ACPI_BATTERY=y
CONFIG_ACPI_BUTTON=y
CONFIG_ACPI_FAN=y
CONFIG_ACPI_LEGACY_TABLES_LOOKUP=y
CONFIG_ACPI_PROCESSOR=y
CONFIG_ACPI_THERMAL=y
CONFIG_CPU_FREQ=y
CONFIG_CPU_FREQ_DEFAULT_GOV_ONDEMAND=y
CONFIG_CPU_FREQ_GOV_COMMON=y
CONFIG_CPU_FREQ_GOV_ONDEMAND=y
CONFIG_CPU_FREQ_GOV_PERFORMANCE=y
CONFIG_CPU_FREQ_STAT=y
CONFIG_CPU_FREQ_STAT_DETAILS=y
CONFIG_CPU_IDLE=y
CONFIG_CPU_IDLE_GOV_LADDER=y
CONFIG_CPU_SUP_AMD=y
CONFIG_CPU_SUP_CENTAUR=y
CONFIG_CPU_SUP_CYRIX_32=y
CONFIG_CPU_SUP_INTEL=y
CONFIG_CPU_SUP_TRANSMETA_32=y
CONFIG_CPU_SUP_UMC_32=y
CONFIG_HAVE_ACPI_APEI=y
CONFIG_HAVE_ACPI_APEI_NMI=y
CONFIG_THERMAL=y
CONFIG_THERMAL_DEFAULT_GOV_STEP_WISE=y
CONFIG_THERMAL_GOV_STEP_WISE=y
CONFIG_X86_ACPI_CPUFREQ=y
CONFIG_X86_ACPI_CPUFREQ_CPB=y
CONFIG_X86_THERMAL_VECTOR=y
{% endhighlight %}

选择 x86_64 配置，设定好其他的东西之后把这些粘贴到最后，编译即可。

效果还是相当明显的。之前从电源指示灯上就能看出运行功耗非常高，而且散热片十分烫手。之后运行功耗大致和 WES7 持平，散热片还要更凉一些。

## Other Components

我添加了可能会用到的一些组件，包括 Transmission、HD-Idle、OpenVPN 等。

![](../assets/images/diy-nas-project-1/openwrt-services.png)

另外调整了 overlay 的大小到 512MB。剩下的空间单独分了一个区，用于 Debootstrap。

# Second Hardware Revision

80GB 的硬盘还是明显太小了些，即使后面从贵协某台机器上换下了一块儿 160GB 的仍觉不够。然而由于供电条件的严格，又不敢随意购买大容量硬盘（Seagate 标准的 1TB 台式机硬盘要求 5v 0.75a、12v 0.75a 的供电），因此新硬盘的事情一直没着落。

偶然在狗东上搜了下硬盘，发现了一种很特别的转速 5900RPM 的硬盘，供电要求 5v 0.6a 左右，12v 更是不到 0.4a。这简直是为我量身定做的嘛。当晚下单，第二天就到货了。

我买的是狗东上仅仅比台式机硬盘稍贵的 Surveillance HDD SV7，2TB。

拿到它之后发现傻逼了……完全忘了双碟硬盘厚度的问题……

![](../assets/images/diy-nas-project-1/new-hdd.webp)

之前的理线方案完全没考虑到这种规格的硬盘，嘛，还好前面没介绍我是怎么理线的。下面简单介绍下吧。

SATA 数据线我选择了一条联想台式机自带的，长短非常合适，而且恰好只有一边接口有金属卡子，完全满足我的需求。

![](../assets/images/diy-nas-project-1/hdd-sata.webp)

硬盘的电源线就要麻烦不少。

先从这里穿过。

![](../assets/images/diy-nas-project-1/hdd-power-1.webp)

绕一圈。这两张上也有 WiFi 天线的固定方案，如果觉得不错的话可以参考。

![](../assets/images/diy-nas-project-1/hdd-power-2.webp)

在前面的那个柱子上如法炮制，不过要绕两圈。

![](../assets/images/diy-nas-project-1/hdd-power-3.webp)

伸出来的电源线接头在压住硬盘用的铁丝上再绕一圈，注意方向。

![](../assets/images/diy-nas-project-1/hdd-power-4.webp)

抽出来插好就行了。下面是效果图，全高硬盘放进去基本上比较顺畅，没有什么大问题。

![](../assets/images/diy-nas-project-1/new-hdd-2.webp)

![](../assets/images/diy-nas-project-1/new-hdd-1.webp)

# Finally

NAS 定制初步计划就完成了。相当长一段时间内应该是再也不需要担心硬盘容量不够的问题了……

目前宿舍还没有开始限电。等到限电开始的时候，我会根据情况再更新一部分信息。