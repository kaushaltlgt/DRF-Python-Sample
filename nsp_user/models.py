from django.db import models
from django.utils import timezone

class Nspusers(models.Model):
    userid = models.FloatField(primary_key=True)
    createdon = models.DateTimeField(blank=True, null=True)
    createdby = models.FloatField(blank=True, null=True)
    updatedon = models.DateTimeField(blank=True, null=True)
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
    isnsc = models.BooleanField(blank=True, null=True)
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

class OauthAccessTokens(models.Model):
    "used to save/read authentication tokens" 
    id = models.CharField(max_length=100, primary_key=True)
    user_id = models.IntegerField(null=True)
    client_id = models.IntegerField(null=True)
    name = models.CharField(max_length=255, null=True)
    scopes = models.CharField(max_length=3000, null=True)
    revoked = models.IntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'oauth_access_tokens'


def getuserinfo(userid):
    "to get username and full name based on UserID"
    if userid is None:
        return None
    try:
        ns = Nspusers.objects.get(userid=userid)
        UserID = userid
        if ns.email:
            try:
                UserName = str(ns.email).split('@')[0]
            except:
                UserName = ns.email
        else:
            UserName = None
        if ns.firstname and ns.lastname:    
            FullName = ns.firstname + ' ' + ns.lastname
        else:
            FullName = None
    except:
        UserID = userid
        UserName = None
        FullName = None
    try:
        UserID = int(UserID)
    except:
        pass
    return {'UserID':UserID, 'UserName': UserName, 'FullName':FullName}


def getboolvalue(field):
    "to return True/False depending on the field value"
    if field==0:
        return False
    elif field==1:
        return True
    else:
        return None

def getfloatvalue(field):
    "returns float value"
    try:
        return float(field)
    except:
        return None                                


