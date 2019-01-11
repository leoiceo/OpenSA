#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
from django.utils.translation import ugettext_lazy as _
from django.db import models
import uuid


from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
                                password=password,
                                username=username,
                                )
        user.level = 2
        user.is_superuser = True
        user.save(using=self._db)
        return user


class DepartMent(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('DepartMent Name'))
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('DepartMent Comment'))

    class Meta:
        db_table = "department"
        verbose_name = _('DepartMent Manage')
        verbose_name_plural = _('DepartMent Manage')

    def __str__(self):
        return self.name

    @property
    def user_list(self):
        user_name = DepartMent.objects.get(name=self.name)
        return user_name.userprofile_set.all()

class Project(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Project Name'))
    mini_name = models.CharField(max_length=64, unique=True, blank=True, null=True, verbose_name=_('Project MiniName'))
    create_date = models.DateField(auto_now_add=True, blank=True, null=True, verbose_name=_('Create By'))
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Project Comment'))
    key = models.ManyToManyField(to="KeyManage",blank=True,verbose_name=_("Project Keyfile"))

    class Meta:
        db_table = "project"
        verbose_name = _('Project Manage')
        verbose_name_plural = _('Project Manage')

    def __str__(self):
        return self.name

    @property
    def user_name(self):
        return Project.objects.get(name=self.name).userprofile_set.all()

    @property
    def key_name(self):
        return Project.objects.get(name=self.name).key.all()

class KeyManage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=32,unique=True,verbose_name=_("Key Name"))
    user = models.CharField(max_length=64,blank=True,null=True,verbose_name=_("Key User"))
    password = models.CharField(max_length=64,blank=True, null=True,verbose_name=_("Key Password"))
    private = models.TextField(verbose_name=_("Private Key"))
    public = models.TextField(verbose_name=_("Public Key"))
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Create By'))

    class Meta:
        db_table = "keymanage"
        verbose_name = _('Key Manage')
        verbose_name_plural = _('Key Manage')

    def __str__(self):
        return self.name

    @property
    def project_name(self):
        key = KeyManage.objects.get(name=self.name)
        return key.project_set.all()


class PermissionList(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('Permission Name'))
    lable_name = models.CharField(max_length=32, unique=True, blank=True,null=True,verbose_name=_('Permission Lable'))
    url = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name=_('Permission Url'))
    menu = models.ManyToManyField(to="MenuList",blank=True,verbose_name=_("Menu Manager"))

    class Meta:
        db_table = "permissionList"
        verbose_name = _('Permission Manage')
        verbose_name_plural = _('Permission Manage')

    def __str__(self):
        return '{}({})'.format(self.name, self.url)

class MenuList(models.Model):
    name = models.CharField(max_length=32,blank=True,null=True,verbose_name="Menu Name")
    first = models.CharField(max_length=32,blank=True,null=True,verbose_name="First Menu")
    secondary = models.CharField(max_length=32,blank=True,null=True,default="Nothing",verbose_name="Secondary Menu")

    class Meta:
        db_table = "menuList"
        verbose_name = _('Menu Manage')
        verbose_name_plural = _('Menu Manage')

    def __str__(self):
        return "{}->{}".format(self.first,self.secondary)

class RoleList(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('RoleName'))
    permission = models.ManyToManyField(to='PermissionList', blank=True, verbose_name=_('Permission List'))
    class Meta:
        db_table = "rolelist"
        verbose_name = _('Role Manage')
        verbose_name_plural = _('Role Manage')

    def __str__(self):
        return self.name

USER_LEVEL_TYEP = (
    (0, _('View')),
    (1, _('Exec')),
    (2, _('Delete')),
)


class UserProfile(AbstractBaseUser):
    email = models.EmailField(
        verbose_name=_('Email Address'),
        max_length=255,
        unique=True,
    )

    username = models.CharField(max_length=32, verbose_name=_("UserName"))
    token = models.CharField(max_length=128, default=None, blank=True, null=True, verbose_name=_("Token"))
    department = models.ForeignKey(to="DepartMent", blank=True, null=True, on_delete=models.SET_NULL,
                                   verbose_name=_('User Department'))
    mobile = models.CharField(max_length=32, default=None, blank=True, null=True, verbose_name=_('Mobile Phone'))
    project = models.ManyToManyField(to="Project", default=None, blank=True, verbose_name=_("User Project"))
    level = models.IntegerField(choices=USER_LEVEL_TYEP,default=0, blank=True, verbose_name=_('User Level'))
    role = models.ForeignKey(to="RoleList", null=True, blank=True, on_delete=models.SET_NULL,
                             verbose_name=_("User Role"))
    avatar = models.CharField(default="user.png", max_length=64, blank=True, verbose_name=_("User Avatar"))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    is_superuser = models.BooleanField(default=False, verbose_name=_('User Type'))
    limit = models.IntegerField(default=0, blank=True, verbose_name=_('Login Limit'))
    create_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Create By'))
    login_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Login By'))
    valid_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Valid Date'))
    comment = models.CharField(max_length=128,blank=True, null=True, verbose_name=_('User Comment'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = "userprofile"
        verbose_name = _('User Manage')
        verbose_name_plural = _("User Manage")

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_perms(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

    objects = UserManager()

    #User = get_user_model()