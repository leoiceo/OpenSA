#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from django.utils.translation import ugettext_lazy as _
from django.db import models
import uuid

class Asset(models.Model):
    ASSET_STATUS = (
        (1, _("Used")),
        (2, _("Unused")),
        (3, _("Scraped")),
        (4, _("SoldOut"))
    )
    ASSET_TYPE = (
        (1, _("Physical Machine")),
        (2, _("Virtual Machine")),
        (3, _("Switch Board")),
        (4, _("Router")),
        (5, _("Firewall")),
        (6, _("Docker")),
        (7, _("Other"))
    )
    ASSETOS_TYPE=(
        (0,"Centos"),
        (1,"Windows"),
        (2,"Ubuntu"),
        (3,"Debian"),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    hostname = models.CharField(max_length=64, null=True,verbose_name=_("HostName"))
    ip = models.GenericIPAddressField(unique=True, verbose_name=_("IP"))
    other_ip = models.GenericIPAddressField(blank=True,null=True, verbose_name=_("Other_IP"))
    port = models.IntegerField(default=22, verbose_name=_("Port"))
    user = models.CharField(max_length=64,default='root', verbose_name=_("Asset User"))
    password = models.CharField(max_length=100,null=True, verbose_name=_("Asset PassWord"))
    asset_type = models.IntegerField(choices=ASSET_TYPE, null=True, blank=True, verbose_name=_("Asset Type"))
    os_type = models.IntegerField(choices=ASSETOS_TYPE, null=True, blank=True, verbose_name=_("System Type"))
    system_version = models.CharField(max_length=32,null=True, blank=True, verbose_name=_("System Version"))
    mac = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("MAC"))
    cpu_type = models.CharField(max_length=128,  null=True, blank=True, verbose_name=_("CPU Type"))
    cpu_core = models.IntegerField( null=True, blank=True,verbose_name=_("CPU Core Count"))
    cpu_total = models.IntegerField( null=True, blank=True,verbose_name=_("Number of CPUs"))
    sn = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("Asset SN Number"))
    memory = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("Asset Memory"))
    disk_info = models.CharField(max_length=512, null=True, blank=True, verbose_name=_("Disk Information"))
    disk_mount = models.CharField(max_length=512, null=True, blank=True, verbose_name=_("Mount Partition"))
    server_type = models.CharField(max_length=64, null=True, blank=True, verbose_name=_("Server Model"))
    os_kernel = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("System Kernel Version"))
    system_arch = models.CharField(max_length=32, null=True, blank=True, verbose_name=_("System Platform"))
    status = models.IntegerField(choices=ASSET_STATUS, null=True, blank=True, default=1, verbose_name=_("Equipment Status"))
    create_date = models.DateTimeField(blank=True, auto_now_add=True, verbose_name=_("Create By"))
    update_date = models.DateTimeField(blank=True, auto_now=True, verbose_name=_("Update By"))

    project = models.ForeignKey(to="users.Project", related_name='project_asset', default=None, blank=True, null=True,
                                on_delete=models.SET_NULL, verbose_name=_("User Project"))
    idc = models.ForeignKey(to="Idc", null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("IDC"))
    product = models.ForeignKey(to="Product", related_name='product_asset', default=None, null=True,
                                blank=True, on_delete=models.SET_NULL, verbose_name=_("Product"))
    work_env = models.ForeignKey(to="Work_Env", null=True, blank=True, on_delete=models.SET_NULL,
                                 related_name='work_asset', verbose_name=_("Working Environment"))
    use = models.ManyToManyField(to="ServerUse", blank=True, related_name='serveruse_asset', verbose_name=_("Server Use"))



    class Meta:
        db_table = "asset"
        verbose_name = _("Asset Information List")
        verbose_name_plural = _("Asset Information List")

    def __str__(self):
        return self.ip

    @property
    def use_list(self):
        asser = Asset.objects.get(ip=self.ip)
        return asser.use.all()

class ServerUse(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=_("Server Use Name"))
    mini_name = models.CharField(max_length=32, unique=True, verbose_name=_("Server Use Short Name"))

    class Meta:
        db_table = "serveruse"
        verbose_name = _("Server Use")
        verbose_name_plural = _("Server Use")

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=_("Area Name"))
    mini_name = models.CharField(max_length=32, unique=True, verbose_name=_("Area Short Name"))

    class Meta:
        db_table = "area"
        verbose_name = _("Area")
        verbose_name_plural = _("Area")

    def __str__(self):
        return self.name

class Work_Env(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name=_("Work_Env Name"))
    mini_name = models.CharField(max_length=32, unique=True, verbose_name=_("Work_Env Short Name"))

    class Meta:
        db_table = "work_env"
        verbose_name = _("Work_Env")
        verbose_name_plural = _("Work_Env")

    def __str__(self):
        return self.name


class Idc(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_("Idc Name"))
    address = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Idc Address"))
    net_line = models.CharField(max_length=32, blank=True, null=True, default=None, verbose_name=_("Line"))
    bandwidth = models.CharField(max_length=32, blank=True, null=True, default=None, verbose_name=_("Bandwidth"))
    linkman = models.CharField(max_length=16, blank=True, null=True, default=None, verbose_name=_("Customer Manager"))
    phone = models.CharField(max_length=32, blank=True, null=True, default=None, verbose_name=_("Contact number"))
    cabinet_info = models.CharField(max_length=30,blank=True, null=True, default=None, verbose_name=_('Cabinet information'))
    ip_range = models.CharField(max_length=30,blank=True, null=True, default=None, verbose_name=_('IP Range'))
    comment = models.CharField(max_length=128, blank=True, default=None, null=True, verbose_name=_('User Comment'))
    area = models.ForeignKey(to="Area", related_name='area_idc', default=None, blank=True, null=True,
                             on_delete=models.SET_NULL, verbose_name=_("Regional Management"))

    class Meta:
        db_table = "idc"
        verbose_name = _("Idc Manage")
        verbose_name_plural = _("Idc Manage")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=64,unique=True, verbose_name=_("Product Name"))
    mini_name = models.CharField(max_length=32,unique=True, verbose_name=_("Product Short Name"))

    class Meta:
        db_table = "product"
        verbose_name = _("Product Manage")
        verbose_name_plural = _("Product Manage")

    def __str__(self):
        return self.name
