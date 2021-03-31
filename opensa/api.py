#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by leoiceo
from __future__ import absolute_import, unicode_literals
import os
import pwd
import paramiko
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import AccessMixin,LoginRequiredMixin
from users.models import Project,UserProfile,RoleList
import difflib
import sys,json
import numpy as np
from opensa.settings import DATA_DIR,STATIC_DIR
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

class OpenSaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

def readfile(filename):
    try:
        fileHandle = open(filename, 'r+')
        text = fileHandle.read().splitlines()
        fileHandle.close()
        return text
    except IOError as error:
        print('Read file Error:' + str(error))
        sys.exit()

def diff_content(old_file,new_file,fileid):
    old_lines = readfile(old_file)
    new_lines = readfile(new_file)
    d = difflib.HtmlDiff()
    content = d.make_file(old_lines, new_lines)
    diff_content_dir = "{}/diff/".format(STATIC_DIR)
    mkdir(diff_content_dir)
    diff_content_file = "{}/{}.html".format(diff_content_dir,fileid)

    with open(diff_content_file,'w') as f:
        f.write(content)

    return diff_content_file

def generate_scripts(id,content):
    script_dir = "{}/script".format(DATA_DIR)
    mkdir(script_dir)
    script_name = "{}.sh".format(id)
    file = "{}/{}".format(script_dir,script_name)

    with open(file,'w') as f:
        data = content.replace('\r\n', '\n')
        f.seek(0, 0)
        f.truncate()
        f.write(data)

    return script_dir,script_name

def generate_keyfile(id,pkey):
    keydir = "{}/key".format(DATA_DIR)
    mkdir(keydir)
    key_name = "{}.key".format(id)
    keyfile = "{}/{}".format(keydir,key_name)

    with open(keyfile,'w') as f:
        data = pkey.replace('\r\n', '\n')
        f.seek(0, 0)
        f.truncate()
        f.write(data)

    os.chmod(keyfile, 0o600)
    return keyfile

def chown(path, user, group=''):
    if not group:
        group = user
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = pwd.getpwnam(group).pw_gid
        os.chown(path, uid, gid)
    except KeyError:
        pass

def mkdir(dir_name, username='', mode=0o755):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
        os.chmod(dir_name, mode)
    if username:
        chown(dir_name, username)

def check_and_file(file_name):
    if not  os.path.exists(file_name):
        os.mknod(file_name)

def custom_project(request):
    try:
        iUser = UserProfile.objects.get(email="%s" % request.user)
        if iUser.is_superuser:
            pro_info = Project.objects.all()
        else:
            pro_info = iUser.project.all()

    except Exception as e:
        pro_info = None

    try:
        project = request.session["project"]
    except Exception as e:
        project = None

    return {
        "pro_info" : pro_info,
        "project" : project
    }


