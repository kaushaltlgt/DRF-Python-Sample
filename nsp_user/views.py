import datetime
from django.http.response import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseBadRequest, HttpResponseRedirect
from .models import Nspusers, OauthAccessTokens
from functions.kwlogging import SimpleLogger, AdvancedLogger, BaseApiController
from nsp_user.authentication import KWAuthentication, AzureAuthentication
from nsp_user.support import NSPSupport
from schedules_list_map.schedules import WorkOrderAdditionalInfoVO
from django.urls import reverse
from nsp_user.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from nsp_user.graph_helper import *
from nsp_user.support import DjangoOverRideJSONEncoder
from django.utils import timezone
#write views here

class HomePage(View):
    "to show a simple home page"
    def get(self, request):
        "render a simple HTML page"
        html_page = """
                    <!DOCTYPE html>
                    <html>
                        <head>
                        <meta charset="utf-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <title>KWServices</title>
                        </head>
                        <body>
                        <center>
                        <div style='margin-top:200px;'>
                        <h><b>KWSERVICES</b></h>
                        <p style='color:red;'>Unauthorised Access Denied</p>
                        </div>
                        </center>
                        </body>
                    </html>    
                    """
        return HttpResponse(html_page)

def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error != None:
        context['errors'] = []
    context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user',{'is_authenticated': False})
    return context        

def sign_in(request):
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)    # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])

def sign_out(request):
    # Clear out the user and token
    remove_user_and_token(request)
    CurrentUserID = KWAuthentication.getcurrentuser(request)
    OauthAccessTokens.objects.filter(user_id=CurrentUserID).delete()
    return HttpResponse('signed out successfully')

def callback(request):
    # Make the token request
    result = get_token_from_code(request)    #Get the user's profile from graph_helper.py script
    print("result = ", result)
    user = get_user(result['access_token'])     # Store user from auth_helper.py script
    store_user(request, user)
    return HttpResponseRedirect(reverse('home'))                    

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    "accept required parameters for login"
    def post(self, request):
        device_id = request.POST.get('DeviceID')
        device_name = request.POST.get('DeviceName')
        uid = request.POST.get('UID')
        pwd = request.POST.get('PWD')
        if not device_id or not device_name or not uid or not pwd:
            return HttpResponseBadRequest('invalid credentials')
        result = AzureAuthentication.get_token(request, uid, pwd)
        if "access_token" in result:
            AzureAuthentication.save_token(uid, result['access_token'])
            ns = Nspusers.objects.filter(email=uid)[0]
            authdict = {}
            today = timezone.now()
            current_token = OauthAccessTokens.objects.filter(name=uid, expires_at__gte=today) #checking if a valid token already exists in the database
            if current_token.exists():
                valid_token = current_token[0].scopes
            else:
                valid_token = result['access_token']   
            authdict['SignInResult'] = valid_token
            authdict['UserInfo'] = {
                "UserID" : ns.userid,
                "UserName" : uid.split('@')[0],
                "Groups" : None,
                "Admin" : ns.ismanager,
                "Staff" : None,
                "Location" : None
            }
            return JsonResponse(authdict, safe=False, status=200)
        else:
            return JsonResponse(result, safe=False, status=400)    


