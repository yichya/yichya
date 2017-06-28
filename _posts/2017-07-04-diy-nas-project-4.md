---
layout: post
title:  DIY NAS Project (4) Virtualization Practice
---

这篇想谈一谈最近自己在虚拟化上面的一些实践。由于涉及到几种不同的 Hypervisor 的关系，内容量可能会比较多，目前还没有完全想好该如何组织。

主要内容大概会包括：

* 需要解决的问题
    * 集成显卡
    * 11ac 无线网卡
    * 存储部分
    * 直通对于这些设备的意义
* 常见的几种 Hypervisor
    * Vmware ESXi
    * Hyper-V
    * KVM
* 虚拟化相关技术简介
    * 虚拟化的分类
        * Type I 与 Type II
        * Full Virtualization 与 Paravirtualization
        * 上面三种 Hypervisor 如何分类？
    * MMIO 与 IOMMU
    * VT-d，VT-x
    * SR-IOV
        * Hyper-V 中 SR-IOV 发挥的作用
* 针对上述三种 Hypervisor 的实践
    * OpenWRT 的定制
        * Hyper-V 驱动的迷之 Bug？
    * PCI 直通如何实现？
    * 主机与虚拟机的网络配置
    * 存储部分的设计

日期什么的基本上主要是给自己留个 Flag 吧，意思是说在这一天之前肯定写完。
