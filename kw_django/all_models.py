# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class KwUserConfig(models.Model):
    user_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    created_at = models.DateField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'kw_user_config'
        unique_together = (('user_id', 'name'),)


class ModelHasPermissions(models.Model):
    permission_id = models.BigIntegerField(primary_key=True)
    model_type = models.CharField(max_length=255)
    model_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'model_has_permissions'
        unique_together = (('permission_id', 'model_id', 'model_type'),)


class ModelHasRoles(models.Model):
    role_id = models.BigIntegerField(primary_key=True)
    model_type = models.CharField(max_length=255)
    model_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'model_has_roles'
        unique_together = (('role_id', 'model_id', 'model_type'),)


class Nspaccounts(models.Model):
    accountno = models.CharField(primary_key=True, max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
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
    importdtime = models.DateField(blank=True, null=True)
    warrantymigrationstatus = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspaccounts'


class Nspaddresses(models.Model):
    addressid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
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
        db_table = 'nspaddresses'


class Nspaltparts(models.Model):
    partno = models.CharField(primary_key=True, max_length=40)
    altpartno = models.CharField(max_length=40)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    addedon = models.DateField(blank=True, null=True)
    removedon = models.DateField(blank=True, null=True)
    status = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nspaltparts'
        unique_together = (('partno', 'altpartno'),)


class NspautoroutingRoute(models.Model):
    apt_date = models.DateField(primary_key=True)
    warehouse_id = models.CharField(max_length=15)
    tech_id = models.IntegerField()
    order_no = models.CharField(max_length=15)
    travel_distance = models.DecimalField(max_digits=11, decimal_places=3, blank=True, null=True)
    travel_time = models.IntegerField(blank=True, null=True)
    working_time = models.IntegerField(blank=True, null=True)
    stop_number = models.IntegerField(blank=True, null=True)
    scheduled_at_dt = models.DateField(blank=True, null=True)
    created_at = models.DateField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    route_type = models.CharField(max_length=1)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspautorouting_route'
        unique_together = (('apt_date', 'warehouse_id', 'route_type', 'tech_id', 'order_no'),)


class NspautoroutingTech(models.Model):
    apt_date = models.DateField(primary_key=True)
    warehouse_id = models.CharField(max_length=15)
    tech_id = models.IntegerField()
    worktime_from = models.CharField(max_length=5, blank=True, null=True)
    worktime_to = models.CharField(max_length=5, blank=True, null=True)
    travel_distance = models.DecimalField(max_digits=11, decimal_places=3, blank=True, null=True)
    travel_time = models.IntegerField(blank=True, null=True)
    working_time = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)
    created_at = models.DateField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    route_type = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'nspautorouting_tech'
        unique_together = (('apt_date', 'warehouse_id', 'route_type', 'tech_id'),)


class Nspautoroutingdata(models.Model):
    aptdate = models.DateField(primary_key=True)
    warehouseid = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    request = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspautoroutingdata'
        unique_together = (('aptdate', 'warehouseid'),)


class Nspblockparts(models.Model):
    partno = models.CharField(primary_key=True, max_length=40)
    yearmonth = models.DateField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    usedrate = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspblockparts'
        unique_together = (('partno', 'yearmonth'),)


