from django.db import models
from django.db.models import fields

# Create your models here.

class NspPartDetails(models.Model):
    "to save part details data"
    partdetailid = models.IntegerField(primary_key=True) 
    opworkorderid = models.IntegerField() 
    partid = models.CharField(max_length=15)
    createdon = models.DateField(null=True, blank=True) 
    createdby = models.IntegerField(null=True, blank=True) 
    updatedon = models.DateField(null=True, blank=True) 
    updatedby = models.IntegerField(null=True, blank=True) 
    qty = models.IntegerField(null=True, blank=True) 
    unitprice = models.IntegerField(null=True, blank=True) 
    refno = models.CharField(max_length=30, null=True, blank=True) 
    isused = models.BooleanField(null=True, blank=True) 
    fromlocation = models.CharField(max_length=15, null=True, blank=True) 
    trackingno = models.CharField(max_length=35, null=True, blank=True) 
    parteta = models.DateField(null=True, blank=True) 
    isgspnsent = models.BooleanField(null=True, blank=True) 
    partno = models.CharField(max_length=40, null=True, blank=True) 
    partdesc = models.CharField(max_length=255, null=True, blank=True) 
    usage = models.BooleanField(null=True, blank=True) 
    priority = models.IntegerField(null=True, blank=True) 
    reverselocation = models.CharField(max_length=15, null=True, blank=True) 
    reserverequired = models.BooleanField(null=True, blank=True)
    pono = models.CharField(max_length=25,null=True, blank=True) 
    pickingbatchid = models.IntegerField(null=True, blank=True) 
    popartno = models.CharField(max_length=40,null=True, blank=True) 
    reservestatus = models.IntegerField(null=True, blank=True) 
    poitemno = models.IntegerField(null=True, blank=True) 
    claimid = models.IntegerField(null=True, blank=True)
    claimdono = models.CharField(max_length=30, null=True, blank=True) 
    defectserialno = models.CharField(max_length=35, null=True, blank=True) 
    dono = models.CharField(max_length=30, null=True, blank=True) 
    psid = models.IntegerField(null=True, blank=True) 
    dostatus = models.IntegerField(default=0,null=True, blank=True) 
    remark = models.CharField(max_length=100,null=True, blank=True) 
    partetd = models.DateField(null=True, blank=True) 
    warranty = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'NSPPARTDETAILS'


