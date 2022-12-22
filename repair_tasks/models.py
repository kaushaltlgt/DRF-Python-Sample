from django.db import models

# Create your models here.

class NspRepairCode(models.Model):
    code = models.CharField(primary_key=True, max_length=25)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.FloatField()

    class Meta:
        managed = False
        db_table = 'NSPREPAIRCODE'
        unique_together = (('code', 'type'),)



class NspConfigs(models.Model):
    code = models.CharField(primary_key=True, max_length=30)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=4000, blank=True, null=True)
    keyeditable = models.SmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPCONFIGS'


class NspJobs(models.Model):
    jobid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField()
    createdby = models.FloatField()
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    jobtype = models.FloatField()
    warehouseid = models.CharField(max_length=15)
    begindate = models.DateTimeField(blank=True, null=True)
    orderedby = models.FloatField()
    orderedon = models.DateTimeField()
    startedby = models.FloatField(blank=True, null=True)
    startedon = models.DateTimeField(blank=True, null=True)
    completedby = models.FloatField(blank=True, null=True)
    completedon = models.DateTimeField(blank=True, null=True)
    duedate = models.DateField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPJOBS' 


class NspJobDetails(models.Model):
    jobdetailid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    jobid = models.FloatField()
    psid = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    executedby = models.FloatField(blank=True, null=True)
    executedon = models.DateTimeField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPJOBDETAILS'               