class Nspcallbacknos(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    ticketno = models.CharField(max_length=30)
    senton = models.DateField(blank=True, null=True)
    sentby = models.FloatField(blank=True, null=True)
    receivedon = models.DateField(blank=True, null=True)
    receivedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspcallbacknos'


class Nspclaimlogdetails(models.Model):
    logdetailid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    logid = models.FloatField()
    errorcode = models.CharField(max_length=20, blank=True, null=True)
    errortext = models.CharField(max_length=1000, blank=True, null=True)
    ignore = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspclaimlogdetails'


class Nspclaimlogs(models.Model):
    logid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    claimid = models.FloatField()
    seqno = models.FloatField()
    executetype = models.FloatField()
    result = models.FloatField()
    gspnwslogid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspclaimlogs'


class Nspcompanies(models.Model):
    companyid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    sname = models.CharField(unique=True, max_length=50)
    fname = models.CharField(unique=True, max_length=50)
    bizopentime = models.DateField(blank=True, null=True)
    bizclosetime = models.DateField(blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)
    alttel = models.CharField(max_length=20, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    timezone = models.CharField(max_length=3, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    firstname = models.CharField(max_length=30, blank=True, null=True)
    lastname = models.CharField(max_length=30, blank=True, null=True)
    isnsc = models.BooleanField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    companytype = models.FloatField(blank=True, null=True)
    coveredproduct = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspcompanies'


class Nspcompanycontacts(models.Model):
    contactid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
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

    class Meta:
        managed = False
        db_table = 'nspcompanycontacts'


class Nspconfigs(models.Model):
    code = models.CharField(primary_key=True, max_length=30)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=4000, blank=True, null=True)
    keyeditable = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspconfigs'


class Nspcoverages(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=15)
    zipcode = models.CharField(max_length=5)
    warehouseid = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'nspcoverages'
        unique_together = (('accountno', 'zipcode'),)


class Nspdatalogs(models.Model):
    nspdatalogid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    tablename = models.CharField(max_length=50)
    fieldname = models.CharField(max_length=50)
    key1 = models.CharField(max_length=50)
    key2 = models.CharField(max_length=50, blank=True, null=True)
    oldvalue = models.CharField(max_length=2000, blank=True, null=True)
    newvalue = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspdatalogs'


class Nspdefectcode(models.Model):
    code = models.CharField(primary_key=True, max_length=50)
    type = models.FloatField()
    description = models.CharField(max_length=510, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspdefectcode'
        unique_together = (('code', 'type'),)


class Nspdelayreasons(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.FloatField(blank=True, null=True)
    issqcode = models.BooleanField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspdelayreasons'


class Nspdocs(models.Model):
    opticketid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    docid = models.CharField(max_length=15)
    doctype = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspdocs'
        unique_together = (('opticketid', 'docid'),)


class Nspdoctypes(models.Model):
    doctype = models.CharField(primary_key=True, max_length=30)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspdoctypes'


class Nspdodetails(models.Model):
    dodetailid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
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
    isavailable = models.FloatField(blank=True, null=True)
    returnmessage = models.CharField(max_length=4000, blank=True, null=True)
    thirdpartyqty = models.FloatField(blank=True, null=True)
    invoiceitemno = models.FloatField(blank=True, null=True)
    grstatus = models.FloatField(blank=True, null=True)
    isofs = models.FloatField(blank=True, null=True)
    rcvqty = models.FloatField(blank=True, null=True)
    refno = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspdodetails'
        unique_together = (('doid', 'itemno'),)


class Nspdos(models.Model):
    doid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dodate = models.DateField(blank=True, null=True)
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
        db_table = 'nspdos'


class Nspengineercodes(models.Model):
    codeid = models.FloatField(primary_key=True)
    engineercode = models.CharField(max_length=30)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=15)
    userid = models.FloatField()
    status = models.FloatField()
    technicianid = models.CharField(max_length=30, blank=True, null=True)
    rcwarehouseid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspengineercodes'
        unique_together = (('accountno', 'userid'),)


class Nspflatratedetails(models.Model):
    flatratedetailid = models.FloatField(primary_key=True)
    flatrateid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    sealtype = models.FloatField()
    majortype = models.FloatField()
    rate = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nspflatratedetails'
        unique_together = (('flatrateid', 'sealtype', 'majortype'),)


class Nspflatrates(models.Model):
    flatrateid = models.FloatField(primary_key=True)
    vendorid = models.FloatField()
    periodstartdtime = models.DateField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    periodtype = models.FloatField()
    checkseal = models.FloatField()
    checkmajor = models.FloatField()
    accountno = models.CharField(max_length=15)
    isonlylaborrate = models.FloatField()
    partmarkuprate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspflatrates'
        unique_together = (('vendorid', 'accountno', 'periodstartdtime'),)


class Nspgspntechnicianids(models.Model):
    userid = models.FloatField(primary_key=True)
    accountno = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    vdeengineercode = models.CharField(max_length=30, blank=True, null=True)
    vdetechnicianid = models.CharField(max_length=30, blank=True, null=True)
    vdeorigin = models.FloatField()
    refengineercode = models.CharField(max_length=30, blank=True, null=True)
    reftechnicianid = models.CharField(max_length=30, blank=True, null=True)
    reforigin = models.FloatField()
    hkeengineercode = models.CharField(max_length=30, blank=True, null=True)
    hketechnicianid = models.CharField(max_length=30, blank=True, null=True)
    hkeorigin = models.FloatField()
    wsmengineercode = models.CharField(max_length=30, blank=True, null=True)
    wsmtechnicianid = models.CharField(max_length=30, blank=True, null=True)
    wsmorigin = models.FloatField()
    status = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nspgspntechnicianids'
        unique_together = (('userid', 'accountno'),)


class Nspgspnticketsaws(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    ticketid = models.FloatField()
    sawno = models.CharField(max_length=30, blank=True, null=True)
    sawcategory = models.FloatField()
    sawreason = models.FloatField(blank=True, null=True)
    submitdate = models.DateField(blank=True, null=True)
    inquiry = models.CharField(max_length=4000, blank=True, null=True)
    resolution = models.CharField(max_length=4000, blank=True, null=True)
    mileagedist = models.FloatField(blank=True, null=True)
    mileagedistconf = models.FloatField(blank=True, null=True)
    confirmamt = models.FloatField(blank=True, null=True)
    confirmuser = models.CharField(max_length=30, blank=True, null=True)
    confirmdtime = models.DateField(blank=True, null=True)
    confirmcomment = models.CharField(max_length=4000, blank=True, null=True)
    extrapersonlastname = models.CharField(max_length=30, blank=True, null=True)
    extrapersonfirstname = models.CharField(max_length=30, blank=True, null=True)
    sawstatus = models.FloatField(blank=True, null=True)
    statusdtime = models.DateField(blank=True, null=True)
    requestedvia = models.FloatField(blank=True, null=True)
    sawtype = models.FloatField(blank=True, null=True)
    errorcode = models.CharField(max_length=50, blank=True, null=True)
    evidencetypedesc = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspgspnticketsaws'


class Nspgspnwarrantyerrors(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    ticketid = models.FloatField()
    errorcode = models.CharField(max_length=10)
    errordescription = models.CharField(max_length=1000)
    errorstatus = models.CharField(max_length=100, blank=True, null=True)
    wersubmission = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspgspnwarrantyerrors'


class Nsphotparts(models.Model):
    partno = models.CharField(primary_key=True, max_length=40)
    warehouseid = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    keepqty = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsphotparts'
        unique_together = (('partno', 'warehouseid'),)


class Nsphotpartssm(models.Model):
    hotpartid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=15)
    day = models.DateField()
    partno = models.CharField(max_length=40)
    simulationseq = models.FloatField()
    usedqty = models.FloatField()
    assignedqty = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nsphotpartssm'


class Nspjobdetails(models.Model):
    jobdetailid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    jobid = models.FloatField()
    psid = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    executedby = models.FloatField(blank=True, null=True)
    executedon = models.DateField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspjobdetails'


class Nspjobs(models.Model):
    jobid = models.FloatField(primary_key=True)
    createdon = models.DateField()
    createdby = models.FloatField()
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    jobtype = models.FloatField()
    warehouseid = models.CharField(max_length=15)
    begindate = models.DateField(blank=True, null=True)
    orderedby = models.FloatField()
    orderedon = models.DateField()
    startedby = models.FloatField(blank=True, null=True)
    startedon = models.DateField(blank=True, null=True)
    completedby = models.FloatField(blank=True, null=True)
    completedon = models.DateField(blank=True, null=True)
    duedate = models.DateField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspjobs'


class Nsplocations(models.Model):
    warehouseid = models.CharField(primary_key=True, max_length=15)
    locationcode = models.CharField(max_length=25)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    locationtype = models.FloatField(blank=True, null=True)
    restricted = models.BooleanField(blank=True, null=True)
    collectdtime = models.DateField(blank=True, null=True)
    isnsc = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsplocations'
        unique_together = (('warehouseid', 'locationcode'),)


class Nspmailtemplates(models.Model):
    mailtemplateid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=4000, blank=True, null=True)
    emailsubject = models.CharField(max_length=255, blank=True, null=True)
    html = models.FloatField(blank=True, null=True)
    senderaddress = models.CharField(max_length=50, blank=True, null=True)
    sendername = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspmailtemplates'


class Nspmodeldoc4Tickets(models.Model):
    modelno = models.CharField(primary_key=True, max_length=25)
    docid = models.CharField(max_length=15)
    ticketid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspmodeldoc4tickets'
        unique_together = (('modelno', 'docid', 'ticketid'),)


class Nspmodeldocs(models.Model):
    modelno = models.CharField(primary_key=True, max_length=25)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    docid = models.CharField(max_length=15)
    doctype = models.CharField(max_length=30, blank=True, null=True)
    versions = models.CharField(max_length=50, blank=True, null=True)
    note = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspmodeldocs'
        unique_together = (('modelno', 'docid'),)


class Nspmytickets(models.Model):
    userid = models.FloatField(primary_key=True)
    opticketid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspmytickets'
        unique_together = (('userid', 'opticketid'),)


class Nspnscregister(models.Model):
    accountno = models.CharField(primary_key=True, max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    json = models.TextField()
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspnscregister'


class Nspoptimorouteaccounts(models.Model):
    warehouseid = models.CharField(primary_key=True, max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    loginid = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    apikey = models.CharField(max_length=100)
    status = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nspoptimorouteaccounts'


class Nspoptimoroutetechavailability(models.Model):
    warehouseid = models.CharField(primary_key=True, max_length=15)
    techid = models.FloatField()
    aptdate = models.DateField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    status = models.FloatField()
    starttime = models.CharField(max_length=4, blank=True, null=True)
    endtime = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspoptimoroutetechavailability'
        unique_together = (('warehouseid', 'techid', 'aptdate'),)


class Nsppartaccountcredit(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    creditdate = models.DateField()
    accountno = models.CharField(max_length=15)
    creditlimit = models.FloatField(blank=True, null=True)
    consumption = models.FloatField(blank=True, null=True)
    creditbalance = models.FloatField(blank=True, null=True)
    opensales = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartaccountcredit'
        unique_together = (('accountno', 'creditdate'),)


class Nsppartcreditlogs(models.Model):
    logid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    claimid = models.FloatField()
    psid = models.FloatField()
    billvalue = models.FloatField()
    billdate = models.DateField()
    creditvalue = models.FloatField()
    creditdate = models.DateField()

    class Meta:
        managed = False
        db_table = 'nsppartcreditlogs'


class Nsppartdetails(models.Model):
    partdetailid = models.FloatField(primary_key=True)
    opworkorderid = models.FloatField()
    partid = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    unitprice = models.FloatField(blank=True, null=True)
    refno = models.CharField(max_length=30, blank=True, null=True)
    isused = models.BooleanField(blank=True, null=True)
    fromlocation = models.CharField(max_length=15, blank=True, null=True)
    trackingno = models.CharField(max_length=35, blank=True, null=True)
    parteta = models.DateField(blank=True, null=True)
    isgspnsent = models.BooleanField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    partdesc = models.CharField(max_length=255, blank=True, null=True)
    usage = models.BooleanField(blank=True, null=True)
    priority = models.FloatField(blank=True, null=True)
    reverselocation = models.CharField(max_length=15, blank=True, null=True)
    reserverequired = models.BooleanField(blank=True, null=True)
    pono = models.CharField(max_length=25, blank=True, null=True)
    pickingbatchid = models.FloatField(blank=True, null=True)
    popartno = models.CharField(max_length=40, blank=True, null=True)
    reservestatus = models.FloatField(blank=True, null=True)
    poitemno = models.FloatField(blank=True, null=True)
    claimid = models.IntegerField(blank=True, null=True)
    claimdono = models.CharField(max_length=30, blank=True, null=True)
    defectserialno = models.CharField(max_length=35, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    psid = models.FloatField(blank=True, null=True)
    dostatus = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=100, blank=True, null=True)
    partetd = models.DateField(blank=True, null=True)
    warranty = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartdetails'


class Nsppartdetailsaudit(models.Model):
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
    isused = models.BooleanField(blank=True, null=True)
    fromlocation = models.CharField(max_length=15, blank=True, null=True)
    trackingno = models.CharField(max_length=35, blank=True, null=True)
    parteta = models.DateField(blank=True, null=True)
    isgspnsent = models.BooleanField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    partdesc = models.CharField(max_length=255, blank=True, null=True)
    usage = models.BooleanField(blank=True, null=True)
    reverselocation = models.CharField(max_length=15, blank=True, null=True)
    reserverequired = models.BooleanField(blank=True, null=True)
    pono = models.CharField(max_length=25, blank=True, null=True)
    pickingbatchid = models.FloatField(blank=True, null=True)
    popartno = models.CharField(max_length=40, blank=True, null=True)
    reservestatus = models.FloatField(blank=True, null=True)
    poitemno = models.FloatField(blank=True, null=True)
    priority = models.BooleanField(blank=True, null=True)
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
        db_table = 'nsppartdetailsaudit'


class Nsppartmaster4Warehouses(models.Model):
    partno = models.CharField(primary_key=True, max_length=40)
    warehouseid = models.CharField(max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    locationcode1 = models.CharField(max_length=25, blank=True, null=True)
    locationcode2 = models.CharField(max_length=25, blank=True, null=True)
    locationcode3 = models.CharField(max_length=25, blank=True, null=True)
    partaccountno = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'nsppartmaster4warehouses'
        unique_together = (('partno', 'warehouseid', 'partaccountno'),)


class Nsppartmasters(models.Model):
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
        db_table = 'nsppartmasters'


class Nsppartmsrp(models.Model):
    msrpid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=15)
    partno = models.CharField(max_length=40)
    msrp = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartmsrp'
        unique_together = (('accountno', 'partno'),)


class Nsppartretailprices(models.Model):
    retailpriceid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partno = models.CharField(unique=True, max_length=40)
    retailprice = models.FloatField()
    corebprice = models.FloatField(blank=True, null=True)
    fixedretailprice = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartretailprices'


class Nsppartserials(models.Model):
    psid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    indate = models.DateField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    corevalue = models.FloatField(blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    tolocationcode = models.CharField(max_length=25, blank=True, null=True)
    rano = models.CharField(max_length=30, blank=True, null=True)
    outdate = models.DateField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    outtrackingno = models.CharField(max_length=35, blank=True, null=True)
    pono = models.CharField(max_length=30, blank=True, null=True)
    workorderid = models.FloatField(blank=True, null=True)
    itemno = models.FloatField(blank=True, null=True)
    rareason = models.CharField(max_length=40, blank=True, null=True)
    radtime = models.DateField(blank=True, null=True)
    trackingno = models.CharField(max_length=30, blank=True, null=True)
    shipdate = models.DateField(blank=True, null=True)
    delivereddate = models.DateField(blank=True, null=True)
    creditdate = models.DateField(blank=True, null=True)
    rastatus = models.CharField(max_length=30, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    ranote = models.CharField(max_length=255, blank=True, null=True)
    raaccountno = models.CharField(max_length=30, blank=True, null=True)
    corerano = models.CharField(max_length=30, blank=True, null=True)
    locationdate = models.DateField(blank=True, null=True)
    surveydtime = models.DateField(blank=True, null=True)
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
    dodetailid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartserials'


class NsppartserialsSs(models.Model):
    psid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40)
    accountno = models.CharField(max_length=30)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dono = models.CharField(max_length=30)
    indate = models.DateField()
    value = models.FloatField()
    corevalue = models.FloatField(blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    tolocationcode = models.CharField(max_length=25, blank=True, null=True)
    rano = models.CharField(max_length=30, blank=True, null=True)
    outdate = models.DateField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    outtrackingno = models.CharField(max_length=35, blank=True, null=True)
    pono = models.CharField(max_length=30, blank=True, null=True)
    workorderid = models.FloatField(blank=True, null=True)
    itemno = models.FloatField(blank=True, null=True)
    rareason = models.CharField(max_length=40, blank=True, null=True)
    radtime = models.DateField(blank=True, null=True)
    trackingno = models.CharField(max_length=30, blank=True, null=True)
    shipdate = models.DateField(blank=True, null=True)
    delivereddate = models.DateField(blank=True, null=True)
    creditdate = models.DateField(blank=True, null=True)
    rastatus = models.CharField(max_length=30, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    ranote = models.CharField(max_length=255, blank=True, null=True)
    raaccountno = models.CharField(max_length=30, blank=True, null=True)
    corerano = models.CharField(max_length=225, blank=True, null=True)
    locationdate = models.DateField(blank=True, null=True)
    surveydtime = models.DateField(blank=True, null=True)
    surveyby = models.FloatField(blank=True, null=True)
    forvendorid = models.FloatField(blank=True, null=True)
    surveylocationcode = models.CharField(max_length=25, blank=True, null=True)
    isofs = models.FloatField(blank=True, null=True)
    snapshotmonth = models.DateField()
    jobdetailid = models.FloatField(blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    billdate = models.DateField(blank=True, null=True)
    billvalue = models.FloatField(blank=True, null=True)
    creditvalue = models.FloatField(blank=True, null=True)
    billstatus = models.FloatField(blank=True, null=True)
    corebilldate = models.DateField(blank=True, null=True)
    corecreditdate = models.DateField(blank=True, null=True)
    corebillstatus = models.FloatField(blank=True, null=True)
    radono = models.CharField(max_length=30, blank=True, null=True)
    claimid = models.FloatField(blank=True, null=True)
    invoicestatus = models.FloatField(blank=True, null=True)
    uploadid = models.CharField(max_length=20, blank=True, null=True)
    invoiceerrmsg = models.CharField(max_length=3000, blank=True, null=True)
    towarehouseid = models.CharField(max_length=15, blank=True, null=True)
    billdocno = models.CharField(max_length=30, blank=True, null=True)
    dodetailid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartserials_ss'
        unique_together = (('psid', 'snapshotmonth'),)


class Nsppartserialsaudit(models.Model):
    psid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=40, blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    indate = models.DateField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    corevalue = models.FloatField(blank=True, null=True)
    locationcode = models.CharField(max_length=25, blank=True, null=True)
    tolocationcode = models.CharField(max_length=25, blank=True, null=True)
    rano = models.CharField(max_length=30, blank=True, null=True)
    outdate = models.DateField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    outtrackingno = models.CharField(max_length=35, blank=True, null=True)
    pono = models.CharField(max_length=30, blank=True, null=True)
    workorderid = models.FloatField(blank=True, null=True)
    itemno = models.FloatField(blank=True, null=True)
    rareason = models.CharField(max_length=40, blank=True, null=True)
    radtime = models.DateField(blank=True, null=True)
    trackingno = models.CharField(max_length=30, blank=True, null=True)
    shipdate = models.DateField(blank=True, null=True)
    delivereddate = models.DateField(blank=True, null=True)
    creditdate = models.DateField(blank=True, null=True)
    rastatus = models.CharField(max_length=30, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    ranote = models.CharField(max_length=255, blank=True, null=True)
    raaccountno = models.CharField(max_length=30, blank=True, null=True)
    corerano = models.CharField(max_length=30, blank=True, null=True)
    locationdate = models.DateField(blank=True, null=True)
    surveydtime = models.DateField(blank=True, null=True)
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
        db_table = 'nsppartserialsaudit'


class Nsppartserialssm(models.Model):
    psid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=30)
    warehouseid = models.CharField(max_length=15)
    partno = models.CharField(max_length=40)
    dodate = models.DateField()
    indate = models.DateField(blank=True, null=True)
    outdate = models.DateField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=20)
    locationdate = models.DateField(blank=True, null=True)
    fromwarehouse = models.CharField(max_length=15, blank=True, null=True)
    towarehouse = models.CharField(max_length=15, blank=True, null=True)
    value = models.FloatField()
    corevalue = models.FloatField(blank=True, null=True)
    partdetailid = models.FloatField(blank=True, null=True)
    simulationseq = models.FloatField(blank=True, null=True)
    isofs = models.BooleanField(blank=True, null=True)
    rareason = models.CharField(max_length=3, blank=True, null=True)
    dodetailid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartserialssm'


class Nsppartserialssmaudit(models.Model):
    auditid = models.FloatField(primary_key=True)
    type = models.CharField(max_length=1)
    audittime = models.DateField()
    psid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=30)
    warehouseid = models.CharField(max_length=15)
    partno = models.CharField(max_length=40)
    dodate = models.DateField()
    indate = models.DateField(blank=True, null=True)
    outdate = models.DateField(blank=True, null=True)
    outtype = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=20)
    locationdate = models.DateField(blank=True, null=True)
    fromwarehouse = models.CharField(max_length=15, blank=True, null=True)
    towarehouse = models.CharField(max_length=15, blank=True, null=True)
    value = models.FloatField()
    corevalue = models.FloatField(blank=True, null=True)
    partdetailid = models.FloatField(blank=True, null=True)
    simulationseq = models.FloatField(blank=True, null=True)
    isofs = models.BooleanField(blank=True, null=True)
    rareason = models.CharField(max_length=3, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartserialssmaudit'


class Nsppartupdaterequests(models.Model):
    requestid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    psid = models.FloatField()
    requestedon = models.DateField()
    requestedby = models.FloatField()
    finalouttype = models.FloatField()
    remark = models.CharField(max_length=200, blank=True, null=True)
    confirmedon = models.DateField(blank=True, null=True)
    confirmedby = models.FloatField(blank=True, null=True)
    outno = models.CharField(max_length=30, blank=True, null=True)
    outdate = models.DateField(blank=True, null=True)
    status = models.FloatField()
    rejectreason = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppartupdaterequests'


class Nsppickingbatches(models.Model):
    batchid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    ticketcount = models.FloatField(blank=True, null=True)
    partcount = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppickingbatches'


class Nsppodetails(models.Model):
    podetailid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    poid = models.FloatField(blank=True, null=True)
    seqno = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=20, blank=True, null=True)
    shippedpartno = models.CharField(max_length=20, blank=True, null=True)
    partdescription = models.CharField(max_length=255, blank=True, null=True)
    qty = models.FloatField(blank=True, null=True)
    salesprice = models.FloatField(blank=True, null=True)
    salesamount = models.FloatField(blank=True, null=True)
    shippedqty = models.FloatField(blank=True, null=True)
    billingqty = models.FloatField(blank=True, null=True)
    etd = models.DateField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    popartno = models.CharField(max_length=22, blank=True, null=True)
    confirmno = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsppodetails'


class Nsppos(models.Model):
    poid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    accountno = models.CharField(max_length=30, blank=True, null=True)
    podate = models.DateField(blank=True, null=True)
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
        db_table = 'nsppos'


class Nsppsmovinghistories(models.Model):
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
        db_table = 'nsppsmovinghistories'


class Nsprepaircode(models.Model):
    code = models.CharField(primary_key=True, max_length=25)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nsprepaircode'
        unique_together = (('code', 'type'),)


class Nsprequiredparts(models.Model):
    requiredpartid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    modelno = models.CharField(max_length=30)
    periodstart = models.CharField(max_length=2)
    periodend = models.CharField(max_length=2)
    partno = models.CharField(max_length=40, blank=True, null=True)
    attentionmsg = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsprequiredparts'
        unique_together = (('modelno', 'periodstart', 'periodend', 'partno'),)


class Nsproutes(models.Model):
    routeid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
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
        db_table = 'nsproutes'


class Nspsamsungdefectcodes(models.Model):
    modelno = models.CharField(max_length=30)
    codedata = models.TextField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsamsungdefectcodes'


class Nspsamsungmodeldocuments(models.Model):
    opticketid = models.FloatField(primary_key=True)
    url = models.CharField(max_length=255)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    contenttype = models.CharField(max_length=15, blank=True, null=True)
    contentname = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    filesize = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsamsungmodeldocuments'
        unique_together = (('opticketid', 'url'),)


class Nspsamsungrepaircodes(models.Model):
    modelno = models.CharField(primary_key=True, max_length=30)
    codedata = models.TextField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsamsungrepaircodes'


class Nspsapinterfacelogs(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    interfacetype = models.FloatField()
    value = models.FloatField()
    refid = models.FloatField(blank=True, null=True)
    chargecode = models.FloatField()
    subchargecode = models.CharField(max_length=3, blank=True, null=True)
    uploadid = models.CharField(unique=True, max_length=20, blank=True, null=True)
    invoicestatus = models.FloatField()
    invoiceerrmsg = models.CharField(max_length=3000, blank=True, null=True)
    status = models.FloatField()
    creditmemoreason = models.CharField(max_length=255, blank=True, null=True)
    invoiceno = models.CharField(max_length=50, blank=True, null=True)
    refno = models.CharField(max_length=50, blank=True, null=True)
    donotupdate = models.FloatField(blank=True, null=True)
    logfileid = models.FloatField(blank=True, null=True)
    cmlogfileid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsapinterfacelogs'


class Nspsbaccounts(models.Model):
    sbaccountid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    vendorid = models.FloatField()
    companyid = models.CharField(max_length=20)
    userid = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    status = models.FloatField()
    accountno = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'nspsbaccounts'
        unique_together = (('companyid', 'userid'), ('vendorid', 'accountno'),)


class Nspsbtechnicianids(models.Model):
    accountno = models.CharField(primary_key=True, max_length=15)
    userid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    sbtechnicianid = models.CharField(max_length=30)
    status = models.FloatField()

    class Meta:
        managed = False
        db_table = 'nspsbtechnicianids'
        unique_together = (('accountno', 'userid'),)


class Nspschedules(models.Model):
    scheduleid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    systemid = models.FloatField(blank=True, null=True)
    userid = models.FloatField(blank=True, null=True)
    locationcode = models.CharField(max_length=30, blank=True, null=True)
    locationname = models.CharField(max_length=25, blank=True, null=True)
    locationcategory = models.CharField(max_length=10, blank=True, null=True)
    datefrom = models.DateField(blank=True, null=True)
    dateto = models.DateField(blank=True, null=True)
    note = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspschedules'


class Nspscsi(models.Model):
    zipcode = models.CharField(primary_key=True, max_length=10)
    grouping = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=3, blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspscsi'


class Nspsmstemplates(models.Model):
    smstemplateid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    subject = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    status = models.FloatField()
    expectedreplytype = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsmstemplates'


class Nspspaccounts(models.Model):
    spaccountid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    vendorid = models.FloatField()
    userid = models.CharField(max_length=40)
    password = models.CharField(max_length=40)
    svcracct = models.CharField(max_length=40)
    status = models.FloatField()
    accountno = models.CharField(max_length=40)

    class Meta:
        managed = False
        db_table = 'nspspaccounts'
        unique_together = (('vendorid', 'accountno'), ('accountno', 'userid'),)


class Nspsqls(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    subject = models.CharField(max_length=50, blank=True, null=True)
    sql = models.CharField(max_length=4000, blank=True, null=True)
    note = models.CharField(max_length=4000, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsqls'


class Nspstorecoveragedtls(models.Model):
    id = models.FloatField(primary_key=True)
    coverageid = models.FloatField()
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    ascno = models.CharField(max_length=30, blank=True, null=True)
    listorder = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspstorecoveragedtls'


class Nspstorecoverages(models.Model):
    coverageid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    storename = models.CharField(max_length=30, blank=True, null=True)
    storeno = models.CharField(max_length=10, blank=True, null=True)
    zipcode = models.CharField(max_length=5, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspstorecoverages'


class Nspsystemconfigs(models.Model):
    cd = models.CharField(primary_key=True, max_length=50)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspsystemconfigs'


class Nsptechincentives(models.Model):
    techincentiveid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    techid = models.FloatField()
    incentivetype = models.FloatField()
    incentivedate = models.DateField()
    paydate = models.DateField()
    incentiveworkorderid = models.FloatField()
    incentiveamount = models.FloatField()
    incentivestatus = models.FloatField()
    statusbyworkorderid = models.FloatField(blank=True, null=True)
    lastincentivestatus = models.FloatField(blank=True, null=True)
    updatedvia = models.FloatField(blank=True, null=True)
    statusreason = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsptechincentives'


class Nsptechincentivetier(models.Model):
    mitierid = models.FloatField(primary_key=True)
    mitiergroup = models.CharField(max_length=20)
    mitiergrade = models.CharField(max_length=2)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    startdistance = models.FloatField(blank=True, null=True)
    incentive = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsptechincentivetier'
        unique_together = (('mitiergroup', 'mitiergrade'),)


class Nsptechniciantiers(models.Model):
    techtierid = models.FloatField(primary_key=True)
    tiername = models.CharField(unique=True, max_length=20)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    seal = models.FloatField()
    iw_normal = models.FloatField()
    iw_ci = models.FloatField()
    iw_cis = models.FloatField()
    iw_dm = models.FloatField()
    iw_dpm = models.FloatField()
    iw_ex = models.FloatField()
    iw_pu = models.FloatField()
    iw_rc = models.FloatField()
    iw_sr = models.FloatField()
    oow_normal = models.FloatField()
    oow_ci = models.FloatField()
    oow_cis = models.FloatField()
    oow_dm = models.FloatField()
    oow_dpm = models.FloatField()
    oow_ex = models.FloatField()
    oow_pu = models.FloatField()
    oow_rc = models.FloatField()
    oow_sr = models.FloatField()
    status = models.FloatField()
    tub = models.FloatField(blank=True, null=True)
    walloven = models.FloatField(blank=True, null=True)
    dacor = models.FloatField()
    pm = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsptechniciantiers'


class Nsptempnos(models.Model):
    str = models.CharField(max_length=20, blank=True, null=True)
    int = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsptempnos'


class Nspticketstatushistory(models.Model):
    id = models.FloatField(primary_key=True)
    opid = models.FloatField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    nspstatus = models.FloatField(blank=True, null=True)
    startdtime = models.DateField(blank=True, null=True)
    finishdtime = models.DateField(blank=True, null=True)
    statusname = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspticketstatushistory'


class Nsptimeslots(models.Model):
    slotid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    zone = models.CharField(max_length=5, blank=True, null=True)
    fromdtime = models.DateField(blank=True, null=True)
    todtime = models.DateField(blank=True, null=True)
    slot = models.FloatField(blank=True, null=True)
    productcategory = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsptimeslots'


class Nsptriages(models.Model):
    triageid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    productcategory = models.CharField(max_length=50, blank=True, null=True)
    issuecategory = models.CharField(max_length=50, blank=True, null=True)
    note = models.CharField(max_length=4000, blank=True, null=True)
    companyid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nsptriages'


class Nspusers(models.Model):
    userid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    jobtype = models.FloatField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    nspstatus = models.FloatField(blank=True, null=True)
    iscallagent = models.BooleanField(blank=True, null=True)
    iscalltech = models.BooleanField(blank=True, null=True)
    isfieldtech = models.BooleanField(blank=True, null=True)
    isleadtech = models.BooleanField(blank=True, null=True)
    isclaimagent = models.BooleanField(blank=True, null=True)
    ismanager = models.BooleanField(blank=True, null=True)
    isfst = models.BooleanField(blank=True, null=True)
    isdis = models.BooleanField(blank=True, null=True)
    iswarehouse = models.BooleanField(blank=True, null=True)
    userstatus = models.FloatField(blank=True, null=True)
    statusdtime = models.DateField(blank=True, null=True)
    refrigeratorlevel = models.CharField(max_length=15, blank=True, null=True)
    sealsystemlevel = models.CharField(max_length=15, blank=True, null=True)
    washerlevel = models.CharField(max_length=15, blank=True, null=True)
    dryerlevel = models.CharField(max_length=15, blank=True, null=True)
    ovenlevel = models.CharField(max_length=15, blank=True, null=True)
    dishwasherlevel = models.CharField(max_length=15, blank=True, null=True)
    otrlevel = models.CharField(max_length=15, blank=True, null=True)
    dlptvlevel = models.CharField(max_length=15, blank=True, null=True)
    lcdtvlevel = models.CharField(max_length=15, blank=True, null=True)
    ledtvlevel = models.CharField(max_length=15, blank=True, null=True)
    origlocation = models.CharField(max_length=15, blank=True, null=True)
    curlocation = models.CharField(max_length=15, blank=True, null=True)
    totallevel = models.CharField(max_length=15, blank=True, null=True)
    pictureid = models.FloatField(blank=True, null=True)
    init = models.CharField(max_length=2, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)
    currentticketno = models.CharField(max_length=30, blank=True, null=True)
    samsungid = models.CharField(max_length=30, blank=True, null=True)
    iscompany = models.FloatField(blank=True, null=True)
    companyid = models.FloatField(blank=True, null=True)
    ismngrtech = models.BooleanField(blank=True, null=True)
    isremoteagent = models.FloatField(blank=True, null=True)
    engineercode = models.CharField(max_length=30, blank=True, null=True)
    islocationmanager = models.FloatField(blank=True, null=True)
    issupervisor = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    isnsc = models.FloatField(blank=True, null=True)
    tel = models.CharField(max_length=25, blank=True, null=True)
    techtierid = models.FloatField(blank=True, null=True)
    isnscmanager = models.BooleanField(blank=True, null=True)
    isslotmanager = models.BooleanField(blank=True, null=True)
    isregionalmanager = models.BooleanField(blank=True, null=True)
    techskillflags = models.FloatField(blank=True, null=True)
    endzipcode = models.CharField(max_length=5, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    remember_token = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspusers'


class Nspuserupdateschedule(models.Model):
    scheduleid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    userid = models.FloatField()
    updatetype = models.FloatField()
    updateto = models.CharField(max_length=15, blank=True, null=True)
    updatedate = models.DateField()
    status = models.FloatField()
    updatefrom = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspuserupdateschedule'
        unique_together = (('userid', 'updatetype', 'updatedate'),)


class Nspvalidareacodes(models.Model):
    areacode = models.CharField(primary_key=True, max_length=3)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspvalidareacodes'


class Nspwarehouseidmigration(models.Model):
    oldwarehouseid = models.CharField(primary_key=True, max_length=15)
    newwarehouseid = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'nspwarehouseidmigration'


class Nspwarehouses(models.Model):
    warehouseid = models.CharField(primary_key=True, max_length=15)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
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
        db_table = 'nspwarehouses'


class Nspzipcodes(models.Model):
    zipcode = models.CharField(primary_key=True, max_length=5)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    areacode = models.CharField(max_length=3, blank=True, null=True)
    county = models.CharField(max_length=30, blank=True, null=True)
    timezone = models.CharField(max_length=5, blank=True, null=True)
    dst = models.BooleanField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspzipcodes'


class Nspzones(models.Model):
    id = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    zipcode = models.CharField(max_length=5)
    productcategory = models.CharField(max_length=2)
    zone = models.CharField(max_length=1, blank=True, null=True)
    warehouseid = models.CharField(max_length=15)
    coordinatorid = models.IntegerField(blank=True, null=True)
    ampm = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nspzones'
        unique_together = (('warehouseid', 'zipcode', 'productcategory'),)


class OauthAccessTokens(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user_id = models.BigIntegerField(blank=True, null=True)
    client_id = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    scopes = models.CharField(max_length=1000, blank=True, null=True)
    revoked = models.BooleanField(blank=True, null=True)
    created_at = models.DateField(blank=True, null=True)
    updated_at = models.DateField(blank=True, null=True)
    expires_at = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oauth_access_tokens'


class OauthAuthCodes(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    user_id = models.BigIntegerField(blank=True, null=True)
    client_id = models.BigIntegerField(blank=True, null=True)
    scopes = models.CharField(max_length=1000, blank=True, null=True)
    revoked = models.BooleanField(blank=True, null=True)
    expires_at = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oauth_auth_codes'


class OauthRefreshTokens(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    access_token_id = models.CharField(max_length=100, blank=True, null=True)
    revoked = models.BooleanField(blank=True, null=True)
    expires_at = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oauth_refresh_tokens'


class Opbase(models.Model):
    id = models.FloatField(primary_key=True)
    pid = models.FloatField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    opdtime = models.DateField(blank=True, null=True)
    optype = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    originalpid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opbase'


class Opclaim(models.Model):
    id = models.FloatField(primary_key=True)
    claimnumber = models.CharField(max_length=50, blank=True, null=True)
    scheduledtime = models.DateField(blank=True, null=True)
    submitdtime = models.DateField(blank=True, null=True)
    partamount = models.FloatField(blank=True, null=True)
    laboramount = models.FloatField(blank=True, null=True)
    sawamount = models.FloatField(blank=True, null=True)
    otheramount = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=1000, blank=True, null=True)
    claimreceived = models.BooleanField(blank=True, null=True)
    claimstatus = models.FloatField(blank=True, null=True)
    claimtype = models.FloatField(blank=True, null=True)
    reviewcategory = models.CharField(max_length=30, blank=True, null=True)
    totalamount = models.FloatField(blank=True, null=True)
    samsungstatuscode = models.CharField(max_length=2, blank=True, null=True)
    billno = models.CharField(max_length=20, blank=True, null=True)
    syncdtime = models.DateField(blank=True, null=True)
    statusdtime = models.DateField(blank=True, null=True)
    submitby = models.IntegerField(blank=True, null=True)
    claimerror = models.CharField(max_length=255, blank=True, null=True)
    claimstatusnote = models.CharField(max_length=100, blank=True, null=True)
    acctstatus = models.FloatField(blank=True, null=True)
    creditedtotalamount = models.FloatField(blank=True, null=True)
    orgtotalamount = models.FloatField(blank=True, null=True)
    creditissuedate = models.DateField(blank=True, null=True)
    fiscaldate = models.DateField(blank=True, null=True)
    defecttype = models.FloatField(blank=True, null=True)
    creditedpartamount = models.FloatField(blank=True, null=True)
    creditedlaboramount = models.FloatField(blank=True, null=True)
    creditedsawamount = models.FloatField(blank=True, null=True)
    creditedotheramount = models.FloatField(blank=True, null=True)
    samsungstatus = models.FloatField(blank=True, null=True)
    freightamount = models.FloatField(blank=True, null=True)
    creditedfreightamount = models.FloatField(blank=True, null=True)
    defectcode = models.CharField(max_length=20, blank=True, null=True)
    defectsymptom = models.CharField(max_length=512, blank=True, null=True)
    repaircode = models.CharField(max_length=20, blank=True, null=True)
    repairaction = models.CharField(max_length=512, blank=True, null=True)
    engineercode = models.CharField(max_length=30, blank=True, null=True)
    technicianid = models.CharField(max_length=30, blank=True, null=True)
    completedtime = models.DateField(blank=True, null=True)
    delayreason = models.CharField(max_length=100, blank=True, null=True)
    repairtype = models.CharField(max_length=15, blank=True, null=True)
    donotinterface = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opclaim'


class Opclaimdetail(models.Model):
    detailid = models.FloatField(primary_key=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    claimid = models.FloatField(blank=True, null=True)
    ticketid = models.FloatField(blank=True, null=True)
    partno = models.CharField(max_length=100, blank=True, null=True)
    dono = models.CharField(max_length=30, blank=True, null=True)
    dodetailid = models.FloatField(blank=True, null=True)
    claimqty = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opclaimdetail'


class Opcontactcustomer(models.Model):
    id = models.FloatField(primary_key=True)
    scheduledtime = models.DateField(blank=True, null=True)
    startdtime = models.DateField(blank=True, null=True)
    finishdtime = models.DateField(blank=True, null=True)
    edireqdtime = models.DateField(blank=True, null=True)
    edisentdtime = models.DateField(blank=True, null=True)
    editried = models.FloatField(blank=True, null=True)
    logtype = models.FloatField(blank=True, null=True)
    iscxdissatisfied = models.BooleanField(blank=True, null=True)
    followupreason = models.CharField(max_length=500, blank=True, null=True)
    contactresult = models.FloatField(blank=True, null=True)
    satisfactionlevel = models.FloatField(blank=True, null=True)
    contactlog = models.CharField(max_length=4000, blank=True, null=True)
    triage = models.FloatField(blank=True, null=True)
    expectedreplytype = models.FloatField(blank=True, null=True)
    sid = models.CharField(max_length=50, blank=True, null=True)
    emailto = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opcontactcustomer'


class Opmail(models.Model):
    id = models.FloatField(primary_key=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=4000, blank=True, null=True)
    mailtype = models.FloatField(blank=True, null=True)
    printedon = models.DateField(blank=True, null=True)
    rptid = models.FloatField(blank=True, null=True)
    senderaddress = models.CharField(max_length=50, blank=True, null=True)
    sendername = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opmail'


class Opnote(models.Model):
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
        db_table = 'opnote'


class Opticket(models.Model):
    id = models.FloatField(primary_key=True)
    ticketno = models.CharField(unique=True, max_length=30)
    systemid = models.FloatField()
    issuedtime = models.DateField(blank=True, null=True)
    assigndtime = models.DateField(blank=True, null=True)
    firstcontactdtime = models.DateField(blank=True, null=True)
    contactscheduledtime = models.DateField(blank=True, null=True)
    aptstartdtime = models.DateField(blank=True, null=True)
    aptenddtime = models.DateField(blank=True, null=True)
    techid = models.FloatField(blank=True, null=True)
    completedtime = models.DateField(blank=True, null=True)
    contactid = models.FloatField(blank=True, null=True)
    contactid2 = models.FloatField(blank=True, null=True)
    modelno = models.CharField(max_length=30, blank=True, null=True)
    modelno2 = models.CharField(max_length=30, blank=True, null=True)
    serialno = models.CharField(max_length=50, blank=True, null=True)
    serialno2 = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    cancelreason = models.FloatField(blank=True, null=True)
    purchasedate = models.DateField(blank=True, null=True)
    purchasedate2 = models.DateField(blank=True, null=True)
    isticketrequested = models.BooleanField(blank=True, null=True)
    redoticketno = models.CharField(max_length=30, blank=True, null=True)
    redoreason = models.FloatField(blank=True, null=True)
    delayreason = models.CharField(max_length=100, blank=True, null=True)
    acknowledgedtime = models.DateField(blank=True, null=True)
    gspnstatus = models.BigIntegerField(blank=True, null=True)
    isgspncomplete = models.BooleanField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    lastworepairresult = models.FloatField(blank=True, null=True)
    version = models.CharField(max_length=15, blank=True, null=True)
    producttype = models.CharField(max_length=30, blank=True, null=True)
    productcategory = models.CharField(max_length=2, blank=True, null=True)
    angerindex = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=5, blank=True, null=True)
    dst = models.BooleanField(blank=True, null=True)
    warrantystatus = models.CharField(max_length=15, blank=True, null=True)
    partwterm = models.DateField(blank=True, null=True)
    laborwterm = models.DateField(blank=True, null=True)
    origpostingdtime = models.DateField(blank=True, null=True)
    nspdelayreason = models.CharField(max_length=50, blank=True, null=True)
    quedtime = models.DateField(blank=True, null=True)
    redobyticketno = models.CharField(max_length=30, blank=True, null=True)
    redobyticketissuedtime = models.DateField(blank=True, null=True)
    redobyreason = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    flag = models.BooleanField(blank=True, null=True)
    ascnumber = models.CharField(max_length=20, blank=True, null=True)
    manufacturemonth = models.CharField(max_length=20, blank=True, null=True)
    qosocsscore = models.FloatField(blank=True, null=True)
    wtyexception = models.CharField(max_length=50, blank=True, null=True)
    issueopendtime = models.DateField(blank=True, null=True)
    issueclosedtime = models.DateField(blank=True, null=True)
    issuenoteid = models.FloatField(blank=True, null=True)
    issuelatestid = models.FloatField(blank=True, null=True)
    issuestatus = models.FloatField(blank=True, null=True)
    servicetype = models.CharField(max_length=15, blank=True, null=True)
    nspstatus = models.FloatField(blank=True, null=True)
    nspstatusdtime = models.DateField(blank=True, null=True)
    socount = models.FloatField(blank=True, null=True)
    repeatcount = models.FloatField(blank=True, null=True)
    happycallfollowupdtime = models.DateField(blank=True, null=True)
    riskindex = models.FloatField(blank=True, null=True)
    urgent = models.BooleanField(blank=True, null=True)
    flowmenu = models.FloatField(blank=True, null=True)
    flowmenuexception = models.CharField(max_length=30, blank=True, null=True)
    acctonly = models.BooleanField(blank=True, null=True)
    accountno = models.CharField(max_length=20, blank=True, null=True)
    dplus1 = models.BooleanField(blank=True, null=True)
    requestapptdtime = models.DateField(blank=True, null=True)
    refno = models.CharField(max_length=20, blank=True, null=True)
    symptomcode1 = models.CharField(max_length=10, blank=True, null=True)
    symptomcode2 = models.CharField(max_length=10, blank=True, null=True)
    symptomcode3 = models.CharField(max_length=10, blank=True, null=True)
    symptomdescription1 = models.CharField(max_length=100, blank=True, null=True)
    symptomdescription2 = models.CharField(max_length=100, blank=True, null=True)
    symptomdescription3 = models.CharField(max_length=100, blank=True, null=True)
    repairscenario = models.CharField(max_length=4000, blank=True, null=True)
    ctatticketno = models.CharField(max_length=30, blank=True, null=True)
    ctatissuedtime = models.DateField(blank=True, null=True)
    ptatticketno = models.CharField(max_length=30, blank=True, null=True)
    ptatissuedtime = models.DateField(blank=True, null=True)
    psocount = models.FloatField(blank=True, null=True)
    pangerindex = models.FloatField(blank=True, null=True)
    issuegrade = models.FloatField(blank=True, null=True)
    firstapptdate = models.DateField(blank=True, null=True)
    prevticketdate = models.DateField(blank=True, null=True)
    firstdiagnoseby = models.FloatField(blank=True, null=True)
    firstcontactresult = models.BooleanField(blank=True, null=True)
    firstcontactsuccessdtime = models.DateField(blank=True, null=True)
    contactcountforsuccess = models.FloatField(blank=True, null=True)
    contacttotalcount = models.FloatField(blank=True, null=True)
    contacttotalsuccesscount = models.FloatField(blank=True, null=True)
    bizassigndtime = models.DateField(blank=True, null=True)
    firstrepairfailcode = models.FloatField(blank=True, null=True)
    agentid = models.FloatField(blank=True, null=True)
    origmodelno = models.CharField(max_length=30, blank=True, null=True)
    origserialno = models.CharField(max_length=50, blank=True, null=True)
    origversion = models.CharField(max_length=15, blank=True, null=True)
    origwarrantystatus = models.CharField(max_length=15, blank=True, null=True)
    firstaptmadedtime = models.DateField(blank=True, null=True)
    repaircompletedate = models.DateField(blank=True, null=True)
    firstassigndtime = models.DateField(blank=True, null=True)
    roappointmentfrom = models.CharField(max_length=20, blank=True, null=True)
    roappointmentto = models.CharField(max_length=20, blank=True, null=True)
    completedwt = models.BooleanField(blank=True, null=True)
    contactpreference = models.CharField(max_length=10, blank=True, null=True)
    requestdtime = models.DateField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    isscsi = models.BooleanField(blank=True, null=True)
    callfiredtime = models.DateField(blank=True, null=True)
    callfirestatus = models.FloatField(blank=True, null=True)
    rcreworktype = models.CharField(max_length=1, blank=True, null=True)
    lmomdaycount = models.FloatField(blank=True, null=True)
    isthd = models.FloatField(blank=True, null=True)
    smsconsent = models.FloatField(blank=True, null=True)
    dontcheckcall = models.FloatField(blank=True, null=True)
    attentioncode = models.FloatField(blank=True, null=True)
    riskcodeforclaim = models.FloatField(blank=True, null=True)
    istier2 = models.FloatField(blank=True, null=True)
    vendorid = models.FloatField(blank=True, null=True)
    alertmessage = models.CharField(max_length=4000, blank=True, null=True)
    servicecontractnumber = models.CharField(max_length=20, blank=True, null=True)
    followupcheckcall = models.FloatField(blank=True, null=True)
    targetdate = models.DateField(blank=True, null=True)
    labortype = models.FloatField(blank=True, null=True)
    gspnagentid = models.CharField(max_length=50, blank=True, null=True)
    isnsc = models.FloatField(blank=True, null=True)
    replacemodelno = models.CharField(max_length=30, blank=True, null=True)
    replaceserialno = models.CharField(max_length=50, blank=True, null=True)
    returntrackingno = models.CharField(max_length=35, blank=True, null=True)
    deliverytrackingno = models.CharField(max_length=35, blank=True, null=True)
    lastcallfireid = models.FloatField(blank=True, null=True)
    nscaccountno = models.CharField(max_length=15, blank=True, null=True)
    followupmessage = models.FloatField(blank=True, null=True)
    welcomesmsid = models.FloatField(blank=True, null=True)
    isjustbilling = models.BooleanField(blank=True, null=True)
    followuptype = models.FloatField(blank=True, null=True)
    msgtotech = models.CharField(max_length=1000, blank=True, null=True)
    purchasestore = models.CharField(max_length=100, blank=True, null=True)
    customertype = models.IntegerField(blank=True, null=True)
    emergencymessagetype = models.FloatField(blank=True, null=True)
    emergencymessagesenton = models.DateField(blank=True, null=True)
    emergencymessagecontactmethod = models.FloatField(blank=True, null=True)
    gspntechnicianid = models.CharField(max_length=30, blank=True, null=True)
    gspnengineercode = models.CharField(max_length=30, blank=True, null=True)
    minorredoticketno = models.CharField(max_length=30, blank=True, null=True)
    extwarrantycontractno = models.CharField(max_length=30, blank=True, null=True)
    defectcode = models.CharField(max_length=25, blank=True, null=True)
    defectsymptom = models.CharField(max_length=255, blank=True, null=True)
    hassexception = models.FloatField(blank=True, null=True)
    flags = models.FloatField(blank=True, null=True)
    billno = models.CharField(max_length=20, blank=True, null=True)
    lastsyncfromsystemdtime = models.DateField(blank=True, null=True)
    installationproblemtarget = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opticket'


class Opticketaudit(models.Model):
    id = models.FloatField()
    ticketno = models.CharField(max_length=30)
    systemid = models.FloatField()
    issuedtime = models.DateField(blank=True, null=True)
    assigndtime = models.DateField(blank=True, null=True)
    firstcontactdtime = models.DateField(blank=True, null=True)
    contactscheduledtime = models.DateField(blank=True, null=True)
    aptstartdtime = models.DateField(blank=True, null=True)
    aptenddtime = models.DateField(blank=True, null=True)
    techid = models.FloatField(blank=True, null=True)
    completedtime = models.DateField(blank=True, null=True)
    contactid = models.FloatField(blank=True, null=True)
    contactid2 = models.FloatField(blank=True, null=True)
    modelno = models.CharField(max_length=30, blank=True, null=True)
    modelno2 = models.CharField(max_length=30, blank=True, null=True)
    serialno = models.CharField(max_length=50, blank=True, null=True)
    serialno2 = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    cancelreason = models.FloatField(blank=True, null=True)
    purchasedate = models.DateField(blank=True, null=True)
    purchasedate2 = models.DateField(blank=True, null=True)
    isticketrequested = models.BooleanField(blank=True, null=True)
    redoticketno = models.CharField(max_length=30, blank=True, null=True)
    redoreason = models.FloatField(blank=True, null=True)
    delayreason = models.CharField(max_length=100, blank=True, null=True)
    acknowledgedtime = models.DateField(blank=True, null=True)
    gspnstatus = models.BigIntegerField(blank=True, null=True)
    isgspncomplete = models.BooleanField(blank=True, null=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    lastworepairresult = models.FloatField(blank=True, null=True)
    version = models.CharField(max_length=15, blank=True, null=True)
    producttype = models.CharField(max_length=30, blank=True, null=True)
    productcategory = models.CharField(max_length=2, blank=True, null=True)
    angerindex = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=5, blank=True, null=True)
    dst = models.BooleanField(blank=True, null=True)
    warrantystatus = models.CharField(max_length=15, blank=True, null=True)
    partwterm = models.DateField(blank=True, null=True)
    laborwterm = models.DateField(blank=True, null=True)
    origpostingdtime = models.DateField(blank=True, null=True)
    nspdelayreason = models.CharField(max_length=50, blank=True, null=True)
    quedtime = models.DateField(blank=True, null=True)
    redobyticketno = models.CharField(max_length=30, blank=True, null=True)
    redobyticketissuedtime = models.DateField(blank=True, null=True)
    redobyreason = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    flag = models.BooleanField(blank=True, null=True)
    ascnumber = models.CharField(max_length=20, blank=True, null=True)
    manufacturemonth = models.CharField(max_length=20, blank=True, null=True)
    qosocsscore = models.FloatField(blank=True, null=True)
    wtyexception = models.CharField(max_length=50, blank=True, null=True)
    issueopendtime = models.DateField(blank=True, null=True)
    issueclosedtime = models.DateField(blank=True, null=True)
    issuenoteid = models.FloatField(blank=True, null=True)
    issuelatestid = models.FloatField(blank=True, null=True)
    issuestatus = models.FloatField(blank=True, null=True)
    servicetype = models.CharField(max_length=15, blank=True, null=True)
    nspstatus = models.FloatField(blank=True, null=True)
    nspstatusdtime = models.DateField(blank=True, null=True)
    socount = models.FloatField(blank=True, null=True)
    repeatcount = models.FloatField(blank=True, null=True)
    happycallfollowupdtime = models.DateField(blank=True, null=True)
    riskindex = models.FloatField(blank=True, null=True)
    urgent = models.BooleanField(blank=True, null=True)
    flowmenu = models.FloatField(blank=True, null=True)
    flowmenuexception = models.CharField(max_length=30, blank=True, null=True)
    acctonly = models.BooleanField(blank=True, null=True)
    accountno = models.CharField(max_length=20, blank=True, null=True)
    dplus1 = models.BooleanField(blank=True, null=True)
    requestapptdtime = models.DateField(blank=True, null=True)
    refno = models.CharField(max_length=20, blank=True, null=True)
    symptomcode1 = models.CharField(max_length=10, blank=True, null=True)
    symptomcode2 = models.CharField(max_length=10, blank=True, null=True)
    symptomcode3 = models.CharField(max_length=10, blank=True, null=True)
    symptomdescription1 = models.CharField(max_length=100, blank=True, null=True)
    symptomdescription2 = models.CharField(max_length=100, blank=True, null=True)
    symptomdescription3 = models.CharField(max_length=100, blank=True, null=True)
    repairscenario = models.CharField(max_length=4000, blank=True, null=True)
    ctatticketno = models.CharField(max_length=30, blank=True, null=True)
    ctatissuedtime = models.DateField(blank=True, null=True)
    ptatticketno = models.CharField(max_length=30, blank=True, null=True)
    ptatissuedtime = models.DateField(blank=True, null=True)
    psocount = models.FloatField(blank=True, null=True)
    pangerindex = models.FloatField(blank=True, null=True)
    issuegrade = models.FloatField(blank=True, null=True)
    firstapptdate = models.DateField(blank=True, null=True)
    prevticketdate = models.DateField(blank=True, null=True)
    firstdiagnoseby = models.FloatField(blank=True, null=True)
    firstcontactresult = models.BooleanField(blank=True, null=True)
    firstcontactsuccessdtime = models.DateField(blank=True, null=True)
    contactcountforsuccess = models.FloatField(blank=True, null=True)
    contacttotalcount = models.FloatField(blank=True, null=True)
    contacttotalsuccesscount = models.FloatField(blank=True, null=True)
    bizassigndtime = models.DateField(blank=True, null=True)
    firstrepairfailcode = models.FloatField(blank=True, null=True)
    agentid = models.FloatField(blank=True, null=True)
    origmodelno = models.CharField(max_length=30, blank=True, null=True)
    origserialno = models.CharField(max_length=50, blank=True, null=True)
    origversion = models.CharField(max_length=15, blank=True, null=True)
    origwarrantystatus = models.CharField(max_length=15, blank=True, null=True)
    firstaptmadedtime = models.DateField(blank=True, null=True)
    repaircompletedate = models.DateField(blank=True, null=True)
    firstassigndtime = models.DateField(blank=True, null=True)
    roappointmentfrom = models.CharField(max_length=20, blank=True, null=True)
    roappointmentto = models.CharField(max_length=20, blank=True, null=True)
    completedwt = models.BooleanField(blank=True, null=True)
    contactpreference = models.CharField(max_length=10, blank=True, null=True)
    requestdtime = models.DateField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    isscsi = models.BooleanField(blank=True, null=True)
    callfiredtime = models.DateField(blank=True, null=True)
    callfirestatus = models.FloatField(blank=True, null=True)
    rcreworktype = models.CharField(max_length=1, blank=True, null=True)
    lmomdaycount = models.FloatField(blank=True, null=True)
    isthd = models.FloatField(blank=True, null=True)
    smsconsent = models.FloatField(blank=True, null=True)
    dontcheckcall = models.FloatField(blank=True, null=True)
    attentioncode = models.FloatField(blank=True, null=True)
    riskcodeforclaim = models.FloatField(blank=True, null=True)
    istier2 = models.FloatField(blank=True, null=True)
    vendorid = models.FloatField(blank=True, null=True)
    alertmessage = models.CharField(max_length=4000, blank=True, null=True)
    servicecontractnumber = models.CharField(max_length=20, blank=True, null=True)
    followupcheckcall = models.FloatField(blank=True, null=True)
    targetdate = models.DateField(blank=True, null=True)
    labortype = models.FloatField(blank=True, null=True)
    gspnagentid = models.CharField(max_length=50, blank=True, null=True)
    isnsc = models.FloatField(blank=True, null=True)
    replacemodelno = models.CharField(max_length=30, blank=True, null=True)
    replaceserialno = models.CharField(max_length=50, blank=True, null=True)
    returntrackingno = models.CharField(max_length=35, blank=True, null=True)
    deliverytrackingno = models.CharField(max_length=35, blank=True, null=True)
    lastcallfireid = models.FloatField(blank=True, null=True)
    nscaccountno = models.CharField(max_length=15, blank=True, null=True)
    followupmessage = models.FloatField(blank=True, null=True)
    welcomesmsid = models.FloatField(blank=True, null=True)
    isjustbilling = models.BooleanField(blank=True, null=True)
    followuptype = models.FloatField(blank=True, null=True)
    msgtotech = models.CharField(max_length=1000, blank=True, null=True)
    purchasestore = models.CharField(max_length=100, blank=True, null=True)
    customertype = models.IntegerField(blank=True, null=True)
    emergencymessagetype = models.FloatField(blank=True, null=True)
    emergencymessagesenton = models.DateField(blank=True, null=True)
    emergencymessagecontactmethod = models.FloatField(blank=True, null=True)
    gspntechnicianid = models.CharField(max_length=30, blank=True, null=True)
    gspnengineercode = models.CharField(max_length=30, blank=True, null=True)
    minorredoticketno = models.CharField(max_length=30, blank=True, null=True)
    extwarrantycontractno = models.CharField(max_length=30, blank=True, null=True)
    auditid = models.FloatField(primary_key=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    auditee = models.FloatField(blank=True, null=True)
    auditdtime = models.DateField(blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    completionscheduledtime = models.DateField(blank=True, null=True)
    completionscheduleby = models.FloatField(blank=True, null=True)
    defectcode = models.CharField(max_length=25, blank=True, null=True)
    defectsymptom = models.CharField(max_length=255, blank=True, null=True)
    hassexception = models.FloatField(blank=True, null=True)
    flags = models.FloatField(blank=True, null=True)
    billno = models.CharField(max_length=20, blank=True, null=True)
    lastsyncfromsystemdtime = models.DateField(blank=True, null=True)
    installationproblemtarget = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opticketaudit'


class Opworkorder(models.Model):
    id = models.FloatField(primary_key=True)
    workorderno = models.CharField(max_length=15, blank=True, null=True)
    aptstartdtime = models.DateField(blank=True, null=True)
    aptenddtime = models.DateField(blank=True, null=True)
    startdtime = models.DateField(blank=True, null=True)
    finishdtime = models.DateField(blank=True, null=True)
    contactid = models.FloatField(blank=True, null=True)
    technicianid = models.FloatField(blank=True, null=True)
    techniciannote = models.CharField(max_length=2000, blank=True, null=True)
    defectcode = models.CharField(max_length=25, blank=True, null=True)
    repaircode = models.CharField(max_length=25, blank=True, null=True)
    odometer = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=2000, blank=True, null=True)
    repairaction = models.CharField(max_length=512, blank=True, null=True)
    defectsymptom = models.CharField(max_length=512, blank=True, null=True)
    partcost = models.FloatField(blank=True, null=True)
    laborcost = models.FloatField(blank=True, null=True)
    othercost = models.FloatField(blank=True, null=True)
    salestax = models.FloatField(blank=True, null=True)
    checklist1 = models.BooleanField(blank=True, null=True)
    checklist2 = models.BooleanField(blank=True, null=True)
    checklist3 = models.BooleanField(blank=True, null=True)
    checklist4 = models.BooleanField(blank=True, null=True)
    ispartinfoclear = models.BooleanField(blank=True, null=True)
    warrantystatus = models.FloatField(blank=True, null=True)
    signaturedocid = models.CharField(max_length=15, blank=True, null=True)
    signedname = models.CharField(max_length=50, blank=True, null=True)
    finalworkorderdocid = models.CharField(max_length=15, blank=True, null=True)
    repairresultcode = models.FloatField(blank=True, null=True)
    paymenttype = models.FloatField(blank=True, null=True)
    diagnosedby = models.FloatField(blank=True, null=True)
    iscxdissatisfied = models.BooleanField(blank=True, null=True)
    ispartordered = models.BooleanField(blank=True, null=True)
    partorderby = models.FloatField(blank=True, null=True)
    repairfailcode = models.FloatField(blank=True, null=True)
    soprintdtime = models.DateField(blank=True, null=True)
    aptmadeby = models.FloatField(blank=True, null=True)
    aptmadedtime = models.DateField(blank=True, null=True)
    partorderdtime = models.DateField(blank=True, null=True)
    diagnosedtime = models.DateField(blank=True, null=True)
    triage = models.FloatField(blank=True, null=True)
    extraman = models.FloatField(blank=True, null=True)
    quoteby = models.FloatField(blank=True, null=True)
    quotedtime = models.DateField(blank=True, null=True)
    seallevel = models.FloatField(blank=True, null=True)
    seq = models.FloatField(blank=True, null=True)
    partwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    sqbox = models.CharField(max_length=15, blank=True, null=True)
    itsjobid = models.CharField(max_length=15, blank=True, null=True)
    reservecomplete = models.BooleanField(blank=True, null=True)
    partresearchby = models.FloatField(blank=True, null=True)
    partresearchdtime = models.DateField(blank=True, null=True)
    completelogid = models.FloatField(blank=True, null=True)
    reverseitsjobid = models.CharField(max_length=15, blank=True, null=True)
    routedistance = models.FloatField(blank=True, null=True)
    routeduration = models.FloatField(blank=True, null=True)
    routeid = models.FloatField(blank=True, null=True)
    installationtype = models.FloatField(blank=True, null=True)
    reminderemaildtime = models.DateField(blank=True, null=True)
    remindersmsdtime = models.DateField(blank=True, null=True)
    triagenote = models.CharField(max_length=2000, blank=True, null=True)
    originalticketid = models.FloatField(blank=True, null=True)
    isrescheduled = models.FloatField(blank=True, null=True)
    pendedon = models.DateField(blank=True, null=True)
    pendedby = models.FloatField(blank=True, null=True)
    unpendedon = models.DateField(blank=True, null=True)
    unpendedby = models.FloatField(blank=True, null=True)
    incentivestatus = models.FloatField(blank=True, null=True)
    incentive = models.FloatField(blank=True, null=True)
    msgtotech = models.CharField(max_length=1000, blank=True, null=True)
    msgconfirmdtime = models.DateField(blank=True, null=True)
    techassigntype = models.IntegerField(blank=True, null=True)
    rstartdtime = models.DateField(blank=True, null=True)
    renddtime = models.DateField(blank=True, null=True)
    paymenttransactionid = models.CharField(max_length=100, blank=True, null=True)
    ispartialwarranty = models.BooleanField(blank=True, null=True)
    smallsignaturedocid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opworkorder'


class Opworkorderaudit(models.Model):
    id = models.FloatField()
    workorderno = models.CharField(max_length=15, blank=True, null=True)
    aptstartdtime = models.DateField(blank=True, null=True)
    aptenddtime = models.DateField(blank=True, null=True)
    startdtime = models.DateField(blank=True, null=True)
    finishdtime = models.DateField(blank=True, null=True)
    contactid = models.FloatField(blank=True, null=True)
    technicianid = models.FloatField(blank=True, null=True)
    techniciannote = models.CharField(max_length=2000, blank=True, null=True)
    defectcode = models.CharField(max_length=25, blank=True, null=True)
    repaircode = models.CharField(max_length=25, blank=True, null=True)
    odometer = models.FloatField(blank=True, null=True)
    note = models.CharField(max_length=2000, blank=True, null=True)
    repairaction = models.CharField(max_length=512, blank=True, null=True)
    defectsymptom = models.CharField(max_length=512, blank=True, null=True)
    partcost = models.FloatField(blank=True, null=True)
    laborcost = models.FloatField(blank=True, null=True)
    othercost = models.FloatField(blank=True, null=True)
    salestax = models.FloatField(blank=True, null=True)
    checklist1 = models.BooleanField(blank=True, null=True)
    checklist2 = models.BooleanField(blank=True, null=True)
    checklist3 = models.BooleanField(blank=True, null=True)
    checklist4 = models.BooleanField(blank=True, null=True)
    ispartinfoclear = models.BooleanField(blank=True, null=True)
    warrantystatus = models.FloatField(blank=True, null=True)
    signaturedocid = models.CharField(max_length=15, blank=True, null=True)
    signedname = models.CharField(max_length=50, blank=True, null=True)
    finalworkorderdocid = models.CharField(max_length=15, blank=True, null=True)
    repairresultcode = models.FloatField(blank=True, null=True)
    paymenttype = models.FloatField(blank=True, null=True)
    diagnosedby = models.FloatField(blank=True, null=True)
    iscxdissatisfied = models.BooleanField(blank=True, null=True)
    ispartordered = models.BooleanField(blank=True, null=True)
    partorderby = models.FloatField(blank=True, null=True)
    repairfailcode = models.FloatField(blank=True, null=True)
    soprintdtime = models.DateField(blank=True, null=True)
    aptmadeby = models.FloatField(blank=True, null=True)
    aptmadedtime = models.DateField(blank=True, null=True)
    partorderdtime = models.DateField(blank=True, null=True)
    diagnosedtime = models.DateField(blank=True, null=True)
    triage = models.FloatField(blank=True, null=True)
    extraman = models.FloatField(blank=True, null=True)
    quoteby = models.FloatField(blank=True, null=True)
    quotedtime = models.DateField(blank=True, null=True)
    seallevel = models.FloatField(blank=True, null=True)
    seq = models.FloatField(blank=True, null=True)
    partwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    sqbox = models.CharField(max_length=15, blank=True, null=True)
    itsjobid = models.CharField(max_length=15, blank=True, null=True)
    reservecomplete = models.BooleanField(blank=True, null=True)
    partresearchby = models.FloatField(blank=True, null=True)
    partresearchdtime = models.DateField(blank=True, null=True)
    completelogid = models.FloatField(blank=True, null=True)
    reverseitsjobid = models.CharField(max_length=15, blank=True, null=True)
    routedistance = models.FloatField(blank=True, null=True)
    routeduration = models.FloatField(blank=True, null=True)
    routeid = models.FloatField(blank=True, null=True)
    installationtype = models.FloatField(blank=True, null=True)
    reminderemaildtime = models.DateField(blank=True, null=True)
    remindersmsdtime = models.DateField(blank=True, null=True)
    triagenote = models.CharField(max_length=2000, blank=True, null=True)
    originalticketid = models.FloatField(blank=True, null=True)
    isrescheduled = models.FloatField(blank=True, null=True)
    pendedon = models.DateField(blank=True, null=True)
    pendedby = models.FloatField(blank=True, null=True)
    unpendedon = models.DateField(blank=True, null=True)
    unpendedby = models.FloatField(blank=True, null=True)
    incentivestatus = models.FloatField(blank=True, null=True)
    incentive = models.FloatField(blank=True, null=True)
    msgtotech = models.CharField(max_length=1000, blank=True, null=True)
    msgconfirmdtime = models.DateField(blank=True, null=True)
    techassigntype = models.IntegerField(blank=True, null=True)
    rstartdtime = models.DateField(blank=True, null=True)
    renddtime = models.DateField(blank=True, null=True)
    auditid = models.FloatField(primary_key=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    auditee = models.FloatField(blank=True, null=True)
    auditdtime = models.DateField(blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    pid = models.FloatField(blank=True, null=True)
    paymenttransactionid = models.CharField(max_length=100, blank=True, null=True)
    ispartialwarranty = models.BooleanField(blank=True, null=True)
    smallsignaturedocid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'opworkorderaudit'


class QuestSlTempExplain1(models.Model):
    statement_id = models.CharField(max_length=30, blank=True, null=True)
    plan_id = models.FloatField(blank=True, null=True)
    timestamp = models.DateField(blank=True, null=True)
    remarks = models.CharField(max_length=4000, blank=True, null=True)
    operation = models.CharField(max_length=30, blank=True, null=True)
    options = models.CharField(max_length=255, blank=True, null=True)
    object_node = models.CharField(max_length=128, blank=True, null=True)
    object_owner = models.CharField(max_length=30, blank=True, null=True)
    object_name = models.CharField(max_length=30, blank=True, null=True)
    object_alias = models.CharField(max_length=65, blank=True, null=True)
    object_instance = models.BigIntegerField(blank=True, null=True)
    object_type = models.CharField(max_length=30, blank=True, null=True)
    optimizer = models.CharField(max_length=255, blank=True, null=True)
    search_columns = models.FloatField(blank=True, null=True)
    id = models.BigIntegerField(blank=True, null=True)
    parent_id = models.BigIntegerField(blank=True, null=True)
    depth = models.BigIntegerField(blank=True, null=True)
    position = models.BigIntegerField(blank=True, null=True)
    cost = models.BigIntegerField(blank=True, null=True)
    cardinality = models.BigIntegerField(blank=True, null=True)
    bytes = models.BigIntegerField(blank=True, null=True)
    other_tag = models.CharField(max_length=255, blank=True, null=True)
    partition_start = models.CharField(max_length=255, blank=True, null=True)
    partition_stop = models.CharField(max_length=255, blank=True, null=True)
    partition_id = models.BigIntegerField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)  # This field type is a guess.
    other_xml = models.TextField(blank=True, null=True)
    distribution = models.CharField(max_length=30, blank=True, null=True)
    cpu_cost = models.BigIntegerField(blank=True, null=True)
    io_cost = models.BigIntegerField(blank=True, null=True)
    temp_space = models.BigIntegerField(blank=True, null=True)
    access_predicates = models.CharField(max_length=4000, blank=True, null=True)
    filter_predicates = models.CharField(max_length=4000, blank=True, null=True)
    projection = models.CharField(max_length=4000, blank=True, null=True)
    time = models.BigIntegerField(blank=True, null=True)
    qblock_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'quest_sl_temp_explain1'


class Repairedworkorders(models.Model):
    id = models.FloatField(primary_key=True)
    workorderno = models.CharField(max_length=15, blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    completedtime = models.DateField(blank=True, null=True)
    type = models.FloatField(blank=True, null=True)
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    incentiveamount = models.FloatField(blank=True, null=True)
    nextpaydate = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'repairedworkorders'


class RoleHasPermissions(models.Model):
    permission_id = models.BigIntegerField(primary_key=True)
    role_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'role_has_permissions'
        unique_together = (('permission_id', 'role_id'),)


class Samsungmodeldocuments(models.Model):
    modelno = models.CharField(primary_key=True, max_length=30)
    documentdata = models.TextField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'samsungmodeldocuments'