class NspPartDetailsAudit(models.Model):
    "to save part details audit data"
    auditid = models.FloatField(primary_key=True)
    type = models.CharField(max_length=1)
    auditee = models.FloatField()
    auditdtime = models.DateField()
    partdetailid = models.FloatField()
    opworkorderid = models.FloatField()
    partid = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    unitprice = models.FloatField(blank=True, null=True)
    refno = models.CharField(max_length=30, blank=True, null=True)
    isused = models.BooleanField(null=True, blank=True)
    fromlocation = models.CharField(max_length=15, blank=True, null=True)
    trackingno = models.CharField(max_length=35, blank=True, null=True)
    parteta = models.DateField(blank=True, null=True)
    isgspnsent = models.BooleanField(null=True, blank=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    partdesc = models.CharField(max_length=255, blank=True, null=True)
    usage = models.BooleanField(null=True, blank=True)
    reverselocation = models.CharField(max_length=15, blank=True, null=True)
    reserverequired = models.BooleanField(null=True, blank=True)
    pono = models.CharField(max_length=25, blank=True, null=True)
    pickingbatchid = models.FloatField(blank=True, null=True)
    popartno = models.CharField(max_length=40, blank=True, null=True)
    reservestatus = models.FloatField(blank=True, null=True)
    poitemno = models.FloatField(blank=True, null=True)
    priority = models.BooleanField(null=True, blank=True)
    claimid = models.IntegerField(blank=True, null=True)
    claimdono = models.CharField(max_length=30, blank=True, null=True)
    defectserialno = models.CharField(max_length=35, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    psid = models.FloatField(blank=True, null=True)
    dostatus = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    partetd = models.DateField(blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    warranty = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPARTDETAILSAUDIT'

class NspPartMasters(models.Model):
    "master table for parts"
    partno = models.CharField(primary_key=True, max_length=40)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partdescription = models.CharField(max_length=255)
    reserveexception = models.BooleanField(blank=True, null=True)
    orderexception = models.BooleanField(blank=True, null=True)
    billexception = models.BooleanField(blank=True, null=True)
    parttype = models.FloatField()
    reusable = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPARTMASTERS'        


def GetPartMaster(PartNo):
    "to check partno in NSPPARTMASTERS table"
    check_count = NspPartMasters.objects.filter(partno=PartNo).count()
    if check_count==0:
        return {'data':0}
    else:
        pm_data = NspPartMasters.objects.filter(partno=PartNo)[0]
        return {'data':pm_data}


class NspPartMaster4Warehouses(models.Model):
    partno = models.CharField(primary_key=True, max_length=40)
    warehouseid = models.CharField(max_length=15)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    locationcode1 = models.CharField(max_length=25, blank=True, null=True)
    locationcode2 = models.CharField(max_length=25, blank=True, null=True)
    locationcode3 = models.CharField(max_length=25, blank=True, null=True)
    partaccountno = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'NSPPARTMASTER4WAREHOUSES'
        unique_together = (('partno', 'warehouseid', 'partaccountno'),)        


class NspPartSerials(models.Model):
    "table for saving part serials"
    psid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    indate = models.DateTimeField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    corevalue = models.FloatField(blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    tolocationcode = models.CharField(max_length=25, blank=True, null=True)
    rano = models.CharField(max_length=30, blank=True, null=True)
    outdate = models.DateTimeField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    outtrackingno = models.CharField(max_length=35, blank=True, null=True)
    pono = models.CharField(max_length=30, blank=True, null=True)
    workorderid = models.FloatField(blank=True, null=True)
    itemno = models.FloatField(blank=True, null=True)
    rareason = models.CharField(max_length=40, blank=True, null=True)
    radtime = models.DateTimeField(blank=True, null=True)
    trackingno = models.CharField(max_length=30, blank=True, null=True)
    shipdate = models.DateTimeField(blank=True, null=True)
    delivereddate = models.DateTimeField(blank=True, null=True)
    creditdate = models.DateTimeField(blank=True, null=True)
    rastatus = models.CharField(max_length=30, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    ranote = models.CharField(max_length=255, blank=True, null=True)
    raaccountno = models.CharField(max_length=30, blank=True, null=True)
    corerano = models.CharField(max_length=30, blank=True, null=True)
    locationdate = models.DateField(blank=True, null=True)
    surveydtime = models.DateTimeField(blank=True, null=True)
    surveyby = models.FloatField(blank=True, null=True)
    forvendorid = models.FloatField(blank=True, null=True)
    isofs = models.BooleanField(blank=True, null=True)
    surveylocationcode = models.CharField(max_length=25, blank=True, null=True)
    jobdetailid = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    billdate = models.DateField(blank=True, null=True)
    billvalue = models.FloatField(blank=True, null=True)
    creditvalue = models.FloatField(blank=True, null=True)
    billstatus = models.FloatField(blank=True, null=True)
    corebilldate = models.DateField(blank=True, null=True)
    corecreditdate = models.DateField(blank=True, null=True)
    corebillstatus = models.FloatField(blank=True, null=True)
    claimid = models.FloatField(blank=True, null=True)
    radono = models.CharField(max_length=30, blank=True, null=True)
    towarehouseid = models.CharField(max_length=15, blank=True, null=True)
    billdocno = models.CharField(max_length=30, blank=True, null=True)
    dodetailid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPARTSERIALS'

class NspPartSerialsAudit(models.Model):
    "to save audit records for nsp part serials"
    psid = models.FloatField()
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    indate = models.DateTimeField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    corevalue = models.FloatField(blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    tolocationcode = models.CharField(max_length=25, blank=True, null=True)
    rano = models.CharField(max_length=30, blank=True, null=True)
    outdate = models.DateTimeField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    outtrackingno = models.CharField(max_length=35, blank=True, null=True)
    pono = models.CharField(max_length=30, blank=True, null=True)
    workorderid = models.FloatField(blank=True, null=True)
    itemno = models.FloatField(blank=True, null=True)
    rareason = models.CharField(max_length=40, blank=True, null=True)
    radtime = models.DateTimeField(blank=True, null=True)
    trackingno = models.CharField(max_length=30, blank=True, null=True)
    shipdate = models.DateTimeField(blank=True, null=True)
    delivereddate = models.DateTimeField(blank=True, null=True)
    creditdate = models.DateTimeField(blank=True, null=True)
    rastatus = models.CharField(max_length=30, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    ranote = models.CharField(max_length=255, blank=True, null=True)
    raaccountno = models.CharField(max_length=30, blank=True, null=True)
    corerano = models.CharField(max_length=30, blank=True, null=True)
    locationdate = models.DateField(blank=True, null=True)
    surveydtime = models.DateTimeField(blank=True, null=True)
    surveyby = models.FloatField(blank=True, null=True)
    forvendorid = models.FloatField(blank=True, null=True)
    isofs = models.FloatField(blank=True, null=True)
    surveylocationcode = models.CharField(max_length=25, blank=True, null=True)
    jobdetailid = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    billdate = models.DateField(blank=True, null=True)
    billvalue = models.FloatField(blank=True, null=True)
    creditvalue = models.FloatField(blank=True, null=True)
    billstatus = models.FloatField(blank=True, null=True)
    corebilldate = models.DateField(blank=True, null=True)
    corecreditdate = models.DateField(blank=True, null=True)
    corebillstatus = models.FloatField(blank=True, null=True)
    claimid = models.FloatField(blank=True, null=True)
    radono = models.CharField(max_length=30, blank=True, null=True)
    towarehouseid = models.CharField(max_length=15, blank=True, null=True)
    billdocno = models.CharField(max_length=30, blank=True, null=True)
    auditid = models.FloatField(primary_key=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    auditee = models.FloatField(blank=True, null=True)
    auditdtime = models.DateField(blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    dodetailid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPARTSERIALSAUDIT'                

class NspLocations(models.Model):
    "to store part locations data"
    warehouseid = models.CharField(max_length=15, primary_key=True) 
    locationcode = models.CharField(max_length=25) 
    createdon = models.DateField(null=True, blank=True) 
    createdby = models.IntegerField(null=True, blank=True) 
    updatedon = models.DateField(null=True, blank=True) 
    updatedby = models.IntegerField(null=True, blank=True) 
    locationtype = models.IntegerField(null=True, blank=True) 
    restricted = models.BooleanField(null=True, blank=True) 
    collectdtime = models.DateField(null=True, blank=True) 
    isnsc = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        unique_together = (('warehouseid', 'locationcode'),)
        db_table = 'NSPLOCATIONS'

class NspWareHouses(models.Model):
    warehouseid = models.CharField(primary_key=True, max_length=15)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    nickname = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=15, blank=True, null=True)
    longitude = models.CharField(max_length=15, blank=True, null=True)
    markeradjx = models.FloatField(blank=True, null=True)
    markeradjy = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=3, blank=True, null=True)
    dst = models.BooleanField(blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=25, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    partwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    sqboxes = models.CharField(max_length=4000, blank=True, null=True)
    btslocationcode = models.CharField(max_length=25, blank=True, null=True)
    usedlocationcode = models.CharField(max_length=25, blank=True, null=True)
    ralocationcode = models.CharField(max_length=25, blank=True, null=True)
    pickingblocklocations = models.CharField(max_length=4000, blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)
    itsmigration = models.BigIntegerField(blank=True, null=True)
    companyid = models.FloatField(blank=True, null=True)
    isactive = models.BooleanField(blank=True, null=True)
    sapcostcenter = models.CharField(max_length=10, blank=True, null=True)
    sapcontractno = models.CharField(max_length=12, blank=True, null=True)
    callfiretelno = models.CharField(max_length=10, blank=True, null=True)
    callfirebroadcastid = models.CharField(max_length=15, blank=True, null=True)
    mitiergroup = models.CharField(max_length=20, blank=True, null=True)
    hotparts = models.FloatField(blank=True, null=True)
    rdcwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    warehousetype = models.FloatField(blank=True, null=True)
    thirdpartyorderaccountno = models.CharField(max_length=15, blank=True, null=True)
    parttat = models.FloatField(blank=True, null=True)
    extrafirstname = models.CharField(max_length=50, blank=True, null=True)
    extralastname = models.CharField(max_length=50, blank=True, null=True)
    timedifference = models.FloatField(blank=True, null=True)
    note4so1 = models.CharField(max_length=100, blank=True, null=True)
    note4so2 = models.CharField(max_length=2000, blank=True, null=True)
    extraman = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPWAREHOUSES'


class NspPSMovingHistories(models.Model):
    pshistoryid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    psid = models.FloatField()
    fromwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    fromlocationcode = models.CharField(max_length=25, blank=True, null=True)
    towarehouseid = models.CharField(max_length=15)
    tolocationcode = models.CharField(max_length=25)
    workorderid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPSMOVINGHISTORIES'                                


class DocFolders(models.Model):
    docid = models.CharField(primary_key=True, max_length=15)
    foldername = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DOCFOLDERS'


class DocNodes(models.Model):
    pdocid = models.CharField(max_length=255)
    nodetype = models.FloatField(blank=True, null=True)
    nodename = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)
    docid = models.CharField(primary_key=True, max_length=255)
    status = models.IntegerField(blank=True, null=True)
    systemid = models.IntegerField(blank=True, null=True)
    idtype = models.IntegerField(blank=True, null=True)
    isprivate = models.BooleanField(blank=True, null=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DOCNODES'


class DocFiles(models.Model):
    docid = models.OneToOneField('Docnodes', models.DO_NOTHING, db_column='docid', primary_key=True)
    filename = models.CharField(max_length=255, blank=True, null=True)
    ext = models.CharField(max_length=5, blank=True, null=True)
    ocr = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DOCFILES'


class NspDocs(models.Model):
    opticketid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    docid = models.CharField(max_length=15)
    doctype = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPDOCS'
        unique_together = (('opticketid', 'docid'),)


class OpNote(models.Model):
    id = models.FloatField(primary_key=True)
    scheduledtime = models.DateField(blank=True, null=True)
    delayreason1 = models.CharField(max_length=50, blank=True, null=True)
    delayreason2 = models.CharField(max_length=50, blank=True, null=True)
    delayreason3 = models.CharField(max_length=50, blank=True, null=True)
    redobyticketno = models.CharField(max_length=30, blank=True, null=True)
    redobyticketissuedtime = models.DateField(blank=True, null=True)
    redoreason = models.CharField(max_length=50, blank=True, null=True)
    qosrtsscore = models.FloatField(blank=True, null=True)
    qosrrsscore = models.FloatField(blank=True, null=True)
    qosocsscore = models.FloatField(blank=True, null=True)
    qosdate = models.DateField(blank=True, null=True)
    note = models.CharField(max_length=4000, blank=True, null=True)
    notetype = models.FloatField(blank=True, null=True)
    refno = models.CharField(max_length=30, blank=True, null=True)
    reviewnote = models.CharField(max_length=1000, blank=True, null=True)
    mailto = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OPNOTE' 


class NspAccounts(models.Model):
    "to save account information"
    accountno = models.CharField(primary_key=True, max_length=15)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountname = models.CharField(max_length=30, blank=True, null=True)
    type = models.FloatField(blank=True, null=True)
    partaccountno = models.CharField(max_length=15, blank=True, null=True)
    groupaccountno = models.CharField(max_length=15, blank=True, null=True)
    adminaccountno = models.CharField(max_length=15, blank=True, null=True)
    itscompanyid = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    isdplus1 = models.BooleanField(blank=True, null=True)
    partaccountname = models.CharField(max_length=30, blank=True, null=True)
    isotb = models.FloatField(blank=True, null=True)
    callfiretelno = models.CharField(max_length=10, blank=True, null=True)
    callfirebroadcastid = models.CharField(max_length=15, blank=True, null=True)
    weekendcallfire = models.FloatField(blank=True, null=True)
    extaccountno = models.CharField(max_length=20, blank=True, null=True)
    nsccedispatchaccount = models.CharField(max_length=15, blank=True, null=True)
    nschadispatchaccount = models.CharField(max_length=15, blank=True, null=True)
    isnsc = models.FloatField(blank=True, null=True)
    contactid = models.FloatField(blank=True, null=True)
    importdtime = models.DateTimeField(blank=True, null=True)
    warrantymigrationstatus = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPACCOUNTS'


class NspDoDetails(models.Model):
    "to save DO details data"
    dodetailid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    doid = models.FloatField(blank=True, null=True)
    itemno = models.FloatField(blank=True, null=True)
    pono = models.CharField(max_length=30, blank=True, null=True)
    partno = models.CharField(max_length=20, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    total = models.FloatField(blank=True, null=True)
    corevalue = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    schqty = models.FloatField(blank=True, null=True)
    poitemno = models.FloatField(blank=True, null=True)
    closeqty = models.IntegerField(blank=True, null=True)
    claimqty = models.FloatField(blank=True, null=True)
    raqty = models.FloatField(blank=True, null=True)
    isavailable = models.BooleanField(blank=True, null=True)
    returnmessage = models.CharField(max_length=4000, blank=True, null=True)
    thirdpartyqty = models.FloatField(blank=True, null=True)
    invoiceitemno = models.FloatField(blank=True, null=True)
    grstatus = models.FloatField(blank=True, null=True)
    isofs = models.FloatField(blank=True, null=True)
    rcvqty = models.FloatField(blank=True, null=True)
    refno = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPDODETAILS'
        unique_together = (('doid', 'itemno'),)


class NspDos(models.Model):
    "to save DOs data"
    doid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dodate = models.DateTimeField(blank=True, null=True)
    dono = models.CharField(unique=True, max_length=30, blank=True, null=True)
    refno = models.CharField(max_length=30, blank=True, null=True)
    itemqty = models.FloatField(blank=True, null=True)
    totalqty = models.FloatField(blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    shipmentid = models.CharField(max_length=15, blank=True, null=True)
    eta = models.DateField(blank=True, null=True)
    trackingno = models.CharField(max_length=30, blank=True, null=True)
    seller = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPDOS'

class NspCompanyContacts(models.Model):
    "to save company contact information"
    contactid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    companyid = models.FloatField(blank=True, null=True)
    contacttype = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=80, blank=True, null=True)
    tel = models.CharField(max_length=25, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    addressid = models.FloatField(blank=True, null=True)
    alttel = models.CharField(max_length=25, blank=True, null=True)
    mobile = models.CharField(max_length=25, blank=True, null=True)

    def return_null_value(self):
        "returns None for empty string values"
        if self.name=='':
            return None
        if self.tel=='':
            return None
        if self.fax=='':
            return None
        if self.email=='':
            return None
        if self.alttel=='':
            return None
        if self.mobile=='':
            return None                    

    class Meta:
        managed = False
        db_table = 'NSPCOMPANYCONTACTS'


class NspAddresses(models.Model):
    "to save nsp addresses"
    addressid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=3, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    category = models.CharField(max_length=10, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    geotype = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPADDRESSES'



class NspPos(models.Model):
    "save data for nsp pos"
    poid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    podate = models.DateTimeField(blank=True, null=True)
    pono = models.CharField(unique=True, max_length=30, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    itemqty = models.FloatField(blank=True, null=True)
    confirmno = models.CharField(max_length=20, blank=True, null=True)
    totalqty = models.FloatField(blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    shipto = models.CharField(max_length=30, blank=True, null=True)
    forvendorid = models.FloatField(blank=True, null=True)
    isofs = models.FloatField(blank=True, null=True)
    seller = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPPOS'


class NspHotParts(models.Model):
    partno = models.CharField(primary_key=True, max_length=40)
    warehouseid = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    keepqty = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPHOTPARTS'
        unique_together = (('partno', 'warehouseid'),)                                                                                              

