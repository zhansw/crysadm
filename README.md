##说明
这个项目是从[powergx](https://git.airl.us/powergx)的[Crysadm](https://git.airl.us/powergx/crysadm)项目fork来的。原项目的目的是构建一个web版本迅雷赚钱宝的监控平台。因为我没有服务器，所以我做了这个docker镜像部署项目，使用[DaoCloud](https://www.daocloud.io/)提供的免费Docker容器来运行(二级域名也挺好的哦~~)。


##非常惭愧
github的帐号很久以前就注册了，但是没有好好利用。总是三天打鱼两天晒网，这是第一次正真意义上使用github平台，所以有做的不对的地方，请各位客官见谅。

##部署
赚钱宝的主人们可以无偿使用这套代码来部署属于自己的监控平台。对软件部署不懂的朋友，我调试好容器后，会做一个DaoCloud平台注册和使用教程，到时候我会将我做的镜像公布出来，方便大家使用。

##感谢
在此特别感谢[powergx](https://git.airl.us/powergx)同学，感谢他的无私奉献精神，让我们有这么好的web监控体验。谢谢！

##powergx：
运行环境 python3.3+ , redis
* crysadm 启动web服务
* config 配置redis server
* crysadm_helper 启动后台服务

安装后访问 /install 生成管理员账号
config.py.example 改名为config.py 使用