def get_nsp_user(request):
    # URI : /servicequick/api/NSPUsers?ID=45971&type=
    SimpleLogger.do_log(">>> Get()...")
    p1 = KWAuthentication
    authstat = p1.authenticate(request)

    user_id = request.GET.get('ID')
    user_type = request.GET.get('type')

    CurrentUserID = KWAuthentication.getcurrentuser(request)
    jsonString = str(json.dumps({'user_type':user_type}))
    AppVersion = request.META.get('HTTP_APPVERSION')
    callerApp = BaseApiController.CallerApp(request) 
    sqAPILog = BaseApiController.StartLog(CurrentUserID, str(user_type), "GET", "NSPUsersController", jsonString, callerApp, AppVersion)

    if authstat is not True:
        return JsonResponse(authstat, status=401)

    if user_type is None:
        nspUser = Nspusers.objects.filter(nspstatus=1)\
            .exclude(email__isnull=True).exclude(email__exact='').order_by('email')
    else:        
        if user_type.upper()=='NSC':
            if user_id is not None:
                nspUser = Nspusers.objects.filter(isnsc=True, nspstatus=1, userid=user_id)
            else:
                nspUser = Nspusers.objects.filter(isnsc=True, nspstatus=1)    
        elif user_type.upper()=='TECHNICIAN':
            if user_id is not None:
                nspUser = Nspusers.objects.filter(isfieldtech=True, nspstatus=1, userid=user_id).order_by('email')
            else:
                nspUser = Nspusers.objects.filter(isfieldtech=True, nspstatus=1).order_by('email')
        else:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Wrong user type: {user_type}')            
            return JsonResponse({'message':f'Wrong user type: {user_type}'}, safe=False, status=400)
    #Preparing a list of dicts        
    ResponseData = []        
    for ns in nspUser:        
        resultList = {}
        resultList['UserID'] = ns.userid
        resultList['WarehouseID'] = ns.warehouseid
        resultList['NSPStatus'] = ns.nspstatus
        resultList['IsCallAgent'] = ns.iscallagent
        resultList['IsCallTech'] = ns.iscalltech
        resultList['IsFieldTech'] = ns.isfieldtech
        resultList['IsLeadTech'] = ns.isleadtech
        resultList['IsManager'] = ns.ismanager
        resultList['IsClaimAgent'] = ns.isclaimagent
        resultList['IsFST'] = ns.isfst
        resultList['IsDIS'] = ns.isdis
        resultList['IsWarehouse'] = ns.iswarehouse
        resultList['Email'] = ns.email
        resultList['FirstName'] = ns.firstname
        resultList['LastName'] = ns.lastname
        resultList['CurrentTicketNo'] = ns.currentticketno
        resultList['CompanyID'] = ns.companyid
        resultList['Latitude'] = ns.latitude
        resultList['Longitude'] = ns.longitude
        resultList['IsNSC'] = ns.isnsc
        resultList['IsNSCManager'] = ns.isnscmanager
        if ns.init is None and ns.firstname and ns.lastname:
            initial = ns.firstname[0:1] + ns.lastname[0:1]
            resultList['Initial'] = initial
        else:        
            resultList['Initial'] = ns.init
        if ns.firstname and ns.lastname:    
            resultList['FullName'] = ns.firstname + ' ' + ns.lastname
        else:
            resultList['FullName'] = None
        if ns.email:
            try:
                resultList['UserName'] = str(ns.email).split('@')[0]
            except:
                resultList['UserName'] = ns.email
        else:
            resultList['UserName'] = None
        resultList['CreatedOn'] = ns.createdon
        resultList['CreatedBy'] = ns.createdby
        resultList['UpdatedOn'] = ns.updatedon 
        resultList['UpdatedBy'] = ns.updatedby
        if ns.updatedby is not None:
            resultList['LogBy'] = ns.updatedby
        else:
            resultList['LogBy'] = ns.createdby    
        resultList['LogByName'] = None #this is always null as per C# code
        ResponseData.append(resultList)
    finalRes = {}    
    finalRes['ListSize'] = len(ResponseData)                
    finalRes['List'] = ResponseData
    finalRes['LogID'] = BaseApiController.getlogid("GET", "NSPUsersController", CurrentUserID)    
    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)                            
    return JsonResponse(finalRes, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)        


