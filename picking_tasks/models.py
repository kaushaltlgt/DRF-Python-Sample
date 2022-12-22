from django.db import models

# Create your models here.

class NspPickingBatches(models.Model):
    "save picking batches data"
    batchid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    ticketcount = models.FloatField(blank=True, null=True)
    partcount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPICKINGBATCHES'
