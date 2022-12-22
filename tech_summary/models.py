from django.db import models


class NspRoutes(models.Model):
    routeid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    technicianid = models.FloatField(blank=True, null=True)
    routedate = models.DateField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    socount = models.FloatField(blank=True, null=True)
    solist = models.CharField(max_length=300, blank=True, null=True)
    polylinepoints = models.CharField(max_length=4000, blank=True, null=True)
    googlejson = models.TextField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPROUTES'

class AndroidDevices(models.Model):
    appid = models.CharField(primary_key=True, max_length=64)
    deviceid = models.CharField(max_length=64)
    devicename = models.CharField(max_length=64, blank=True, null=True)
    deviceversion = models.CharField(max_length=64, blank=True, null=True)
    devicemodel = models.CharField(max_length=64, blank=True, null=True)
    deviceserial = models.CharField(max_length=64, blank=True, null=True)
    remoteuser = models.CharField(max_length=255, blank=True, null=True)
    remoteaddr = models.CharField(max_length=255, blank=True, null=True)
    useragent = models.CharField(max_length=255, blank=True, null=True)
    registrationid = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    createdon = models.DateTimeField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ANDROIDDEVICES'
        unique_together = (('appid', 'deviceid'),)        