def get_user_by_id(request, user_id = None):
    # GET api/nspUsers/5
    SimpleLogger.do_log(f">>> Get()...{user_id}")
    p1 = KWAuthentication
    authstat = p1.authenticate(request)

    CurrentUserID = KWAuthentication.getcurrentuser(request)
    jsonString = str(json.dumps({'user_id':user_id}))
    AppVersion = request.META.get('HTTP_APPVERSION')
    callerApp = BaseApiController.CallerApp(request) 
    sqAPILog = BaseApiController.StartLog(CurrentUserID, str(user_id), "GET", "NSPUsersController", jsonString, callerApp, AppVersion)

    if authstat is not True:
        return JsonResponse(authstat, status=401)
    
    if user_id is None:
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='user id not provided')            
        return JsonResponse({'message':'user id not provided'}, safe=False, status=400)

    try:
        ns = Nspusers.objects.get(userid=user_id)
    except (Nspusers.DoesNotExist):
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'NSPUser not found: {user_id}')            
        return JsonResponse({'message':f'NSPUser not found: {user_id}'}, safe=False, status=400)

    resultList = {}
    resultList['UserID'] = ns.userid
    resultList['WarehouseID'] = ns.warehouseid
    resultList['NSPStatus'] = ns.nspstatus
    resultList['IsCallAgent'] = ns.iscallagent
    resultList['IsCallTech'] = ns.iscalltech
    resultList['IsFieldTech'] = ns.isfieldtech
    resultList['IsLeadTech'] = ns.isleadtech
    resultList['IsManager'] = ns.ismanager
    resultList['IsClaimAgent'] = ns.isclaimagent
    resultList['IsFST'] = ns.isfst
    resultList['IsDIS'] = ns.isdis
    resultList['IsWarehouse'] = ns.iswarehouse
    resultList['Email'] = ns.email
    resultList['FirstName'] = ns.firstname
    resultList['LastName'] = ns.lastname
    resultList['CurrentTicketNo'] = ns.currentticketno
    resultList['CompanyID'] = ns.companyid
    resultList['Latitude'] = ns.latitude
    resultList['Longitude'] = ns.longitude
    resultList['IsNSC'] = ns.isnsc
    resultList['IsNSCManager'] = ns.isnscmanager
    if ns.init is None and ns.firstname and ns.lastname:
        initial = ns.firstname[0:1] + ns.lastname[0:1]
        resultList['Initial'] = initial
    else:        
        resultList['Initial'] = ns.init
    if ns.firstname and ns.lastname:    
        resultList['FullName'] = ns.firstname + ' ' + ns.lastname
    else:
        resultList['FullName'] = None
    if ns.email:
        try:
            resultList['UserName'] = str(ns.email).split('@')[0]
        except:
            resultList['UserName'] = ns.email
    else:
        resultList['UserName'] = None
    resultList['CreatedOn'] = ns.createdon
    resultList['CreatedBy'] = ns.createdby
    resultList['UpdatedOn'] = ns.updatedon 
    resultList['UpdatedBy'] = ns.updatedby
    if ns.updatedby is not None:
        resultList['LogBy'] = ns.updatedby
    else:
        resultList['LogBy'] = ns.createdby    
    resultList['LogByName'] = None #this is always null as per C# code
    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)                        
    return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