class LoginPermissionRequired(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            iUser = UserProfile.objects.get(email="{}".format(request.user))
            if not iUser.is_superuser:
                role_permission = RoleList.objects.get(name=iUser.role.name)
                role_permission_list = role_permission.permission.all()
                matchUrl = []
                for x in role_permission_list:
                    if request.path == x.url or request.path.rstrip('/') == x.url:
                        matchUrl.append(x.url)
                    elif request.path.startswith(x.url):
                        matchUrl.append(x.url)

                if len(matchUrl) == 0:
                    return HttpResponseRedirect('/')
        except Exception as e:
            return HttpResponseRedirect('/')

        return super().dispatch(request, *args, **kwargs)


class Choice_Project(LoginRequiredMixin,View):
    model = Project

    def post(self, request):
        number = 0
        try:
            id = request.POST.get('nid', None)
            name = Project.objects.get(id=id).name
            request.session['project'] = name
            number = 1
        except Exception as e:
            number = 0
        finally:
            return HttpResponse(number)

class Connection(object):
    def __init__(self, ip, user, port=22, key='/root/.ssh/id_rsa',remote_file='/tmp',local_dir=None,remote_dir=None,password=None,keypass=None,timeout=300):
        self.ip = ip
        self.user = user
        self.port = int(port)
        self.timeout = int(timeout)
        self.try_times = 3
        self.remote_file = remote_file
        self.local_dir = local_dir
        self.remote_dir = remote_dir
        #self.private_key = paramiko.RSAKey.from_private_key_file(key)
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        if not password:
            if not keypass:
                self.private_key = paramiko.RSAKey.from_private_key_file(key)
            else:
                self.private_key = paramiko.RSAKey.from_private_key_file(key, keypass)
            self.client.connect(hostname=self.ip,
                                port=self.port,
                                username=self.user,
                                pkey=self.private_key)
        else:
            self.client.connect(hostname=self.ip,
                                port=self.port,
                                username=self.user,
                                password=password)
        self.transport = self.client.get_transport()
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.channel = self.transport.open_channel('session')
        self.channel.settimeout(None)
        self.channel.set_combine_stderr(True)

    def __del__(self):
        self.client.close()


    def downlowd(self, local_dir):
        self.sftp.get(self.remote_file, local_dir)

    def upload(self, local_dir):
        self.sftp.put(local_dir, self.remote_file)

    def upload_dir(self,local_dir,remote_dir):
        try:
            for root, dirs, files in os.walk(local_dir):
                for name in dirs:
                    local_path = os.path.join(root, name)
                    a = local_path.replace(local_dir, '')
                    remote_file = "{}{}".format(remote_dir, a)
                    cmd = "mkdir -p {}".format(remote_file)
                    self.client.exec_command(cmd, timeout=self.timeout)

                for filespath in files:
                    local_file = os.path.join(root, filespath)
                    if root != local_dir:
                        a = local_file.replace(local_dir, '')
                        remote_file = "{}{}".format(remote_dir,a)
                    else:
                        remote_file = os.path.join(remote_dir, filespath)
                    self.sftp.put(local_file, remote_file)

            result = {"result": True, "message": 'upload {} to {} success'.format(local_dir,remote_dir)}
        except Exception as e:
            result = {"result":False, "message":"{}".format(e)}

        return result

    def linux_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd,timeout=self.timeout)
        result = stdout.read()
        error = stderr.read()
        if error:
            return {"result":False, "message":error,"status": False}
        else:
            return {"result":True, "message":result,"status": True}

    def task_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command('{}'.format(cmd), timeout=self.timeout)
        result = stdout.read()
        error = stderr.read()
        channel = stdout.channel
        status = channel.recv_exit_status()
        if int(status) is 0:
            status = True
        else:
            status = False

        if error:
            return {"result": False, "message": error, "status": False}
        else:
            return {"result": True, "message": result, "status": status }

    def win_cmd(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd,timeout=self.timeout)
        result = stdout.read().decode('gbk').encode('utf-8')
        error = stderr.read().decode('gbk').encode('utf-8')
        if not error and "ERROR" not in result:
            return {"result":True, "message":result}
        else:
            if error:
                return {"result":False, "message":error}
            else:
                return {"result":False, "message":result}

    def rsync(self,local_dir, remote_dir,exclude_file, dot=True):
        check_and_file(exclude_file)

        if dot:
            cmd = "/usr/bin/rsync -q -rt --delete --delete-after --progress --exclude-from='{0}' -e 'ssh -i {1} -o StrictHostKeyChecking=no -o PasswordAuthentication=no -p {2}' {3}/ {4}@{5}:{6}/".format(
                exclude_file,self.private_key , self.port, local_dir, self.user, self.ip, remote_dir)
        else:
            cmd = "/usr/bin/rsync -q -rt --progress --exclude-from='{0}' -e 'ssh -i {1} -o StrictHostKeyChecking=no -o PasswordAuthentication=no -p {2}' {3}/ {4}@{5}:{6}/".format(
                exclude_file,self.private_key, self.port, local_dir, self.user, self.ip, remote_dir)
        ret = self.linux_cmd(cmd)
        return ret



class RequestMiddleware(object):

    def __init__(self, get_response):
        #print("程序启动时执行, 只执行一次")
        self.get_response = get_response

    def __call__(self, request):
        #print("中间件开始")
        from audit.models import RequestRecord
        try:
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                remote_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                remote_ip = request.META['REMOTE_ADDR']

            if request.method == 'POST':
                request_type = 1
            else:
                request_type = 0
            if request.path == "/skin_config/" or 'admin' in request.path or 'favicon' in request.path \
                    or 'audit' in request.path or '/toastr.js.map' in request.path:
                pass
            else:
                get_path = request.get_full_path()
                if len(request.FILES) > 0 :
                    post_body = request.FILES
                else:
                    post_body = request.body

                up_obj = UserProfile.objects.get(username=request.user.username)
                RequestRecord.objects.create(username=up_obj, type=request_type, ipaddr=remote_ip,
                                             get_full_path=get_path,post_body=post_body)

        except Exception as e:
            import datetime
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


        response = self.get_response(request)
        #print("中间件结束")
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        #print("请求实际函数前执行")
        pass

    def process_exception(self, request, exception):
        #from django.http import JsonResponse
        print("程序异常时执行")

        #return JsonResponse({"msg": exception.args[0], "code": -1})


