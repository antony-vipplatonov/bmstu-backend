from django.db import models


class Compaund(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    admiralname = models.CharField(max_length=50)
    country = models.CharField(max_length=50, blank=True, null=True)
    victory = models.IntegerField()
    status = models.CharField(max_length=1)
    creatorname = models.CharField(max_length=50)
    moderatorname = models.CharField(max_length=50)
    datacreate = models.DateField()
    dataform = models.DateField()
    dataend = models.DateField()

    class Meta:
        managed = False
        db_table = 'Compaund'


class CompaundShips(models.Model):
    idship = models.OneToOneField('Ship', models.DO_NOTHING, db_column='idship', primary_key=True)
    idcompaund = models.ForeignKey(Compaund, models.DO_NOTHING, db_column='idcompaund')
    captain = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Compaund ships'
        unique_together = (('idship', 'idcompaund'),)


class Ship(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    weapon = models.TextField()
    armoring = models.TextField()
    year = models.IntegerField()
    displacement = models.FloatField()
    length = models.FloatField()
    speed = models.FloatField()
    status = models.CharField(max_length=15)
    image = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ship'


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Users'

