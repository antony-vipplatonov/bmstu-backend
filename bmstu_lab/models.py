from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager, PermissionsMixin
from django.db import models

class Users(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)
    is_staff = models.BooleanField(null=True)
    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        db_table = 'Users'

class Compaund(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    admiralname = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    victory = models.TextField(blank=True, null=True)
    status = models.CharField(default="черновик")
    creatorname = models.ForeignKey(Users, models.DO_NOTHING, db_column='creatorname')
    moderatorname = models.ForeignKey(Users, models.DO_NOTHING, db_column='moderatorname', related_name='compaund_moderatorname_set', null=True)
    datacreate = models.DateTimeField(auto_now=True)
    dataform = models.DateTimeField(blank=True, null=True)
    dataend = models.DateTimeField(blank=True, null=True)
    battledate = models.DateField(blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'Compaund'

class Ship(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    weapon = models.TextField()
    armoring = models.TextField()
    year = models.IntegerField()
    displacement = models.FloatField()
    length = models.FloatField()
    speed = models.FloatField()
    status = models.CharField(max_length=15, default="действует")
    image_src = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ship'


class CompaundShips(models.Model):
    id = models.AutoField(primary_key=True)
    idship = models.ForeignKey(Ship, models.DO_NOTHING, db_column='idship', blank=True, null=True)
    idcompaund = models.ForeignKey(Compaund, models.DO_NOTHING, db_column='idcompaund', blank=True, null=True)
    captain = models.CharField(max_length=50, blank=True, null=True)
    losses = models.IntegerField(null=True)

    class Meta:
        db_table = 'Compaund ships'
        unique_together = (('idship', 'idcompaund'),)