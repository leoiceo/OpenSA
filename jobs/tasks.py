#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by leoiceo
from __future__ import absolute_import
import os,json,time
from opensa import settings
from celery import shared_task,current_task
from asset.models import Asset
from audit.models import TaskSchedule,JobsResults
from jobs.models import ScriptsManage,TaskScheduling
from opensa.api import generate_keyfile,generate_scripts,Connection,OpenSaEncoder
from django.utils.translation import ugettext as _


@shared_task
def batch_scripts_func(*args,**kwargs):

    current_task.update_state(state='PROGRESS')
    jr_obj = JobsResults.objects.get(id=args[0])
    ts_obj = TaskSchedule.objects.get(task_id=batch_scripts_func.request.id)

    jr_obj.task_schedule.add(ts_obj)

    script_obj = ScriptsManage.objects.get(id=args[1])
    timeout = args[2]
    input_args = args[3]
    asset_obj = Asset.objects.get(id=args[4])
    ts_obj.asset = asset_obj
    ts_obj.save()

    script_dir, script_name = generate_scripts(script_obj.id, script_obj.content)
    script_type = script_obj.get_type_display()

    if script_type == "shell" or script_type == "bat":
        script_env = "/bin/bash"
    else:
        script_env = "/usr/bin/python"


    user = jr_obj.key.user
    keypass = jr_obj.key.password
    keyfile = generate_keyfile(jr_obj.key.id, jr_obj.key.private)


    localfile = "{}/{}".format(script_dir, script_name)
    remotefile = "/tmp/{}".format(script_name)

    batch_script = Connection(ip=asset_obj.ip, user=user, port=asset_obj.port, key=keyfile, remote_file=remotefile, password=keypass,keypass=jr_obj.key.password,
                              timeout=timeout)
    batch_script.upload(localfile)

    if len(input_args) > 0:
        cmd = "{} {} {}".format(script_env,remotefile,' '.join(input_args))
    else:
        cmd = "{} {}".format(script_env,remotefile)

    ret = batch_script.linux_cmd(cmd)
    if ret["result"]:
        ts_obj.log = "on {} server execution {} successed".format(asset_obj.hostname,script_obj.name)
    else:
        ts_obj.log = "on {} server execution {} failed".format(asset_obj.hostname, script_obj.name)

    ts_obj.save()
    return json.dumps(ret["message"], ensure_ascii=False, cls=OpenSaEncoder)

@shared_task
def batch_files_func(*args,**kwargs):

    current_task.update_state(state='PROGRESS')
    jr_obj = JobsResults.objects.get(id=args[0])
    ts_obj = TaskSchedule.objects.get(task_id=batch_files_func.request.id)

    jr_obj.task_schedule.add(ts_obj)
    upload_id = args[1]
    remote_dir = args[2]
    timeout = args[3]
    asset_obj = Asset.objects.get(id=args[4])
    ts_obj.asset = asset_obj
    ts_obj.save()

    user = jr_obj.key.user
    keypass = jr_obj.key.password
    keyfile = generate_keyfile(jr_obj.key.id, jr_obj.key.private)

    local_dir = "{}/upload/{}".format(settings.DATA_DIR, upload_id)
    batch_files = Connection(ip=asset_obj.ip, user=user, port=asset_obj.port, key=keyfile, local_dir=local_dir,remote_dir=remote_dir,
                          password=keypass,timeout=timeout)

    result = batch_files.upload_dir(local_dir,remote_dir)

    ts_obj.save()

    if result["result"]:
        ts_obj.log = "on {} server upload dir {} successed".format(asset_obj.hostname, upload_id)
        cmd = "ls -l {}".format(remote_dir)
        ret = batch_files.linux_cmd(cmd)
    else:
        ts_obj.log = "on {} server upload dir {} failed".format(asset_obj.hostname, upload_id)
        ret = {
            "message":result["message"]
        }
    return json.dumps(ret["message"], ensure_ascii=False, cls=OpenSaEncoder)

