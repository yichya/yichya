---
layout: post
title: Card Pick Simulater Based on Nameko & RabbitMQ
categories:
  - Large Things
tags:
  - gevent
  - python
  - libev
  - nameko
  - microservice
---

寒假里面，过年前一天抽到了花鸟卷，几天之后又抽到了青行灯，加上去年最后一天抽到的酒吞，勉强算是脱非了吧 23333

网易爸爸的抽卡机制真的是让人完全捉摸不透，不过一个很常见的玄学是【卡池说】，也就是说，十二点过后的几分钟里世界疯狂的开始刷【神眷】的时候抽到 SSR 的概率会高很多。草民的三只 SSR 也确实都是在十二点过后不久抽到的，或许这个传说确实是存在。

寒假里面看了些微服务相关的东西，但是一直没有动手实践。恰逢 Umefit 因为业务发展需求将进行重构，新来的 CTO 建议我们采用微服务架构，融合先进的 DevOps 理念进行下一个版本的迭代。

于是就有了这个抽卡模拟器。

# Overview

[链接在此](http://bc.yichyaqc.cn:8000/client/index.html)

[这里](http://bc.yichyaqc.cn:8001/client/index.html)是一个功能完全一样的版本，只不过是一个单独的 Flask App，用来进行性能对比。

[这里](https://coding.net/u/yichya/p/nameko-cardpick/git)是项目的仓库首页。

<!-- more -->

# Nameko

[https://github.com/nameko/nameko](https://github.com/nameko/nameko)

这个框架是 Python 世界中一个挺典型的适合 SOA 开发的框架，目前看还是挺火的。支持服务发现和负载均衡，看起来是一个很适合初学者玩耍的框架。

我们这次搭 Demo，就主要用它来做了。

# RabbitMQ

Nameko 官方示例中使用的消息队列是 RabbitMQ，所以我们这次也用的是它。

## Install

安装 RabbitMQ 最简单的方式是直接用 Docker。建议使用带管理界面的版本，可以在管理界面中查看消息队列的一系列监控信息。

{% highlight bash %}
$ docker pull rabbitmq:3-management
{% endhighlight %}

安装好之后启动：

{% highlight bash %}
$ docker run -d --name rabbitmq rabbitmq:3-management
{% endhighlight %}

查看容器 IP：

{% highlight bash %}
$ docker inspect --format '\{\{ .NetworkSettings.IPAddress }}' rabbitmq
172.17.0.2
{% endhighlight %}

此时打开 172.17.0.2:15672 即可看到 RabbitMQ 的登录界面，用 guest／guest 即可登录。

# Configure RabbitMQ for later use

创建一个用户给 Nameko，并简单的分配绝对足够的权限：

{% highlight bash %}
$ docker exec -it rabbitmq bash
root@29deed168df9:/# rabbitmqctl add_user nameko nameko
Creating user "nameko" ...
root@29deed168df9:/# rabbitmqctl set_user_tags nameko administrator
Setting tags for user "nameko" to [administrator] ...
root@29deed168df9:/# rabbitmqctl set_permissions nameko ".*" ".*" ".*"
Setting permissions for user "nameko" in vhost "/" ...
root@29deed168df9:/# 
{% endhighlight %}

这样 RabbitMQ 就准备好了。

RabbitMQ 还可以实现权限控制、Cluster 等高级功能，这些我们将在下次进行服务的扩容时尝试。

# Basic Design

用户在游戏中实际的抽卡效果是，拿出一张票，在上面画一个符或者发一段语音，然后就可以看到抽卡结果。如果得到了 SR 或者 SSR 卡的话，还会有一个公告板显示用户抽到了什么什么式神真是羡煞旁人啊【雾

当然有人通过拆包发现，其实客户端画的什么符，在实际的抽卡 RPC 中并没有发到服务器，那我就省下这个步骤好了【我才不会说是我不会做呢。

至于这个公告板，我也没多想，轮询太 low 了，用 WebSockets 做应该比较合适。

Nameko 的介绍中称其支持 WebSockets，不过还是 Experimental。文档中也没有关于 WebSockets 的介绍。考虑之后决定用单独的 Flask App 来提供 WebSockets，顺便负责提供 Web 页面给用户。

数据库方面使用 MongoDB。至于原因，看看游戏客户端日志，被 ObjectId 糊一脸的时候你就懂了。

最后架构图如下：

```
  +----------+       +--------------+       +---------------+       +----------------+       +-------------+
  | Database | <---> | Card Service | <---> | Message Queue | <---> | Client Service | <---> | Web Service |
  +----------+       +--------------+       +---------------+       +----------------+       +-------------+
```

其实这里的 Client Service 跟实际上的游戏客户端处于同样的位置上，也就是说：

```
                                                                    +----------------+       +-------------+
                                                                ·-> | Client Service | <---> | Web Service |
                                                                |   +----------------+       +-------------+
                                                                |   +----------------+       +-------------+
                                                                ·-> | Client Service | <---> | Web Service |
                                                                |   +----------------+       +-------------+
  +----------+       +--------------+       +---------------+   |   +----------------+       +-------------+
  | Database | <---> | Card Service | <---> | Message Queue | <-·-> | Client Service | <---> | Web Service |
  +----------+       +--------------+       +---------------+   |   +----------------+       +-------------+
                                                                |   +----------------+       +-------------+
                                                                ·-> | Client Service | <---> | Web Service |
                                                                |   +----------------+       +-------------+
                                                                |   +----------------+       +-------------+
                                                                ·-> | Client Service | <---> | Web Service |
                                                                    +----------------+       +-------------+

```

在系统需要扩容的时候，压力一般会在数据库和游戏服务器上。游戏服务器可以考虑根据功能进行拆分，数据库可以简单的使用 mongos 进行分库，或者在游戏服务器拆分的基础上进行分库。而 RabbitMQ 消息队列也是可以使用 Clustering 功能进行横向扩展的。另外，利用 RabbitMQ 的路由功能可以很方便的实现请求的分发。

```
  +----------+       +--------------+       +---------------+       +----------------+       +-------------+
  | Database | <---> | Card Service | <---> |               | <---> | Client Service | <---> | Web Service |
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  | Database | <---> | User Service | <---> |               | <---> | Client Service | <---> | Web Service |
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  | Database | <---> | Batl Service | <---> | Message Queue | <---> | Client Service | <---> | Web Service |
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  | Database | <---> | Expl Service | <---> |               | <---> | Client Service | <---> | Web Service |
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  +----------+       +--------------+       |               |       +----------------+       +-------------+
  | Database | <---> | Shop Service | <---> |               | <---> | Client Service | <---> | Web Service |
  +----------+       +--------------+       +---------------+       +----------------+       +-------------+

```

实际的扩容，我们留到下次再谈。

# Card Service Implemention

最简单的基于卡池的抽卡器需要满足以下两个功能：

* 抽卡（用户提交请求，系统从卡池中选择一张卡返回给用户，并将这张卡从卡池中删除；抽到高稀有度的卡时，通知所有用户）
* 更新卡池

Nameko 提供了 RPC、发布者-订阅者（Pub-Sub）两种服务处理模式，还非常贴心的提供了一个定时器（Timer）模式，恰好可以满足我们的所有功能：

* 关于抽卡，很明显，我们可以跟游戏中实际的一样做成 RPC。
* 关于高稀有度广播，发布订阅模式非常合适。
* 更新卡池，可以使用定时服务，也可以使用发布者订阅者模式，在抽卡 RPC 过程中检测到卡池余量较低时发布广播通知服务更新卡池。

我们这里为了简单起见，使用定时更新卡池的方式。

{% highlight python %}
class CardService(object):
    name = "card_service"
    dispatch = EventDispatcher()

    @rpc
    def pick_card(self, user, nonce):
        # several processes about nonce...

        # pick a card with given nonce
        card = pick_one(nonce)

        # serialize card data...
        
        # publish big news if the card is quite rare
        if card.cclass in [SR, SSR]:
            self.dispatch("pick_card", json.dumps(data))
        
        return card

    @timer(interval=1152)
    def auto_pool_refresh(self):
        # Refresh Card Pool
        refresh_card_pool()

{% endhighlight %}

同时，为了方便调试与管理，我们也可以添加一个手动更新卡池的 RPC Endpoint：

{% highlight python %}
    @rpc
    def manual_pool_refresh(self):
        # Refresh Card Pool
        refresh_card_pool()
{% endhighlight %}

这样我们就完成了服务端抽卡服务。

想要启动服务，我们还需要配置 Nameko。Nameko 的配置文件是 YAML 格式的，内容不多且很容易理解：

{% highlight yaml %}
AMQP_URI: 'amqp://nameko:nameko@172.17.0.2'
WEB_SERVER_ADDRESS: '0.0.0.0:10000'

max_workers: 10
parent_calls_tracked: 10
{% endhighlight %}

修改消息队列 URL 为我们刚才设定的用户名和密码以及容器的 IP 即可。

要启动服务的话，我们只需要用 nameko run 命令，将配置文件和包含上面的 CardService 类的 Python Package 作为参数：

{% highlight bash %}
$ nameko run --config nameko.yml card_service
{% endhighlight %}

# Nameko Shell

Nameko 提供给了我们一个非常好用的工具，即 Nameko Shell。通过它，我们可以直接连接到消息队列，并利用它提供的 RPC 接口和 Event Dispatcher 进行 RPC 和消息发布。

我们现在来用 Nameko Shell 测试刚才部署的服务。

启动 Nameko Shell：

{% highlight bash %}
$ nameko shell --broker amqp://nameko:nameko@172.17.0.2
Nameko Python 3.5.2 (default, Nov 17 2016, 17:05:23) 
[GCC 5.4.0 20160609] shell on linux
Broker: b'amqp://nameko:nameko@172.17.0.2'
>>> 
{% endhighlight %}

此时就可以使用 Nameko Shell 提供的 n 对象操作服务了。

随便来抽个卡看看：

{% highlight python %}
>>> n.rpc.card_service.pick_card("user", "nonce")
'{"extra": {"server_nonce": 8434319762358272268, "client_nonce": 7521845498220021516, "matched_card": 9131675239571130064}, "card": "\\u5c71\\u7ae5 (R), \\u2605\\u2605", "user": "user"}'
>>> 
{% endhighlight %}

山童……啊有点儿小非……算了不重要，代码正常运行才是坠吼的。

【山童：感受过钟灵四件套满命中，一锤晕一片让你全程罚站的恐惧和无奈嘛？】

抽卡服务的逻辑应该就没问题了，那么我们下面开始做用户端逻辑吧。

# Client Service & Web Service

Client Service 在我的想法中，其实相当于实际当中的游戏客户端，Web Service 相当于游戏的界面部分。

在我们的设计中，Client Service 应该包括以下的功能：

* 调用服务器抽卡 RPC。
* 接收来自服务器的羡煞旁人广播。

同样，Web Service 也需要满足这些功能。

Nameko 的接口除了 Nameko 自身的 RPC 之外，还支持 HTTP 请求，因此，Web Service 可以发送 HTTP 请求到 Client Service 完成整个抽卡 RPC。同样，Client Service 也可以向 Web Service 发出 HTTP 请求来传送羡煞旁人广播。

首先写 Client Service 中的抽卡 RPC。

{% highlight python %}
class ApiService(object):
    name = "api_service"

    card_proxy = RpcProxy("card_service")
    user_proxy = RpcProxy("user_service")


    @http('POST', '/pick_card')
    def pick_card(self, request):
        pick_form = CardPickForm(formdata=request.form)
        return (200, {'Content-Type': 'application/json'}, self.card_proxy.pick_card(pick_form.token.data, pick_form.nonce.data))
{% endhighlight %}

配置文件中的 WEB_SERVER_ADDRESS 此时就派上用场了。运行这个服务后，向 0.0.0.0:10000/pick_card 发送一个 Post 请求，就可以在返回值中得到抽卡结果。

然后我们在 Web Service 中对这个接口进行简单封装：

{% highlight python %}
@gateway_blueprint.route("/<string:service_name>", methods=['POST'])
def call_service(service_name):
    return jsonify(requests.post("http://localhost:10000/%s" % service_name, data=request.form).json())
{% endhighlight %}

抽卡的接口就做好了。

然后我们来完成 Client Service 中接收羡煞旁人广播的部分。这一部分将接收到的信息通过 POST 发送到 Web Service 中。

{% highlight python %}
class NewsService(object):
    name = "news_service"
    config = Config()

    def post_message(self, m):
        def post(message):
            requests.post(url="http://%s/client/broadcast" % self.config.get("SERVER_NAME"), data={'content': message})

        eventlet.greenthread.spawn(post, m)

    @event_handler(CARD_SERVICE, PICK_CARD, handler_type=BROADCAST, reliable_delivery=False)
    def card_pick(self, pl):
        payload = json.loads(pl)
        self.post_message(templates[PICK_CARD](payload['user'], payload['card']))
{% endhighlight %}

实现 Web Service 中的接口：
{% highlight python %}
@client_blueprint.route("/broadcast", methods=['POST'])
def broadcast():
    broadcast_form = BroadCastForm()
    if broadcast_form.validate():
        broadcast_form.add_into_queue()
        return "OK"
    return "Error"
{% endhighlight %}

接下来需要在 Web Service 中运行一个 WebSocket 服务器，这里我使用的是基于 geventwebsocket 的 Flask-Sockets。Flask 搭配 gevent 的 monkey patch 可以实现 Web Service 的非阻塞，对性能有相当大的提升。需要注意的是，geventwebsocket 官方版不支持 Python 3，需要使用第三方包 karellen-geventws。

这里我们使用了一个 Queue.queue 对象存储 Client Service 传来的消息，并将这些消息以每秒一条的速度传送给所有的客户端。

{% highlight python %}
clients = set()

@websocket_blueprint.route('/data')
def data(ws):
    clients.add(ws)

    while True:
        sleep(1)
        if mq.empty():
            continue

        msg = json.loads(mq.get())
        msg['online'] = clients.__len__()
        for w in clients.copy():
            try:
                w.send(json.dumps(msg))
            except WebSocketError:
                clients.remove(w)
{% endhighlight %}

正确启动 Web Service 需要使用 gevent 提供的 WSGI Server。

{% highlight python %}
from gevent.monkey import patch_all
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

patch_all()
app = create_app()
app.config.update(SERVER_NAME='127.0.0.1:8000')
http_server = WSGIServer(('0.0.0.0', 8000), app, handler_class=WebSocketHandler)
http_server.serve_forever()
{% endhighlight %}

启动服务，我们就可以开始随心所欲的抽卡了。

# Performance Test

为进行性能对比，我同时实现了一个没有使用 Nameko，仅由 Flask 完成的功能相同的单点版本，称作 Web Compare。

测试环境是腾讯云一块钱一个月的机器，单核 CPU，1GB 内存，Ubuntu 16.04，别的配置应该不用详细写了吧……

测试时 Card Service、Client Service、Web Service、Web Compare、MongoDB 和 RabbitMQ 均只有一个实例，Web Compare 与 Nameko 版本共享一个数据库。两个测试之间间隔二十分钟确保系统处于空闲状态。

使用命令：
{% highlight bash %}
$ ab -c 100 -n 1000 -p post -T application/x-www-form-urlencoded http://bc.yichyaqc.cn:8000/gateway/pick_card
{% endhighlight %}

Flask 版本性能如下：
```
Server Software:        
Server Hostname:        bc.yichyaqc.cn
Server Port:            8001

Document Path:          /gateway/pick_card
Document Length:        218 bytes

Concurrency Level:      100
Time taken for tests:   3.292 seconds
Complete requests:      1000
Failed requests:        886
   (Connect: 0, Receive: 0, Length: 886, Exceptions: 0)
Total transferred:      345514 bytes
Total body sent:        200000
HTML transferred:       217514 bytes
Requests per second:    303.74 [#/sec] (mean)
Time per request:       329.227 [ms] (mean)
Time per request:       3.292 [ms] (mean, across all concurrent requests)
Transfer rate:          102.49 [Kbytes/sec] received
                        59.32 kb/s sent
                        161.81 kb/s total

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:       28   34   7.1     32      83
Processing:    36  273 449.9    187    3254
Waiting:       35  272 450.0    187    3254
Total:         68  307 450.1    221    3290

Percentage of the requests served within a certain time (ms)
  50%    221
  66%    233
  75%    242
  80%    254
  90%    317
  95%    399
  98%   2662
  99%   3262
 100%   3290 (longest request)
```

Nameko 版本性能如下：
```
Server Software:        
Server Hostname:        bc.yichyaqc.cn
Server Port:            8000

Document Path:          /gateway/pick_card
Document Length:        212 bytes

Concurrency Level:      100
Time taken for tests:   15.960 seconds
Complete requests:      1000
Failed requests:        958
   (Connect: 0, Receive: 0, Length: 958, Exceptions: 0)
Total transferred:      344560 bytes
Total body sent:        200000
HTML transferred:       216560 bytes
Requests per second:    62.66 [#/sec] (mean)
Time per request:       1595.982 [ms] (mean)
Time per request:       15.960 [ms] (mean, across all concurrent requests)
Transfer rate:          21.08 [Kbytes/sec] received
                        12.24 kb/s sent
                        33.32 kb/s total

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:       28   33   5.9     31      76
Processing:   435 1526 620.8   1275    3159
Waiting:      434 1525 620.9   1274    3159
Total:        463 1559 621.0   1307    3189

Percentage of the requests served within a certain time (ms)
  50%   1307
  66%   1395
  75%   1958
  80%   2147
  90%   2793
  95%   2899
  98%   3000
  99%   3032
 100%   3189 (longest request)
 ```

可以看到，在没有扩展的时候，Nameko 版本由于涉及到较多的网络通信，整个过程所花的时间长了许多倍，每秒请求数也是处于极大劣势。当然，这是十分合情合理的。

在 RabbitMQ 的后台可以看到，积压的消息最多有大概 21 条，并发消息速度最高达到 200 条每秒。

![](../assets/images/nameko-cardpick-1/rabbitmq.png)

我们下一次将对 Nameko 服务进行横向扩充，以观察在较高的并发压力下，Nameko 实现的可扩展架构受到的性能影响是否小于单个 Flask App。

# Other Things

如果你们的兴趣点并不在架构而在卡池上的话……

【关于卡池的设计】

通过咨询某松之苍斗鸡第一大佬，他的建议是卡池爆率设计为 350:50:1。简单猜测了一下每天抽卡的次数，综合考虑我服务器上 MongoDB 的写入性能，卡池刷新设计为每 1152 秒清空并放入 3208 张新卡。

其实清空不清空倒是次要的，我这么做只是怕数据库被撑爆 2333333

【关于出三勾四勾的概率】

这个我没问也没咋想，随便想了个概率，94:5:1。

【关于抽卡机制】

抽卡算法是，客户端提供给服务端一个随机字符串，我在后面加一个随机字符串后打乱顺序并计算 hash，然后将卡池中第一个 hash 值比它大的卡作为结果返回。

这个做法我也没咋想……反正不是重点……

抽卡时候的天时、地利、人和分别是服务端最终用来匹配的 Hash、匹配到的那张卡的 Hash，以及客户端随机字符串的 Hash。
