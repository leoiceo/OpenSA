# OpenSA 运维自动化平台 

[![Python3](https://img.shields.io/badge/python-3.7-green.svg?style=plastic)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-2.1-brightgreen.svg?style=plastic)](https://www.djangoproject.com/)
[![Ansible](https://img.shields.io/badge/ansible-2.6.3-blue.svg?style=plastic)](https://www.ansible.com/)
[![Paramiko](https://img.shields.io/badge/paramiko-2.4.2-green.svg?style=plastic)](http://www.paramiko.org/)

#### 架构说明
* Django 2.1 + Mysql 5.7 + redis 5.0 + celery v4.2.0 
* 生产环境请使用 nginx + uwsgi,不对公网开放,或者使用SSL双向认证
* 命令和文件分发基于SSH协议，支持Linux/Windows(cygwin)|支持快速修改为ansible
* 使用2.7版本inspina模版
* 支持国际化(默认中/英)，有些细节未完善，欢迎加入完善项目，联系WX “leoiceo” 或者加群(142189771)
* 如果系统自己用得还不错,请多多推荐给身边的朋友 (star！star！star！......)
* 欢迎提交功能开发和优化建议！

#### [screenshots](https://github.com/leoiceo/OpenSA/wiki/screenshots) 
* screenshots文件200M以上,建议 download screenshots 目录进行查看

#### [中文指南 wiki](https://github.com/leoiceo/OpenSA/wiki)

#### 安装部署说明
* 系统: CentOS 7
```
setenforce 0
sed -i "s/enforcing/disabled/g" /etc/selinux/config

# 修改字符集,否则可能报 input/output error的问题,因为日志里打印了中文
localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
echo 'LANG="zh_CN.UTF-8"' > /etc/locale.conf
```
* 安装 Python3  && redis 
```
wget http://www.python.org/ftp/python/3.7.1/Python-3.7.1.tar.xz
tar -xvf Python-3.7.1.tar.xz && cd Python-3.7.1 
./configure --prefix=/usr/local/python37
make && make install

yum install redis -y
service redis start

##settings 设置了密码，可自行修改Redis.conf
```
* 拉取代码安装模块
```
cd /opt/
git clone https://github.com/leoiceo/OpenSA
wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py
python ez_setup.py --insecure

# 创建日志目录 
mkdir -p /data/opensa/logs
 
# 修改pypi源
mkdir -p ~/.pip/
cat > ~/.pip/pip.conf <<EOF
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host=mirrors.aliyun.com
EOF

cd OpenSA
/usr/local/python37/bin/pip install -r requirements.txt
```
* 初始化数据库 (修改 config.conf 设置DB和redis配置信息)
```
cd /opt/OpenSA
sh migrate.sh

# 初始化权限和用户
python manage.py permission_data

# 国际化文件生成
django-admin makemessages -l en
django-admin compilemessages
```

* Celery 后台启动
```
cd /opt/OpenSA
nohup /usr/local/python37/bin/celery -B -A opensa worker --loglevel=INFO  &
```

* 启动
```
cd /opt/OpenSA
python manage.py runserver 0.0.0.0:8000
```
 
* 默认用户名密码
```
管理员： opensa@imdst.com
密码：redhat
```

#### 交流群QQ: 142189771

#### 截图
![](https://github.com/leoiceo/OpenSA/blob/master/screenshots/1.png)
![](https://github.com/leoiceo/OpenSA/blob/master/screenshots/2.png)
![](https://github.com/leoiceo/OpenSA/blob/master/screenshots/3.png)
![](https://github.com/leoiceo/OpenSA/blob/master/screenshots/4.png)
#### 预览进度
* [博客地址](https://blog.imdst.com/kai-yuan-yun-wei-zi-dong-hua-ping-tai-kai-fa-she-ji-si-lu/)

#### 参与人员
* pzp

#### 附上一波小广告，【炎陵黄桃】 自家果园，每年一季，欢迎尝鲜
* [快来吃桃了！](https://blog.imdst.com/ylht-zjgy-xzxf/)
* 扫码购买

![](https://github.com/leoiceo/OpenSA/blob/master/static/img/0a73f3fcf8d43667286430b11c10b.png)
