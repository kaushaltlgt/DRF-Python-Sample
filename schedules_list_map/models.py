from django.db import models

# Create your models here.

class GSPNWSLOGS(models.Model):
    "to save logs from function startlog"
    id = models.IntegerField(primary_key=True)
    createdon = models.DateField(null=True, blank=True)
    createdby = models.IntegerField(null=True, blank=True)
    updatedon = models.DateField(null=True, blank=True)
    updatedby = models.IntegerField(null=True, blank=True)
    refno = models.CharField(max_length=30, null=True, blank=True)
    method = models.CharField(max_length=100, null=True, blank=True)
    callelapse = models.IntegerField(null=True, blank=True)
    errorcode = models.CharField(max_length=10, null=True, blank=True) 
    errormsg = models.CharField(max_length=255, null=True, blank=True)
    caller = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'GSPNWSLOGS'

class SQAPILogs(models.Model):
    "to save logs generated from the class SQAPIClient"
    id = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    refno = models.CharField(max_length=50, blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    callelapse = models.IntegerField(blank=True, null=True)
    errorcode = models.CharField(max_length=10, blank=True, null=True)
    errormsg = models.CharField(max_length=255, blank=True, null=True)
    caller = models.CharField(max_length=100, blank=True, null=True)
    server = models.CharField(max_length=50, blank=True, null=True)
    callerapp = models.FloatField(blank=True, null=True)
    appversion = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SQAPILOGS'


class NspDataLogs(models.Model):
    "to save logs"
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
        db_table = 'NSPDATALOGS'                


class NspDefectCode(models.Model):
    "nsp defect codes"
    code = models.CharField(primary_key=True, max_length=50)
    type = models.FloatField()
    description = models.CharField(max_length=510, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPDEFECTCODE'
        unique_together = (('code', 'type'),)


class NspSamsungDefectCodes(models.Model):
    "nsp defect codes for Samsung"
    modelno = models.CharField(max_length=30, primary_key=True)
    codedata = models.TextField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPSAMSUNGDEFECTCODES'

class NspRepairCode(models.Model):
    "nsp repair codes"
    code = models.CharField(primary_key=True, max_length=25)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.FloatField()

    class Meta:
        managed = False
        db_table = 'NSPREPAIRCODE'
        unique_together = (('code', 'type'),)


class NspSamsungRepairCodes(models.Model):
    "nsp samsung repair codes"
    modelno = models.CharField(primary_key=True, max_length=30)
    codedata = models.TextField(blank=True, null=True)
    createdon = models.DateField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NSPSAMSUNGREPAIRCODES'                               


class OpBase(models.Model):
    id = models.FloatField(primary_key=True)
    pid = models.FloatField(blank=True, null=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.FloatField(blank=True, null=True)
    opdtime = models.DateTimeField(blank=True, null=True)
    optype = models.FloatField(blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    originalpid = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OPBASE'		


class OpContactCustomer(models.Model):
    id = models.FloatField(primary_key=True)
    scheduledtime = models.DateTimeField(blank=True, null=True)
    startdtime = models.DateTimeField(blank=True, null=True)
    finishdtime = models.DateTimeField(blank=True, null=True)
    edireqdtime = models.DateTimeField(blank=True, null=True)
    edisentdtime = models.DateTimeField(blank=True, null=True)
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
        db_table = 'OPCONTACTCUSTOMER'        

class OpTicket(models.Model):
    id = models.FloatField(primary_key=True)
    ticketno = models.CharField(unique=True, max_length=30)
    systemid = models.FloatField()
    issuedtime = models.DateTimeField(blank=True, null=True)
    assigndtime = models.DateTimeField(blank=True, null=True)
    firstcontactdtime = models.DateTimeField(blank=True, null=True)
    contactscheduledtime = models.DateTimeField(blank=True, null=True)
    aptstartdtime = models.DateTimeField(blank=True, null=True)
    aptenddtime = models.DateTimeField(blank=True, null=True)
    techid = models.FloatField(blank=True, null=True)
    completedtime = models.DateTimeField(blank=True, null=True)
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
    isticketrequested = models.BooleanField(null=True, blank=True)
    redoticketno = models.CharField(max_length=30, blank=True, null=True)
    redoreason = models.FloatField(blank=True, null=True)
    delayreason = models.CharField(max_length=100, blank=True, null=True)
    acknowledgedtime = models.DateTimeField(blank=True, null=True)
    gspnstatus = models.BigIntegerField(blank=True, null=True)
    isgspncomplete = models.BooleanField(null=True, blank=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    lastworepairresult = models.FloatField(blank=True, null=True)
    version = models.CharField(max_length=15, blank=True, null=True)
    producttype = models.CharField(max_length=30, blank=True, null=True)
    productcategory = models.CharField(max_length=2, blank=True, null=True)
    angerindex = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=5, blank=True, null=True)
    dst = models.BooleanField(null=True, blank=True)
    warrantystatus = models.CharField(max_length=15, blank=True, null=True)
    partwterm = models.DateField(blank=True, null=True)
    laborwterm = models.DateField(blank=True, null=True)
    origpostingdtime = models.DateTimeField(blank=True, null=True)
    nspdelayreason = models.CharField(max_length=50, blank=True, null=True)
    quedtime = models.DateField(blank=True, null=True)
    redobyticketno = models.CharField(max_length=30, blank=True, null=True)
    redobyticketissuedtime = models.DateTimeField(blank=True, null=True)
    redobyreason = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    flag = models.BooleanField(null=True, blank=True)
    ascnumber = models.CharField(max_length=20, blank=True, null=True)
    manufacturemonth = models.CharField(max_length=20, blank=True, null=True)
    qosocsscore = models.FloatField(blank=True, null=True)
    wtyexception = models.CharField(max_length=50, blank=True, null=True)
    issueopendtime = models.DateTimeField(blank=True, null=True)
    issueclosedtime = models.DateTimeField(blank=True, null=True)
    issuenoteid = models.FloatField(blank=True, null=True)
    issuelatestid = models.FloatField(blank=True, null=True)
    issuestatus = models.FloatField(blank=True, null=True)
    servicetype = models.CharField(max_length=15, blank=True, null=True)
    nspstatus = models.FloatField(blank=True, null=True)
    nspstatusdtime = models.DateTimeField(blank=True, null=True)
    socount = models.FloatField(blank=True, null=True)
    repeatcount = models.FloatField(blank=True, null=True)
    happycallfollowupdtime = models.DateTimeField(blank=True, null=True)
    riskindex = models.FloatField(blank=True, null=True)
    urgent = models.BooleanField(null=True, blank=True)
    flowmenu = models.FloatField(blank=True, null=True)
    flowmenuexception = models.CharField(max_length=30, blank=True, null=True)
    acctonly = models.BooleanField(null=True, blank=True)
    accountno = models.CharField(max_length=20, blank=True, null=True)
    dplus1 = models.BooleanField(null=True, blank=True)
    requestapptdtime = models.DateTimeField(blank=True, null=True)
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
    firstcontactresult = models.BooleanField(null=True, blank=True)
    firstcontactsuccessdtime = models.DateTimeField(blank=True, null=True)
    contactcountforsuccess = models.FloatField(blank=True, null=True)
    contacttotalcount = models.FloatField(blank=True, null=True)
    contacttotalsuccesscount = models.FloatField(blank=True, null=True)
    bizassigndtime = models.DateTimeField(blank=True, null=True)
    firstrepairfailcode = models.FloatField(blank=True, null=True)
    agentid = models.FloatField(blank=True, null=True)
    origmodelno = models.CharField(max_length=30, blank=True, null=True)
    origserialno = models.CharField(max_length=50, blank=True, null=True)
    origversion = models.CharField(max_length=15, blank=True, null=True)
    origwarrantystatus = models.CharField(max_length=15, blank=True, null=True)
    firstaptmadedtime = models.DateTimeField(blank=True, null=True)
    repaircompletedate = models.DateField(blank=True, null=True)
    firstassigndtime = models.DateTimeField(blank=True, null=True)
    roappointmentfrom = models.CharField(max_length=20, blank=True, null=True)
    roappointmentto = models.CharField(max_length=20, blank=True, null=True)
    completedwt = models.BooleanField(null=True, blank=True)
    contactpreference = models.CharField(max_length=10, blank=True, null=True)
    requestdtime = models.DateTimeField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    isscsi = models.BooleanField(null=True, blank=True)
    callfiredtime = models.DateTimeField(blank=True, null=True)
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
    isjustbilling = models.BooleanField(null=True, blank=True)
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
    lastsyncfromsystemdtime = models.DateTimeField(blank=True, null=True)
    installationproblemtarget = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OPTICKET'


class OpTicketAudit(models.Model):
    id = models.FloatField()
    ticketno = models.CharField(max_length=30)
    systemid = models.FloatField()
    issuedtime = models.DateTimeField(blank=True, null=True)
    assigndtime = models.DateTimeField(blank=True, null=True)
    firstcontactdtime = models.DateTimeField(blank=True, null=True)
    contactscheduledtime = models.DateTimeField(blank=True, null=True)
    aptstartdtime = models.DateTimeField(blank=True, null=True)
    aptenddtime = models.DateTimeField(blank=True, null=True)
    techid = models.FloatField(blank=True, null=True)
    completedtime = models.DateTimeField(blank=True, null=True)
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
    isticketrequested = models.BooleanField(null=True, blank=True)
    redoticketno = models.CharField(max_length=30, blank=True, null=True)
    redoreason = models.FloatField(blank=True, null=True)
    delayreason = models.CharField(max_length=100, blank=True, null=True)
    acknowledgedtime = models.DateTimeField(blank=True, null=True)
    gspnstatus = models.BigIntegerField(blank=True, null=True)
    isgspncomplete = models.BooleanField(null=True, blank=True)
    warehouseid = models.CharField(max_length=15, blank=True, null=True)
    lastworepairresult = models.FloatField(blank=True, null=True)
    version = models.CharField(max_length=15, blank=True, null=True)
    producttype = models.CharField(max_length=30, blank=True, null=True)
    productcategory = models.CharField(max_length=2, blank=True, null=True)
    angerindex = models.FloatField(blank=True, null=True)
    timezone = models.CharField(max_length=5, blank=True, null=True)
    dst = models.BooleanField(null=True, blank=True)
    warrantystatus = models.CharField(max_length=15, blank=True, null=True)
    partwterm = models.DateField(blank=True, null=True)
    laborwterm = models.DateField(blank=True, null=True)
    origpostingdtime = models.DateTimeField(blank=True, null=True)
    nspdelayreason = models.CharField(max_length=50, blank=True, null=True)
    quedtime = models.DateField(blank=True, null=True)
    redobyticketno = models.CharField(max_length=30, blank=True, null=True)
    redobyticketissuedtime = models.DateTimeField(blank=True, null=True)
    redobyreason = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    flag = models.BooleanField(null=True, blank=True)
    ascnumber = models.CharField(max_length=20, blank=True, null=True)
    manufacturemonth = models.CharField(max_length=20, blank=True, null=True)
    qosocsscore = models.FloatField(blank=True, null=True)
    wtyexception = models.CharField(max_length=50, blank=True, null=True)
    issueopendtime = models.DateTimeField(blank=True, null=True)
    issueclosedtime = models.DateTimeField(blank=True, null=True)
    issuenoteid = models.FloatField(blank=True, null=True)
    issuelatestid = models.FloatField(blank=True, null=True)
    issuestatus = models.FloatField(blank=True, null=True)
    servicetype = models.CharField(max_length=15, blank=True, null=True)
    nspstatus = models.FloatField(blank=True, null=True)
    nspstatusdtime = models.DateTimeField(blank=True, null=True)
    socount = models.FloatField(blank=True, null=True)
    repeatcount = models.FloatField(blank=True, null=True)
    happycallfollowupdtime = models.DateTimeField(blank=True, null=True)
    riskindex = models.FloatField(blank=True, null=True)
    urgent = models.BooleanField(null=True, blank=True)
    flowmenu = models.FloatField(blank=True, null=True)
    flowmenuexception = models.CharField(max_length=30, blank=True, null=True)
    acctonly = models.BooleanField(null=True, blank=True)
    accountno = models.CharField(max_length=20, blank=True, null=True)
    dplus1 = models.BooleanField(null=True, blank=True)
    requestapptdtime = models.DateTimeField(blank=True, null=True)
    refno = models.CharField(max_length=20, blank=True, null=True)
    symptomcode1 = models.CharField(max_length=10, blank=True, null=True)
    symptomcode2 = models.CharField(max_length=10, blank=True, null=True)
    symptomcode3 = models.CharField(max_length=10, blank=True, null=True)
    symptomdescription1 = models.CharField(max_length=100, blank=True, null=True)
    symptomdescription2 = models.CharField(max_length=100, blank=True, null=True)
    symptomdescription3 = models.CharField(max_length=100, blank=True, null=True)
    repairscenario = models.CharField(max_length=4000, blank=True, null=True)
    ctatticketno = models.CharField(max_length=30, blank=True, null=True)
    ctatissuedtime = models.DateTimeField(blank=True, null=True)
    ptatticketno = models.CharField(max_length=30, blank=True, null=True)
    ptatissuedtime = models.DateTimeField(blank=True, null=True)
    psocount = models.FloatField(blank=True, null=True)
    pangerindex = models.FloatField(blank=True, null=True)
    issuegrade = models.FloatField(blank=True, null=True)
    firstapptdate = models.DateField(blank=True, null=True)
    prevticketdate = models.DateField(blank=True, null=True)
    firstdiagnoseby = models.FloatField(blank=True, null=True)
    firstcontactresult = models.BooleanField(null=True, blank=True)
    firstcontactsuccessdtime = models.DateTimeField(blank=True, null=True)
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
    firstaptmadedtime = models.DateTimeField(blank=True, null=True)
    repaircompletedate = models.DateField(blank=True, null=True)
    firstassigndtime = models.DateTimeField(blank=True, null=True)
    roappointmentfrom = models.CharField(max_length=20, blank=True, null=True)
    roappointmentto = models.CharField(max_length=20, blank=True, null=True)
    completedwt = models.BooleanField(null=True, blank=True)
    contactpreference = models.CharField(max_length=10, blank=True, null=True)
    requestdtime = models.DateTimeField(blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)
    isscsi = models.BooleanField(null=True, blank=True)
    callfiredtime = models.DateTimeField(blank=True, null=True)
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
    isjustbilling = models.BooleanField(null=True, blank=True)
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
    auditdtime = models.DateTimeField(blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    completionscheduledtime = models.DateTimeField(blank=True, null=True)
    completionscheduleby = models.FloatField(blank=True, null=True)
    defectcode = models.CharField(max_length=25, blank=True, null=True)
    defectsymptom = models.CharField(max_length=255, blank=True, null=True)
    hassexception = models.FloatField(blank=True, null=True)
    flags = models.FloatField(blank=True, null=True)
    billno = models.CharField(max_length=20, blank=True, null=True)
    lastsyncfromsystemdtime = models.DateTimeField(blank=True, null=True)
    installationproblemtarget = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OPTICKETAUDIT'				


class OpWorkOrder(models.Model):
    "used to save WORK ORDER details"
    id = models.FloatField(primary_key=True)
    workorderno = models.CharField(max_length=15, blank=True, null=True)
    aptstartdtime = models.DateTimeField(blank=True, null=True)
    aptenddtime = models.DateTimeField(blank=True, null=True)
    startdtime = models.DateTimeField(blank=True, null=True)
    finishdtime = models.DateTimeField(blank=True, null=True)
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
    soprintdtime = models.DateTimeField(blank=True, null=True)
    aptmadeby = models.FloatField(blank=True, null=True)
    aptmadedtime = models.DateTimeField(blank=True, null=True)
    partorderdtime = models.DateTimeField(blank=True, null=True)
    diagnosedtime = models.DateTimeField(blank=True, null=True)
    triage = models.FloatField(blank=True, null=True)
    extraman = models.FloatField(blank=True, null=True)
    quoteby = models.FloatField(blank=True, null=True)
    quotedtime = models.DateTimeField(blank=True, null=True)
    seallevel = models.FloatField(blank=True, null=True)
    seq = models.FloatField(blank=True, null=True)
    partwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    sqbox = models.CharField(max_length=15, blank=True, null=True)
    itsjobid = models.CharField(max_length=15, blank=True, null=True)
    reservecomplete = models.BooleanField(blank=True, null=True)
    partresearchby = models.FloatField(blank=True, null=True)
    partresearchdtime = models.DateTimeField(blank=True, null=True)
    completelogid = models.FloatField(blank=True, null=True)
    reverseitsjobid = models.CharField(max_length=15, blank=True, null=True)
    routedistance = models.FloatField(blank=True, null=True)
    routeduration = models.FloatField(blank=True, null=True)
    routeid = models.FloatField(blank=True, null=True)
    installationtype = models.FloatField(blank=True, null=True)
    reminderemaildtime = models.DateTimeField(blank=True, null=True)
    remindersmsdtime = models.DateTimeField(blank=True, null=True)
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
    msgconfirmdtime = models.DateTimeField(blank=True, null=True)
    techassigntype = models.IntegerField(blank=True, null=True)
    rstartdtime = models.DateTimeField(blank=True, null=True)
    renddtime = models.DateTimeField(blank=True, null=True)
    paymenttransactionid = models.CharField(max_length=100, blank=True, null=True)
    ispartialwarranty = models.BooleanField(blank=True, null=True)
    smallsignaturedocid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OPWORKORDER'        


class OpWorkOrderAudit(models.Model):
    "to save audit records for work orders"
    id = models.FloatField()
    workorderno = models.CharField(max_length=15, blank=True, null=True)
    aptstartdtime = models.DateTimeField(blank=True, null=True)
    aptenddtime = models.DateTimeField(blank=True, null=True)
    startdtime = models.DateTimeField(blank=True, null=True)
    finishdtime = models.DateTimeField(blank=True, null=True)
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
    soprintdtime = models.DateTimeField(blank=True, null=True)
    aptmadeby = models.FloatField(blank=True, null=True)
    aptmadedtime = models.DateTimeField(blank=True, null=True)
    partorderdtime = models.DateTimeField(blank=True, null=True)
    diagnosedtime = models.DateTimeField(blank=True, null=True)
    triage = models.FloatField(blank=True, null=True)
    extraman = models.FloatField(blank=True, null=True)
    quoteby = models.FloatField(blank=True, null=True)
    quotedtime = models.DateTimeField(blank=True, null=True)
    seallevel = models.FloatField(blank=True, null=True)
    seq = models.FloatField(blank=True, null=True)
    partwarehouseid = models.CharField(max_length=15, blank=True, null=True)
    sqbox = models.CharField(max_length=15, blank=True, null=True)
    itsjobid = models.CharField(max_length=15, blank=True, null=True)
    reservecomplete = models.BooleanField(blank=True, null=True)
    partresearchby = models.FloatField(blank=True, null=True)
    partresearchdtime = models.DateTimeField(blank=True, null=True)
    completelogid = models.FloatField(blank=True, null=True)
    reverseitsjobid = models.CharField(max_length=15, blank=True, null=True)
    routedistance = models.FloatField(blank=True, null=True)
    routeduration = models.FloatField(blank=True, null=True)
    routeid = models.FloatField(blank=True, null=True)
    installationtype = models.FloatField(blank=True, null=True)
    reminderemaildtime = models.DateTimeField(blank=True, null=True)
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
    msgconfirmdtime = models.DateTimeField(blank=True, null=True)
    techassigntype = models.IntegerField(blank=True, null=True)
    rstartdtime = models.DateTimeField(blank=True, null=True)
    renddtime = models.DateTimeField(blank=True, null=True)
    auditid = models.FloatField(primary_key=True)
    type = models.CharField(max_length=1, blank=True, null=True)
    auditee = models.FloatField(blank=True, null=True)
    auditdtime = models.DateTimeField(blank=True, null=True)
    method = models.CharField(max_length=100, blank=True, null=True)
    status = models.FloatField(blank=True, null=True)
    pid = models.FloatField(blank=True, null=True)
    paymenttransactionid = models.CharField(max_length=100, blank=True, null=True)
    ispartialwarranty = models.BooleanField(blank=True, null=True)
    smallsignaturedocid = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'OPWORKORDERAUDIT'        


class Pictures(models.Model):
    pictureid = models.IntegerField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.IntegerField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
    updatedby = models.IntegerField(blank=True, null=True)
    tablename = models.CharField(max_length=30, blank=True, null=True)
    filterstr = models.CharField(max_length=100, blank=True, null=True)
    fieldname = models.CharField(max_length=30, blank=True, null=True)
    ext = models.CharField(max_length=5, blank=True, null=True)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    refcd = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PICTURES'         		
	



