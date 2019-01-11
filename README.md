# OpenSA
# 企业级运维自动化平台 
####安装部署说明
* 系统: CentOS 7
```
setenforce 0
sed -i "s/enforcing/disabled/g" /etc/selinux/config

# 修改字符集,否则可能报 input/output error的问题,因为日志里打印了中文
localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
echo 'LANG="zh_CN.UTF-8"' > /etc/locale.conf
```
* 安装 Python3 
```
wget http://www.python.org/ftp/python/3.7.1/Python-3.7.1.tar.xz
tar -zxvf Python-3.7.1.tar.xz && cd Python-3.7.1 
./configure --prefix=/usr/local/python37
make && make install
```
* 拉取代码安装模块
```
cd /opt/
git clone https://github.com/leoiceo/OpenSA
wget --no-check-certificate https://bootstrap.pypa.io/ez_setup.py
python ez_setup.py --insecure
easy_install pip

# 修改pypi源
mkdir -p ~/.pip/
cat ~/.pip/pip.conf <<EOF
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host=mirrors.aliyun.com
EOF

cd OpenSA
pip -r requirements.txt
```
* 初始化数据库
```
cd /opt/OpenSA
sh migrate.sh

#初始化权限和用户
python manage.py permission_data
```
* 启动
```
python manage.py runserver 0.0.0.0:8000
```
* 初始账号密码登陆
> 账号: opensa@imdst.com
> 密码：redhat
* Demo地址
>http://opensa.imdst.com 
>user: demo@imdst.com 
>pass: Demo123
#### 功能说明
### 资产管理
### 作业管理
* 脚本管理
* 计划任务
* 任务编排
* 文件分发
* 批量执行脚本
* 批量执行命令
* 批量执行任务

### 日志审计
* 改密日志
* 登陆日志
* 请求日志
* 作业日志
* 录像回放

### 系统设置
* 用户管理  
* 部门管理  
* 项目管理 
* 权限管理 
* 角色管理 
* 密钥管理

### 未来开发计划
* 持续集成(待开发)
* 灰度发布(待开发)
* 反向代理可视化(待开发)

#### 架构说明
* Django 2.1 + Mysql 5.7 + redis 3.2 + celery v4.2.0 
* 命令和文件分发基于SSH协议，支持Linux/Windows(cygwin)|支持快速修改为ansible
* 使用2.7版本inspina模版
* 支持国际化(默认中/英)

#### 交流群QQ: 142189771

#### 预览进度
* [博客地址](https://blog.imdst.com/kai-yuan-yun-wei-zi-dong-hua-ping-tai-kai-fa-she-ji-si-lu/)