@shared_task
def ExecutionCmd(*args,**kwargs):
    current_task.update_state(state='PROGRESS', meta={'current': "10%", 'total': 100})
    ts_obj = TaskSchedule.objects.get(task_id=ExecutionCmd.request.id)
    jr_obj = JobsResults.objects.get(id=args[0])
    jr_obj.task_schedule.add(ts_obj)
    asset_obj = Asset.objects.get(id=args[1])
    ts_obj.asset = asset_obj
    ts_obj.save()
    current_task.update_state(state='PROGRESS', meta={'current': "20%", 'total': 100})
    user = jr_obj.key.user
    keypass = jr_obj.key.password
    keyfile = generate_keyfile(jr_obj.key.id, jr_obj.key.private)
    current_task.update_state(state='PROGRESS', meta={'current': "40%", 'total': 100})
    batch_script = Connection(ip=asset_obj.ip, user=user, port=asset_obj.port, key=keyfile, keypass=keypass,)
    ret = batch_script.linux_cmd(args[2])
    current_task.update_state(state='PROGRESS', meta={'current': "60%", 'total': 100})
    if ret["result"]:
        ts_obj.log = "on {} server execution {} successed".format(asset_obj.hostname, "{}".format(args[2]))
    else:
        ts_obj.log = "on {} server execution {} failed".format(asset_obj.hostname, "{}".format(args[2]))
    current_task.update_state(state='PROGRESS', meta={'current': "80%", 'total': 100})
    ts_obj.save()
    current_task.update_state(state='PROGRESS', meta={'current': "100%", 'total': 100})
    return ret["message"].decode("utf-8")

@shared_task
def batch_task_func(*args,**kwargs):
    task_dict, message_dict = {}, {}
    message_list = []
    current_task.update_state(state='PROGRESS')
    jr_obj = JobsResults.objects.get(id=args[0])
    ts_obj = TaskSchedule.objects.get(task_id=batch_task_func.request.id)

    jr_obj.task_schedule.add(ts_obj)

    task_obj = TaskScheduling.objects.get(id=args[1])
    timeout = args[2]
    asset_obj = Asset.objects.get(id=args[3])
    ts_obj.asset = asset_obj
    ts_obj.save()
    user = jr_obj.key.user
    keypass = jr_obj.key.password
    keyfile = generate_keyfile(jr_obj.key.id, jr_obj.key.private)

    for i in task_obj.task_scripts.all().order_by('level'):
        script_obj = ScriptsManage.objects.get(id=i.scripts.id)
        script_dir, script_name = generate_scripts(script_obj.id, script_obj.content)
        script_type = script_obj.get_type_display()
        try:
            if script_type == "shell" or script_type == "bat":
                script_env = "/bin/bash"
            else:
                script_env = "/usr/bin/python"

            localfile = "{}/{}".format(script_dir, script_name)
            remotefile = "/tmp/{}".format(script_name)

            batch_script = Connection(ip=asset_obj.ip, user=user, port=asset_obj.port, key=keyfile, remote_file=remotefile,
                                      keypass=keypass,timeout=timeout)

            batch_script.upload(localfile)
            cmd = "{} {}".format(script_env,remotefile)

            time.sleep(i.delaytime)
            ret = batch_script.task_cmd(cmd)

            message = "script name:{} level:{} server:{}\\nresult:\\n{}\\n".format(script_obj.name,i.level,asset_obj.ip,ret["message"].decode())
            message_list.append(message)

            if ret["result"] and ret["status"]:

                task_dict['{}_{}'.format(script_obj.name,i.level)] = _("execution successed")

            else:
                if ret["result"]:
                    log = _("execution success,exception exit")
                else:
                    log = _("execution success,error exit")


                if i.status == 1:
                    task_dict['{}_{}'.format(script_obj.name, i.level)] = log

                else:
                    task_dict['{}_{}'.format(script_obj.name, i.level)] = log
                    break

        except Exception as e:
            task_dict['{}_{}'.format(script_obj.name, i.level)] = _("execution failed")
            message = "script name:{}\\nlevel:{}\\nresult:\\n{}\\n".format(script_obj.name, i.level, e)
            message_list.append(message)
    ts_obj.log = task_dict
    ts_obj.save()
    return json.dumps(message_list, ensure_ascii=False, cls=OpenSaEncoder)


@shared_task
def crontab_scripts(ip, job, script):
    input_args ={}
    timeout = 1000
    from celery import group
    group(batch_scripts_func.s(job, script, timeout, input_args, i) for i in ip)()

@shared_task
def crontab_task(ip, job, task):
    timeout = 1000
    from celery import group
    group(batch_task_func.s(job, task, timeout, i) for i in ip)()