def get_user_by_username(request, userName = None):
    # GET api/nspUsers/Name
    SimpleLogger.do_log(f">>> Get()...{userName}")
    p1 = KWAuthentication
    authstat = p1.authenticate(request)

    CurrentUserID = KWAuthentication.getcurrentuser(request)
    jsonString = str(json.dumps({'userName':userName}))
    AppVersion = request.META.get('HTTP_APPVERSION')
    callerApp = BaseApiController.CallerApp(request) 
    sqAPILog = BaseApiController.StartLog(CurrentUserID, str(userName), "GET", "NSPUsersController", jsonString, callerApp, AppVersion)

    if authstat is not True:
        return JsonResponse(authstat, status=401)
        
    if userName is None:
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='username is not provided')            
        return JsonResponse({'message':'username is not provided'}, safe=False, status=400)

    try:
        ns = Nspusers.objects.get(email__contains=userName)
        SimpleLogger.do_log(f">>> nspUser={userName}")
    except Exception as e:
        print(e)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'NSPUser not found: {userName}')            
        return JsonResponse({'message':f'NSPUser not found: {userName}'}, safe=False, status=400)

    resultList = {}
    resultList['UserID'] = ns.userid
    resultList['WarehouseID'] = ns.warehouseid
    resultList['NSPStatus'] = ns.nspstatus
    resultList['IsCallAgent'] = ns.iscallagent
    resultList['IsCallTech'] = ns.iscalltech
    resultList['IsFieldTech'] = ns.isfieldtech
    resultList['IsLeadTech'] = ns.isleadtech
    resultList['IsManager'] = ns.ismanager
    resultList['IsClaimAgent'] = ns.isclaimagent
    resultList['IsFST'] = ns.isfst
    resultList['IsDIS'] = ns.isdis
    resultList['IsWarehouse'] = ns.iswarehouse
    resultList['Email'] = ns.email
    resultList['FirstName'] = ns.firstname
    resultList['LastName'] = ns.lastname
    resultList['CurrentTicketNo'] = ns.currentticketno
    resultList['CompanyID'] = ns.companyid
    resultList['Latitude'] = ns.latitude
    resultList['Longitude'] = ns.longitude
    resultList['IsNSC'] = ns.isnsc
    resultList['IsNSCManager'] = ns.isnscmanager
    if ns.init is None and ns.firstname and ns.lastname:
        initial = ns.firstname[0:1] + ns.lastname[0:1]
        resultList['Initial'] = initial
    else:        
        resultList['Initial'] = ns.init
    if ns.firstname and ns.lastname:    
        resultList['FullName'] = ns.firstname + ' ' + ns.lastname
    else:
        resultList['FullName'] = None
    if ns.email:
        try:
            resultList['UserName'] = str(ns.email).split('@')[0]
        except:
            resultList['UserName'] = ns.email
    else:
        resultList['UserName'] = None
    resultList['CreatedOn'] = ns.createdon
    resultList['CreatedBy'] = ns.createdby
    resultList['UpdatedOn'] = ns.updatedon 
    resultList['UpdatedBy'] = ns.updatedby
    if ns.updatedby is not None:
        resultList['LogBy'] = ns.updatedby
    else:
        resultList['LogBy'] = ns.createdby    
    resultList['LogByName'] = None #this is always null as per C# code 
    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)                      
    return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class IsUserSOUpdatedController(View):
    "to check workorder is updated for an user" 
    def get(self, request):
        "accept parameters in GET to process"
        # GET servicequick/api/IsUserSOUpdated
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        
        TechID = request.GET.get('TechID')
        LastSyncDTime = request.GET.get('LastSyncDTime') 
        WorkOrders = request.GET.get('WorkOrders')
        reqData = f"TechID : {TechID}, LastSyncDTime : {LastSyncDTime}, WorkOrders : {WorkOrders}"
        #Logging
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(TechID), "GET", "IsUserSOUpdatedController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        try:
            TechID = int(TechID)
        except:
            pass
        try:
            LastSyncDTime = datetime.datetime.strptime(LastSyncDTime, "%Y-%m-%d %H:%M:%S")
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='LastSyncDTime must have time value')            
            return JsonResponse({'message':'LastSyncDTime must have time value'}, safe=False, status=400)
        #Validating the received data
        nspUser = Nspusers.objects.filter(userid=TechID)
        if not nspUser.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'NSPUser not found: {TechID}')            
            return JsonResponse({'message':f'NSPUser not found: {TechID}'}, safe=False, status=400)
        elif not WorkOrders:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='WorkOrders are required')            
            return JsonResponse({'message':'WorkOrders are required'}, safe=False, status=400)
        elif LastSyncDTime.date()!=datetime.date.today():
            print(LastSyncDTime.date)
            print(datetime.date.today())
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='LastSyncDTime must be sometime of today')            
            return JsonResponse({'message':'LastSyncDTime must be sometime of today'}, safe=False, status=400)
        else:
            sIDs = WorkOrders.split(',')
            for s in sIDs:
                try:
                    ID = int(s)
                except:
                    return HttpResponseBadRequest('WorkOrderID must be numeric')
        #check if workorder updated
        SQresbool = NSPSupport.IsWorkOrderUpdatedByOtherUser(CurrentUserID, TechID, LastSyncDTime, WorkOrders) #function returns True/False
        if SQresbool is True:
            res_str = 'true'
        else:
            res_str = 'false'
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)         
        return HttpResponse(res_str)

@method_decorator(csrf_exempt, name='dispatch')
class NSPUserLocationController(View):
    "to update location of an user"
    def put(self, request):
        "accept parameters in PUT request"
        # GET servicequick/api/nspUserLocation
        SimpleLogger.do_log(">>> Put()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        userId = request.GET.get('userId')
        latitude = request.GET.get('latitude') 
        longitude = request.GET.get('longitude')
        reqData = f"userId : {userId}, latitude : {latitude}, longitude : {longitude}"
        #Logging the parameters
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(userId), "GET", "NSPUserLocationController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        
        #Validating the received data
        try:
            userId = int(userId)
        except:
            pass
        try:
            latitude = float(latitude)
        except:
            pass
        try:
            longitude = float(longitude)
        except:
            pass
        nspUser = Nspusers.objects.filter(userid=userId)
        if not nspUser.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'NSPUser not found: {userId}')            
            return JsonResponse({'message':f'NSPUser not found: {userId}'}, safe=False, status=400)
        #Processing the update
        SQService = NSPSupport.UpdateNSPUserLocation(userId, latitude, longitude, CurrentUserID)
        if SQService is True:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return HttpResponse("NSPUser Location Updated")
        else:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=SQService)
            return HttpResponseServerError(f'Server Error. Please try again. More Info : {SQService}')


class UserTicketsController(View):
    "to get tickets assigned to the user"
    def get(self, request):
        "accept userId or userName in GET to process"
        # GET servicequick/api/usertickets
        SimpleLogger.do_log(">>> Get()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Logging and decoding the parameters received    
        userId = request.GET.get('userId')
        userName = request.GET.get('userName')
        try:
            userId = int(userId)
        except:
            pass    
        reqData = f"userId : {userId}, userName : {userName}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(userId) if not None else userName, "GET", "UserTicketsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
       
        # Validation
        nspUser = None
        if not userId:
            if not userName:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Parameter not found: userId or userName')            
                return JsonResponse({'message':'Parameter not found: userId or userName'}, safe=False, status=404)
            else:
                nspUser = NSPSupport.GetNSPUserByUserName(userName)
                if nspUser is None:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"NSP user not found by userName: {userName}")            
                    return JsonResponse({'message':f"NSP user not found by userName: {userName}"}, safe=False, status=404)
        else:
            nspUser = NSPSupport.GetNSPUserByUserID(userId)
            if nspUser is None:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"NSP user not found by userId: {userId}")            
                return JsonResponse({'message':f"NSP user not found by userId: {userId}"}, safe=False, status=404)
        SimpleLogger.do_log(f"nspUser={nspUser}", "debug")
        # Processing the data
        currentTicketList = NSPSupport.GetTechnicianCurrentTickets(nspUser['UserID'])
        resultList = {}
        resultList['UserID'] = userId
        resultList['UserName'] = userName
        resultList['ListSize'] = len(currentTicketList)
        resultList['List'] = currentTicketList

        sGSPNTechIDWithRA = WorkOrderAdditionalInfoVO.GetGSPNTechIDWithRA(nspUser['UserID'])
        for ticket in resultList['List']:
            ticket['LastAttentionCode'] = WorkOrderAdditionalInfoVO.GetLastAttentionCode(ticket['SerialNo'])
            if ticket['AlertMessage'] and ticket['AlertMessage']!="":
                ticket['AlertMessage'] = ticket['AlertMessage'].split('\n')[0]
            if ticket['GSPNTechnicianID'] and ticket['GSPNTechnicianID']!=sGSPNTechIDWithRA:
                ticket['GSPNTechnicianID'] = None

        resultList['LogID'] = BaseApiController.getlogid("GET", "UserTicketsController", CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)                                                                  

                                    






