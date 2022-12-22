import datetime, json, mimetypes, os
from django.utils import timezone
from django.http.response import HttpResponse
from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from functions.querymethods import SingleCursor, DBIDGENERATOR
from nsp_user.authentication import KWAuthentication
from django.http import HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseBadRequest
from functions.kwlogging import SimpleLogger, AdvancedLogger, BaseApiController
from functions.smtpgateway import sendmailoversmtp
from functions.xmlfunctions import get_xml_node
from nsp_user.models import Nspusers, getuserinfo
from schedules_list_map.models import OpContactCustomer, OpBase, OpWorkOrder, OpTicket, OpTicketAudit, OpWorkOrderAudit
from schedules_list_map.schedules import UserTicketScheduleType, GetTechnicianCurrentWorkOrders, WorkOrderAdditionalInfoVO, WorkOrderStatus, TicketStatus, OpType, LogType, ContactLogStatus, ContactResultCode, GspnWebServiceClient, SystemIDEnum
from schedules_detail.models import NspPartSerials, NspLocations
from schedules_detail.support import PartSupport
from schedules_detail.schedules2 import SchedulesService, PictureTrans
from schedules_list_map.support import ContactSupport, NSPWSClient, InventorySupport, FileActions
from nsp_user.support import DjangoOverRideJSONEncoder


# Create your views here.

class UserWorkOrdersController(View):
    "to fetch list of user work orders based on UserID and other parameters"
    def get(self, request):
        # GET /servicequick/api/UserWorkorders?UserID=$userId&ScheduleType=1
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Decoding/Logging the GET request
        user_id = request.GET.get('userId')
        username = request.GET.get('userName') 
        schedule_type = request.GET.get('ScheduleType')
        SimpleLogger.do_log(f"userId = {user_id}")
        SimpleLogger.do_log(f"userName = {username}")
        SimpleLogger.do_log(f"ScheduleType = {schedule_type}")
        reqData = f"userId : {user_id}, userName : {username}, ScheduleType : {schedule_type}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(user_id), "GET", "UserWorkOrdersController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        token = request.META.get('HTTP_KW_TOKEN')
        #Validating the passed parameters
        nspUser = None
        if user_id is None or user_id=='':
            if username is None or username=='':
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Parameter not found: userId or userName')            
                return JsonResponse({'message':'Parameter not found: userId or userName'}, safe=False, status=404)
            else:
                try:
                    Nspusers.objects.filter(email__startswith=username+'@')[0]
                    nspUser = username
                except:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"NSP user not found by userName: {username}")            
                    return JsonResponse({'message':f"NSP user not found by userName: {username}"}, safe=False, status=404)
        else:
            try:
                u = Nspusers.objects.get(userid=user_id)
                nspUser = u.email.split('@')[0]
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"NSP user not found by userId: {user_id}")            
                return JsonResponse({'message':f"NSP user not found by userId: {user_id}"}, safe=False, status=404)

        SimpleLogger.do_log(f"nspUser = {nspUser}")

        try:
            schedule_type = int(schedule_type)
        except:
            schedule_type = UserTicketScheduleType.NONE.value

        try:
            schedule_type_name = UserTicketScheduleType(schedule_type).name  #getting schedule type name from the enum UserTicketScheduleType
        except:
            return HttpResponseBadRequest(f"Invalid value for schedule_type : {str(schedule_type)}")     

        if not user_id:
            user_id = Nspusers.objects.filter(email__startswith=nspUser+'@')[0].userid     

        #getting GSPNTechID
        sGSPNTechIDWithRA = WorkOrderAdditionalInfoVO.GetGSPNTechIDWithRA(user_id)

        #preparing for workOrderList
        workorders_list = GetTechnicianCurrentWorkOrders.process_query(user_id, schedule_type_name, CurrentUserID, token)
        resultList = {}
        resultList['UserID'] = user_id
        resultList['UserName'] = nspUser
        resultList['ScheduleType'] = str(schedule_type)
        resultList['ListSize'] = len(workorders_list)
        resultList['List'] = workorders_list
        resultList['LogID'] = BaseApiController.getlogid('GET', 'UserWorkOrdersController', CurrentUserID)
        
        #print(workorders_list)

        for wo in resultList['List']:
            if schedule_type_name=='TODAY':
                if wo['Ticket']:
                    wo['DefectCodeList'] = WorkOrderAdditionalInfoVO.GetDefectCodeList(wo['Ticket']['ModelNo'], wo['Ticket']['SystemID'], CurrentUserID, token)
                    wo['RepairCodeList'] = WorkOrderAdditionalInfoVO.GetRepairCodeList(wo['Ticket']['ModelNo'], wo['Ticket']['SystemID'], CurrentUserID, token)
                else: 
                    wo['DefectCodeList'] = []
                    wo['RepairCodeList'] = []  
                if wo.get('DefectCode'):
                    wo['DefectCodeDescription'] = WorkOrderAdditionalInfoVO.GetDefectCodeDescription(wo['DefectCodeList'], wo['DEFECTCODE'])
                if wo.get('RepairCode'):
                    wo['RepairCodeDescription'] = WorkOrderAdditionalInfoVO.GetRepairCodeDescription(wo['RepairCodeList'], wo['REPAIRCODE'])
                if wo.get('Ticket').get('SerialNo') is None:
                    wo['SerialNo'] = ""

            if wo['Ticket']:        
                if (wo['Ticket']['GSPNTechnicianID'] and wo['Ticket']['GSPNTechnicianID']!=sGSPNTechIDWithRA) or wo['Ticket']['SystemID']!=SystemIDEnum.GSPN.value or wo['Ticket']['ServiceType']!='IH' or wo['Ticket']['ServiceType']!='RC':
                    wo['Ticket']['GSPNTechnicianID'] = None

                wtyAlert = ''

                if wo['Ticket']['WtyException']=='OTWEU':
                    wtyAlert = 'OTWEU - CS4U: CX is OOW but paid Samsung - please consider just like IW'
                elif wo['Ticket']['WtyException']=='OTWER':
                    wtyAlert = 'OTWER - Samsung will cover labor and parts related for ice maker issue'
                else:
                    pass

                if wtyAlert and (wo['Ticket']['AlertMessage'] or wo['Ticket']['AlertMessage'].startswith(wtyAlert) is False):
                    if wo['Ticket']['AlertMessage'] is not None:
                        msg_subtext = "\r\n" + wo['Ticket']['AlertMessage']
                    else:
                        msg_subtext = ""    
                    wo['Ticket']['AlertMessage'] = wtyAlert + msg_subtext

                if len(wo['Ticket']['Pictures']) > 0:
                    for p in wo['Ticket']['Pictures']:
                        p['URL'] = request.scheme + '://' + request.get_host() + '/media/pictures' + p['URL']    
            else:
                pass
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)                                   
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
        

@method_decorator(csrf_exempt, name='dispatch')
class EditAppointmentController(View):
    "to edit appointments based on workorder ID and other parameters"
    def post(self, request):
        "accept values in the POST request to process data"
        # Api: /servicequick/api/editappointment
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data
        content = request.body.decode("utf-8")
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request") 
        SimpleLogger.do_log(f"content= {content}")       
        WorkOrderID = received_json_data.get('WorkOrderID')
        AptStartDTime = received_json_data.get("AptStartDTime") 
        AptEndDTime = received_json_data.get("AptEndDTime")
        #log the request in the database
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(WorkOrderID), "POST", "EditAppointmentController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        try:
            WorkOrderID = int(WorkOrderID)
        except:
            pass     
       
        SimpleLogger.do_log(f"reqData= {received_json_data}") 

        #validating the request
        if WorkOrderID is None or WorkOrderID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Value not found: WorkOrderID')            
            return JsonResponse({'message':'Value not found: WorkOrderID'}, safe=False, status=400)
        if AptStartDTime is None or not AptStartDTime:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Value not found: AptStartDTime')            
            return JsonResponse({'message':'Value not found: AptStartDTime'}, safe=False, status=400)
        if AptEndDTime is None or not AptEndDTime:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Value not found: AptEndDTime')            
            return JsonResponse({'message':'Value not found: AptEndDTime'}, safe=False, status=400)

        try:
            AptStartDTime = datetime.datetime.strptime(AptStartDTime, "%m/%d/%Y %H:%M:%S")
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid AptStartDTime datetime format. Must be in M/d/yyyy HH:mm:ss')            
            return JsonResponse({'message':'Invalid AptStartDTime datetime format. Must be in M/d/yyyy HH:mm:ss'}, safe=False, status=400)

        try:
            AptEndDTime = datetime.datetime.strptime(AptEndDTime, "%m/%d/%Y %H:%M:%S")
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid AptEndDTime datetime format. Must be in M/d/yyyy HH:mm:ss')            
            return JsonResponse({'message':'Invalid AptEndDTime datetime format. Must be in M/d/yyyy HH:mm:ss'}, safe=False, status=400)

        if AptStartDTime > AptEndDTime:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Value error: StartTime cannot be later than EndTime')            
            return JsonResponse({'message':'Value error: StartTime cannot be later than EndTime'}, safe=False, status=400)

        #AptStartDTime = timezone.make_aware(AptStartDTime)     
        #AptEndDTime = timezone.make_aware(AptEndDTime)  
        #WorkOrderID_string = f"WorkOrderID={WorkOrderID},AptStartDTime={AptStartDTime},AptEndDTime={AptEndDTime}"

        #getting workorder data
        try: 
            query_workorder = OpWorkOrder.objects.get(id=int(WorkOrderID)) 
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Work order not found: {str(WorkOrderID)}"}, safe=False, status=400)
        
        #checking workorder status
        query = f"select * from opworkorder join opbase on opworkorder.ID = opbase.ID where opworkorder.ID = {WorkOrderID};"
        res = SingleCursor.send_query(query)
        if len(res)==0 or type(res) is str:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Work order not found: {str(WorkOrderID)}"}, safe=False, status=400)

        try:  
            if WorkOrderStatus(int(res['STATUS'])).name=='PROCESSING':
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order has already been processing: {str(WorkOrderID)}")            
                return JsonResponse({'message':f"Work order has already been processing: {str(WorkOrderID)}"}, safe=False, status=400)
        except Exception as e:
            print(e)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"WorkOrderStatus value is not valid : {res['STATUS']}")            
            return JsonResponse({'message':f"WorkOrderStatus value is not valid : {res['STATUS']}"}, safe=False, status=400)

        #code for the function UpdateWorkOrderSchedule
        try:
            if int(res['STATUS']) > WorkOrderStatus.SCHEDULED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order cannot be updated: status = {WorkOrderStatus(int(res['STATUS'])).name}")        
                return JsonResponse({'message':f"Work order cannot be updated: status = {WorkOrderStatus(int(res['STATUS'])).name}"}, safe=False, status=400)
        except Exception as e:
            print(e)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"WorkOrderStatus value is not valid : {res['STATUS']}")            
            return JsonResponse({'message':f"WorkOrderStatus value is not valid : {res['STATUS']}"}, safe=False, status=400)

        try:
            b = OpBase.objects.get(id=WorkOrderID)
            ticket_id = OpTicket.objects.get(id=b.pid).id
            if int(res['STATUS']) >= TicketStatus.CLOSED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Ticket has already been closed: {ticket_id}")            
                return JsonResponse({'message':f"Ticket has already been closed: {ticket_id}"}, safe=False, status=400)
        except Exception as e:
            print(e)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"WorkOrderStatus value is not valid : {res['STATUS']}")            
            return JsonResponse({'message':f"WorkOrderStatus value is not valid : {res['STATUS']}"}, safe=False, status=400)       
        
        AptMadeDTime = None    
        AptMadeBy = None
        if (res['APTSTARTDTIME'] is None and AptStartDTime is not None) or (res['APTSTARTDTIME'] is not None and AptStartDTime.date()!=res['APTSTARTDTIME'].date()):
            AptMadeDTime = timezone.now()
            OpWorkOrder.objects.filter(id=WorkOrderID).update(aptmadedtime=AptMadeDTime)

        if CurrentUserID!=0:
            AptMadeBy = CurrentUserID
            OpWorkOrder.objects.filter(id=WorkOrderID).update(aptmadeby=AptMadeBy)

        if int(res['STATUS'])==WorkOrderStatus.SCHEDULED.value:
            workorder_status = WorkOrderStatus.SCHEDULED.value
            OpBase.objects.filter(id=WorkOrderID).update(status=workorder_status)

            #finally update the following records
            OpWorkOrder.objects.filter(id=WorkOrderID).update(aptstartdtime=AptStartDTime, aptenddtime=AptEndDTime)

            #log.Debug("Work order saved: " + workOrder.ID)
            SimpleLogger.do_log(f"Work order saved: {str(WorkOrderID)}")

            #updating the opticket and opbase tables
            try:
                workorder = OpWorkOrder.objects.get(id=WorkOrderID)
                b = OpBase.objects.get(id=WorkOrderID)
                if b.createdon is None or not b.createdon:
                    OpBase.objects.filter(id=WorkOrderID).update(createdon=datetime.date.today(), createdby=CurrentUserID)
                else:
                    OpBase.objects.filter(id=WorkOrderID).update(updatedon=datetime.date.today(), updatedby=CurrentUserID)
                OpTicket.objects.filter(id=b.pid).update(aptstartdtime=workorder.aptstartdtime, aptenddtime=workorder.aptenddtime)
                OpBase.objects.filter(id=WorkOrderID).update(status=TicketStatus.IN_REPAIR.value)
                ticket_no = OpTicket.objects.get(id=b.pid).ticketno
                SimpleLogger.do_log(f"Ticket saved: {str(WorkOrderID)}")
            except Exception as e:
                SimpleLogger.do_log(f"ERROR in saving ticket: {str(e)}")
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"ERROR in saving ticket:: {str(e)}")            
                return JsonResponse({'message':f"ERROR in saving ticket: : {str(e)}"}, safe=False, status=400) 

            #saving a ticketaudit now
            audit_id = DBIDGENERATOR.process_id("OpTicketAudit_SEQ")
            try:
                t = OpTicket.objects.get(id=b.pid)
                OpTicketAudit.objects.create(auditid=audit_id, type="U", method="POST", id=t.id, status=TicketStatus.IN_REPAIR.value, systemid=t.systemid, modelno=t.modelno, serialno=t.serialno,attentioncode=t.attentioncode,alertmessage=t.alertmessage,gspntechnicianid=t.gspntechnicianid,ticketno=t.ticketno,issuedtime=t.issuedtime,assigndtime=t.assigndtime,contactscheduledtime=t.contactscheduledtime,aptstartdtime=t.aptstartdtime,aptenddtime=t.aptenddtime,completedtime=t.completedtime,contactid=t.contactid,contactid2=t.contactid2,brand=t.brand,cancelreason=t.cancelreason,purchasedate=t.purchasedate,redoticketno=t.redoticketno,redoreason=t.redoreason,delayreason=t.delayreason,acknowledgedtime=t.acknowledgedtime,gspnstatus=t.gspnstatus,warehouseid=t.warehouseid,lastworepairresult=t.lastworepairresult,version=t.version,producttype=t.producttype,angerindex=t.angerindex,timezone=t.timezone,dst=t.dst,warrantystatus=t.warrantystatus,partwterm=t.partwterm,laborwterm=t.laborwterm,nspdelayreason=t.nspdelayreason,latitude=t.latitude,longitude=t.longitude,flag=t.flag,ascnumber=t.ascnumber,manufacturemonth=t.manufacturemonth,qosocsscore=t.qosocsscore,wtyexception=t.wtyexception,issueopendtime=t.issueopendtime,issueclosedtime=t.issueclosedtime,issuenoteid=t.issuenoteid,issuelatestid=t.issuelatestid,issuestatus=t.issuestatus,servicetype=t.servicetype,nspstatus=t.nspstatus,nspstatusdtime=t.nspstatusdtime,productcategory=t.productcategory,socount=t.socount,repeatcount=t.repeatcount,techid=t.techid,happycallfollowupdtime=t.happycallfollowupdtime,riskindex=t.riskindex,urgent=t.urgent,accountno=t.accountno,dplus1=t.dplus1,requestapptdtime=t.requestapptdtime,callfiredtime=t.callfiredtime,firstcontactdtime=t.firstcontactdtime,callfirestatus=t.callfirestatus,dontcheckcall=t.dontcheckcall,followupcheckcall=t.followupcheckcall,replacemodelno=t.replacemodelno,replaceserialno=t.replaceserialno,returntrackingno=t.returntrackingno,deliverytrackingno=t.deliverytrackingno,nscaccountno=t.nscaccountno,smsconsent=t.smsconsent)
            except Exception as e: #if saving failed
                print(e)
                #send an email to developer_nsp@kwitech.com
                t = ticket_no
                email = settings.TO_ADDRESS
                message = f'Ticket: {t} \n {str(e)}'
                subject = f"[SQ_API]TicketAudit : AuditID {audit_id} POST"
                sendmailoversmtp(email, subject, message)

                #creating an XML and sending a POST request to a remote URL
                NSPWSClient.RunPostWorkBizLogic(request.META.get('HTTP_KW_TOKEN'), ticket_no)
        #returning the API response
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse('WorkOrder saved')


@method_decorator(csrf_exempt, name='dispatch')
class ContactLogController(View):
    "to manage contact logs"
    def post(self, request):
        "to accept parameters in POST request to process data"
        # API: /servicequick/api/contactlog
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data
        reqcontent = request.body.decode("utf-8")
        try:
            received_json_data = json.loads(reqcontent)
        except:
            return HttpResponseBadRequest("invalid json request") 
        SimpleLogger.do_log(f"content= {reqcontent}")
        SimpleLogger.do_log(f"reqData= {received_json_data}")

        TicketNo = received_json_data.get('TicketNo')
        ContactResultCodeValue = received_json_data.get("ContactResultCode") 
        Content = received_json_data.get("Content") 
        StartDTime = received_json_data.get("StartDTime") 
        ScheduleDTime = received_json_data.get("ScheduleDTime")
        logby_value = received_json_data.get("LogBy")
        logtype_value = received_json_data.get("LogType")

        #log the request in the database
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(TicketNo), "POST", "ContactLogController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        CurrentUserID = KWAuthentication.getcurrentuser(request)

        #validate ticket no
        query = f"select * from opticket where TICKETNO = '{TicketNo}';" 
        ticket = SingleCursor.send_query(query)
        if len(ticket)==0 or type(ticket) is str:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f'Ticket was not found: {TicketNo}')            
            return JsonResponse({'message':f'Ticket was not found: {TicketNo}'}, safe=False, status=404)

        #validation continues
        try:
            c = int(ContactResultCodeValue)
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid value for ContactResultCode')            
            return JsonResponse({'message':'Invalid value for ContactResultCode'}, safe=False, status=400)
        try:
            log = int(logby_value)
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid value for LogBy')            
            return JsonResponse({'message':'Invalid value for LogBy'}, safe=False, status=400)
        try:
            log2 = int(logtype_value)
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid value for LogType')            
            return JsonResponse({'message':'Invalid value for LogType'}, safe=False, status=400)

        #creating a contact log dictionary
        contactlog = {}

        contactlog['ID'] = DBIDGENERATOR.process_id('OpBase_SEQ')
        contactlog['OpType'] = OpType.CONTACT_LOG.value
        contactlog['LogType'] = LogType.CUSTOMER_LOG.value
        contactlog['ScheduleDTime'] = ScheduleDTime
        contactlog['StartDTime'] = StartDTime
        contactlog['Status'] = 60
        contactlog['Ticket'] = TicketNo
        contactlog['Content'] = Content
        try:
            contactlog['ContactResult'] = ContactResultCode(int(ContactResultCodeValue)).value
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"ContactResultCode not valid: {ContactResultCodeValue}")            
            return JsonResponse({'message':f"ContactResultCode not valid: {ContactResultCodeValue}"}, safe=False, status=400)

        if ScheduleDTime and contactlog['Status']==ContactLogStatus.VOID.value:
            contactlog['OpDTime'] = ScheduleDTime
        #elif contactlog['FinishDTime']:   ###c# code is not clear here that from where contactlog['FinishDTime'] is getting its value
        #    contactlog['OpDTime'] = contactlog['FinishDTime']
        elif contactlog['StartDTime']:
            contactlog['OpDTime'] = contactlog['StartDTime']
        elif ScheduleDTime:
            contactlog['OpDTime'] = contactlog['ScheduleDTime']
        else:
            pass

        if int(logby_value)!=0:
            contactlog['CreatedOn'] = contactlog['StartDTime'] 
            contactlog['CreatedBy'] = int(logby_value) 

        if int(logtype_value)!=0:
            try:
                contactlog['LogType'] = LogType(int(logtype_value)).value
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='LogType not valid')            
                return JsonResponse({'message':'LogType not valid'}, safe=False, status=400)

        #saving the contact log
        try:
            OpBase.objects.create(id=contactlog['ID'], createdon=contactlog['CreatedOn'], createdby=contactlog['CreatedBy'],optype=contactlog['OpType'],status=contactlog['Status'])
            OpContactCustomer.objects.create(id=contactlog['ID'], logtype=contactlog['LogType'], scheduledtime=contactlog['ScheduleDTime'], startdtime=contactlog['StartDTime'],contactresult=contactlog['ContactResult'])
            SimpleLogger.do_log(f"Tech Note Saved : {contactlog['ID']}")
        except Exception as e:
            print(e)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Error in saving contact log')            
            return JsonResponse({'message':'Error in saving contact log'}, safe=False, status=400)

        #Send a mail if LogType is a NSC log
        if int(contactlog['LogType'])==LogType.NSC_LOG.value:
            user_name = KWAuthentication.getcurrentusername(request)
            email_title = f"[NSC_NOTICE]  {user_name} post a issue regarding ticket : {TicketNo}" 
            email_content = contactlog['Content']
            if settings.DEUG is True:
                TO_ADDRESS = settings.NSC_ADMIN_EMAIL_DEV
                FROM_ADDRESS = settings.DEVNSP_INFO_EMAIL
            else:
                TO_ADDRESS = settings.NSP_INFO_EMAIL
                FROM_ADDRESS = settings.NSC_ADMIN_EMAIL
            sendmailoversmtp(TO_ADDRESS, email_title, email_content, FROM_ADDRESS) 
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse("")

@method_decorator(csrf_exempt, name='dispatch')
class WorkScheduleController(View):
    "to update time schedule for a workorder"
    def post(self, request):
        "accept required parameters in POST to process"
        # POST api/workschedule
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data
        reqcontent = request.body.decode("utf-8")
        try:
            received_json_data = json.loads(reqcontent)
        except:
            return HttpResponseBadRequest("invalid json request") 
        SimpleLogger.do_log(f"content= {reqcontent}")
        SimpleLogger.do_log(f"reqData= {received_json_data}")

        WorkOrderID = received_json_data.get('WorkOrderID')
        AptStartDTime = received_json_data.get("AptStartDTime") 
        AptEndDTime = received_json_data.get("AptEndDTime") 
        TechnicianID = received_json_data.get("TechnicianID")

        #log the request in the database
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(WorkOrderID), "POST", "WorkScheduleController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        #Validation
        try:
            WorkOrderID = int(WorkOrderID)
        except:
            pass

        if not WorkOrderID or WorkOrderID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Value not found: WorkOrderID')            
            return JsonResponse({'message':'Value not found: WorkOrderID'}, safe=False, status=400)
        try:
            TechnicianID = int(TechnicianID)
        except:
            pass
        if AptStartDTime:
            try:
                AptStartDTime = datetime.datetime.strptime(AptStartDTime, "%Y-%m-%d %H:%M:%S")
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid AptStartDTime datetime format. Must be in yyyy/M/d HH:mm:ss')            
                return JsonResponse({'message':'Invalid AptStartDTime datetime format. Must be in yyyy/M/d HH:mm:ss'}, safe=False, status=400)
        if AptEndDTime:          
            try:
                AptEndDTime = datetime.datetime.strptime(AptEndDTime, "%Y-%m-%d %H:%M:%S")
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid AptEndDTime datetime format. Must be in yyyy/M/d HH:mm:ss')            
                return JsonResponse({'message':'Invalid AptEndDTime datetime format. Must be in yyyy/M/d HH:mm:ss'}, safe=False, status=400)
        try:
            workOrder = OpWorkOrder.objects.filter(id=WorkOrderID).values()[0]
            op = OpBase.objects.filter(id=WorkOrderID).values()[0]
            workOrder.update(op) #updating the dict workOrder with dict from OpBase
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {WorkOrderID}")            
            return JsonResponse({'message':f"Work order not found: {WorkOrderID}"}, safe=False, status=400)
        try:    
            technician = getuserinfo(TechnicianID)['UserName']
        except:
            technician = None
        SimpleLogger.do_log(f"technician={technician}")
        #Saving WorkOrder and Ticket 
        WorkOrderAdditionalInfoVO.UpdateWorkOrderSchedule(workOrder, AptStartDTime, AptEndDTime, TechnicianID, CurrentUserID)
        SimpleLogger.do_log(f"Work order schedule was updated: {workOrder['id']}")
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse("Work Order Schedule Updated")


class InventorySurveyController(View):
    "to check parts inventory"
    def get(self, request):
        "accept parameters in GET to process"
        # GET api/inventorysurvey
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        if authstat is False:
            return JsonResponse({'message':'invalid headers'}, status=400)
        #Decoding/logging the GET request
        PSID = request.GET.get('PSID')
        SurveyLocationCode = request.GET.get('SurveyLocationCode')
        token = request.META.get('HTTP_KW_TOKEN')
        reqData = f"PSID : {PSID}, SurveyLocationCode : {SurveyLocationCode}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(PSID), "GET", "InventorySurveyController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        
        #Validating
        if PSID[0:2]=='PS':
            subPSID = PSID[2:]
        else:
            subPSID = PSID
        try:
            iPSID = int(subPSID)
        except:
            iPSID = 0
        partSerial = PartSupport.GetPartSerial(iPSID)    
        #Processing the information
        DELIMETER = '|' 
        if partSerial is None:
            SimpleLogger.do_log(f"PartSerial '{PSID}' was not found.", "error")
            return HttpResponseServerError(f"PartSerial '{PSID}' was not found.")
        else:
            sWarehouseID = ''
            sLocationCode = ''
            location = None
            if DELIMETER in SurveyLocationCode:
                loc = SurveyLocationCode.split(DELIMETER)
                if loc[0].upper()=='NULL' or loc[0] is None:
                    sWarehouseID = partSerial['WarehouseID']
                else:
                    sWarehouseID = loc[0]
                sLocationCode = loc[1]
            else:
                sWarehouseID = partSerial['WarehouseID']
                sLocationCode = SurveyLocationCode 
            location = NspLocations.objects.filter(warehouseid=sWarehouseID, locationcode=sLocationCode) 
            if not location.exists():
                SimpleLogger.do_log(f"Location {SurveyLocationCode} does not exist in this warehouse.", "error")
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Location {SurveyLocationCode} does not exist in this warehouse.")            
                return JsonResponse({'message':f"Location {SurveyLocationCode} does not exist in this warehouse."}, safe=False, status=400)
            else:
                partSerial['SurveyDTime'] = timezone.now()
                partSerial['SurveyBy'] = CurrentUserID
                partSerial['SurveyLocationCode'] = location[0].locationcode 
                # SavePartSerial
                if partSerial['CreatedOn'] is None:
                    NspPartSerials.objects.filter(psid=partSerial['PSID']).update(surveydtime=partSerial['SurveyDTime'], surveyby=partSerial['SurveyBy'], surveylocationcode=partSerial['SurveyLocationCode'], createdon=timezone.now(), createdby=CurrentUserID)
                else:
                    NspPartSerials.objects.filter(psid=partSerial['PSID']).update(surveydtime=partSerial['SurveyDTime'], surveyby=partSerial['SurveyBy'], surveylocationcode=partSerial['SurveyLocationCode'], updatedon=timezone.now(), updatedby=CurrentUserID)
                # SavePartSerialAudit
                partSerial['AuditID'] = DBIDGENERATOR.process_id('NSPPartSerialsAudit_SEQ')
                partSerial['Method'] = 'GET'
                PartSupport.SavePartSerialAudit(partSerial, CurrentUserID)
        partSerial = PartSupport.GetPartSerial(iPSID) #re-query NspPartSerials for updated info
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)        
        return JsonResponse(partSerial, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class WorkOrdersController(View):
    "to get details of a workorder item"
    def get(self, request, id):
        "to accept WorkOrderID in GET to process"
        SimpleLogger.do_log(f">>> Get()...{id}", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'id':id}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(id), "GET", "WorkOrdersController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)    
        #Check WorkOrder by using WorkOrderID
        try:
            WorkOrderID = int(id)
        except:
            WorkOrderID = id
        SQService = SchedulesService
        if type(WorkOrderID) is int:
            workOrder = SQService.GetWorkOrder(WorkOrderID, CurrentUserID)
        else:
            workOrder = None    
        #If workOrder not found, try to check using WorkOrderNumber
        if workOrder is None:
            workOrder = SQService.GetWorkOrderByWorkOrderNo(id, CurrentUserID)
        SimpleLogger.do_log(f">>> workOrder={workOrder}", "debug")
        if workOrder is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"Work order not found: {id}")            
            return JsonResponse({'message':f"Work order not found: {id}"}, safe=False, status=404)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)     
        return JsonResponse(workOrder, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class TwilioDebuggerController(View):
    "to save Twilio error"
    def post(self, request):
        "accept payload in POST to process" 
        # POST servicequick/api/TwilioDebugger
        SimpleLogger.do_log(">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        SimpleLogger.do_log(f"content= {content}", "debug")
        try:
            payLoad = received_json_data.get("payLoad")
        except:
            return HttpResponseBadRequest("parameter payLoad not found")

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, payLoad['resource_sid'], "POST", "TwilioDebuggerController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)        
       
        # Defining some constants
        E30001 = "Queue overflow"
        E30002 = "Account suspended"
        E30003 = "Unreachable destination handset"
        E30004 = "Message blocked"
        E30005 = "Unknown destination handset"
        E30006 = "Landline or unreachable carrier"
        E30007 = "Carrier violation"
        E30008 = "Unknown error"
        WELCOME_SMS = "Welcome SMS"
        MANAGER_LOG = "Could not send TXT. Please make outbound call. This does not mean to cancel the ticket"
        # Getting ContactLog
        contactlog = ContactSupport.GetContactLogBySID(payLoad['resource_sid'])
        if contactlog is not None:
            try:
                TicketID = OpBase.objects.get(id=contactlog['ID']).pid
                ticket = ContactSupport.GetTicket(TicketID)
            except Exception as e:
                print(e)
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='CANNOT find contact log.')            
                return JsonResponse({'message':'CANNOT find contact log.'}, safe=False, status=404)

        sPreFix = ""
        if contactlog is not None:
            contactlog['ContactResult'] = ContactResultCode.ERR.value
            sPreFix = "Error " + payLoad['error_code']
            if payLoad['error_code']=="30001":
                sPreFix += ": " + E30001 
            elif payLoad['error_code']=="30002":
                sPreFix += ": " + E30002
            elif payLoad['error_code']=="30003":
                sPreFix += ": " + E30003
                ticket['SMSConsent'] = False
            elif payLoad['error_code']=="30004":
                sPreFix += ": " + E30004
                ticket['SMSConsent'] = False
            elif payLoad['error_code']=="30005":
                sPreFix += ": " + E30005                  
                ticket['SMSConsent'] = False
            elif payLoad['error_code']=="30006":
                sPreFix += ": " + E30006                  
                ticket['SMSConsent'] = False
            elif payLoad['error_code']=="30007":
                sPreFix += ": " + E30007                  
                ticket['SMSConsent'] = False
            elif payLoad['error_code']=="30008":
                sPreFix += ": " + E30008
            else:
                pass
            contactlog['Content'] = sPreFix + "\r\n" + contactlog['Content']
            #updating contactlog now
            OpContactCustomer.objects.filter(sid=payLoad['resource_sid'], logtype=LogType.SMS_LOG.value).update(contactresult=contactlog['ContactResult'], contactlog=contactlog['Content'])
            OpBase.objects.filter(id=contactlog['ID']).update(updatedon=timezone.now(), updatedby=CurrentUserID)
            #updating ticket
            ticket['WorkOrders'] = ContactSupport.GetWorkOrdersByTicketID(TicketID)
            if contactlog['FollowUpReason']==WELCOME_SMS and len(ticket['WorkOrders'])==1 and ticket['WorkOrders'][0]['Status']==WorkOrderStatus.SCHEDULED.value:
                ticket['WorkOrders'][0]['Status'] = WorkOrderStatus.VOID.value 
                ticket['WorkOrders'][0]['AuditID'] = DBIDGENERATOR.process_id('OpWorkOrderAudit_SEQ')
                ticket['WorkOrders'][0]['Method'] = 'POST'
                #Saving WorkOrder
                #Defining some values
                wo_status = ticket['WorkOrders'][0]['Status']
                WorkOrderID = OpBase.objects.get(id=contactlog['ID']).id
                #checking status of a record in the OPBASE table and if found, update the record accordingly
                check_query = OpBase.objects.filter(id=WorkOrderID)
                original_pid_value = None 
                if check_query.exists():
                    try:
                        original_pid_value = OpTicket.objects.get(id=check_query[0].pid).id
                    except:
                        original_pid_value = None
                    if check_query[0].createdon is None:
                        check_query.update(createdon=timezone.now(), createdby=CurrentUserID, status=wo_status, originalpid=original_pid_value)
                    else:
                        check_query.update(updatedon=timezone.now(), updatedby=CurrentUserID, status=wo_status)                   
                #Updating details into the opworkorder table 
                audit_id = ticket['WorkOrders'][0]['AuditID']
                #updating OpworkOrder table and copying data to the table OPworkOrderAudit       
                try:
                    w = OpWorkOrder.objects.get(id=WorkOrderID) #getting the updated workorder record
                    OpWorkOrderAudit.objects.create(auditid=audit_id, method='POST', type="U", id=w.id, auditdtime=timezone.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=wo_status, pid=original_pid_value) 
                except Exception as e:
                    #send an email if updation/save failed 
                    print(e)   
                    email_title = f"[SQ_API]WorkOrderAudit : AuditID {audit_id}, POST" 
                    email_content = f"WorkOrder: {str(WorkOrderID)} \n {e}"
                    TO_ADDRESS = settings.NSC_ADMIN_EMAIL
                    FROM_ADDRESS = settings.NSP_INFO_EMAIL
                    sendmailoversmtp(TO_ADDRESS, email_title, email_content, FROM_ADDRESS)
                SimpleLogger.do_log(f"Work order saved:  {WorkOrderID}")
            #creating new records for OpBase and OPContactCustomer
            ContactSupport.createManagerLog(ticket, MANAGER_LOG, CurrentUserID)
            #Saving Ticket
            #creating new record in OPTicketAudit table
            ticket_audit_id = DBIDGENERATOR.process_id('OpTicketAudit_SEQ')
            t = OpTicket.objects.get(id=ticket['ID']) 
            try:
                op = OpBase.objects.filter(pid=t.id)[0]
                OpTicketAudit.objects.create(auditid=ticket_audit_id, type='U', method='POST', id=t.id, status=op.status,systemid=t.systemid,modelno=t.modelno,serialno=t.serialno,attentioncode=t.attentioncode,alertmessage=t.alertmessage,gspntechnicianid=t.gspntechnicianid,ticketno=t.ticketno,issuedtime=t.issuedtime,assigndtime=t.assigndtime,contactscheduledtime=t.contactscheduledtime,aptstartdtime=t.aptstartdtime,aptenddtime=t.aptenddtime,completedtime=t.completedtime,contactid=t.contactid,contactid2=t.contactid2,brand=t.brand,cancelreason=t.cancelreason,purchasedate=t.purchasedate,purchasedate2=t.purchasedate2,redoticketno=t.redoticketno,redoreason=t.redoreason,delayreason=t.delayreason,acknowledgedtime=t.acknowledgedtime,gspnstatus=t.gspnstatus,warehouseid=t.warehouseid,lastworepairresult=t.lastworepairresult,version=t.version,producttype=t.producttype,angerindex=t.angerindex,timezone=t.timezone,dst=t.dst,warrantystatus=t.warrantystatus,partwterm=t.partwterm,laborwterm=t.laborwterm,nspdelayreason=t.nspdelayreason,latitude=t.latitude,longitude=t.longitude,flag=t.flag,ascnumber=t.ascnumber,manufacturemonth=t.manufacturemonth,qosocsscore=t.qosocsscore,wtyexception=t.wtyexception,issueopendtime=t.issueopendtime,issueclosedtime=t.issueclosedtime,issuenoteid=t.issuenoteid,issuelatestid=t.issuelatestid,issuestatus=t.issuestatus,servicetype=t.servicetype,nspstatus=t.nspstatus,nspstatusdtime=t.nspstatusdtime,productcategory=t.productcategory,socount=t.socount,repeatcount=t.repeatcount,techid=t.techid,happycallfollowupdtime=t.happycallfollowupdtime,riskindex=t.riskindex,urgent=t.urgent,accountno=t.accountno,dplus1=t.dplus1,requestapptdtime=t.requestapptdtime,callfiredtime=t.callfiredtime,firstcontactdtime=t.firstcontactdtime,callfirestatus=t.callfirestatus,dontcheckcall=t.dontcheckcall,followupcheckcall=t.followupcheckcall,replacemodelno=t.replacemodelno,replaceserialno=t.replaceserialno,returntrackingno=t.returntrackingno,deliverytrackingno=t.deliverytrackingno,nscaccountno=t.nscaccountno,smsconsent=t.smsconsent)
                OpBase.objects.filter(id=op.id).update(updatedon=datetime.datetime.today(), updatedby=CurrentUserID)
            except Exception as e:
                print(e)
                #send an email
                email_title = f"[SQ_API]TicketAudit : AuditID {ticket_audit_id}, POST" 
                email_content = f"TicketDetails: {t} \n {e}"
                to_address = settings.NSC_ADMIN_EMAIL
                from_address = settings.NSP_INFO_EMAIL
                sendmailoversmtp(to_address, email_title, email_content, from_address)
            #Sending XML request
            NSPWSClient.RunPostWorkBizLogic("", ticket['TicketNo'])
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return HttpResponse("Twilio Error saved.")
        else:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='CANNOT find contact log.')            
            return JsonResponse({'message':'CANNOT find contact log.'}, safe=False, status=404)

class InventoryListController(View):
    "to generate a list of inventory available"
    def get(self, request):
        "accept warehouseId or locationCode/partNo in GET to process"
        # GET servicequick/api/inventorylist?warehouseId=1&locationCode=A&partNo=B
        SimpleLogger.do_log(">>> Get()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Logging and checking passed parameters
        warehouseId = request.GET.get("warehouseId")
        locationCode = request.GET.get("locationCode")
        partNo = request.GET.get("partNo")
        
        SimpleLogger.do_log(f"warehouseId={warehouseId}", "debug") 
        SimpleLogger.do_log(f"locationCode={locationCode}", "debug")
        SimpleLogger.do_log(f"partNo={partNo}", "debug")
        reqData = f"warehouseId : {warehouseId}, locationCode : {locationCode}, partNo : {partNo}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, warehouseId, "GET", "InventoryListController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        if not warehouseId:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter required: warehouseId')            
            return JsonResponse({'message':'Parameter required: warehouseId'}, safe=False, status=400)
        
        #Processing the data
        if partNo and partNo[:2]=='PS':
            try:
                psid = int(partNo[2:])
                partSerial = PartSupport.GetPartSerial(psid)
                if partSerial is not None:
                    partNo = partSerial['PartNo']
                    SimpleLogger.do_log(f"partNo={partNo} (PS{psid})", "debug")
                else:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Part not found by PSID: {partNo}")            
                    return JsonResponse({'message':f"Part not found by PSID: {partNo}"}, safe=False, status=400)
            except Exception as e:
                SimpleLogger.do_log(str(e), "debug")
        if not locationCode and not partNo:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter required: LocationCode or PartNo')            
            return JsonResponse({'message':'Parameter required: LocationCode or PartNo'}, safe=False, status=400)
        itemList = InventorySupport.GetInventoryList(warehouseId, locationCode, partNo)
        # Response Data
        resultList = {}
        resultList['WarehouseID'] = warehouseId
        resultList['LocationCode'] = locationCode
        resultList['PartNo'] = partNo
        resultList['ListSize'] = len(itemList)
        resultList['List'] = itemList
        resultList['LogID'] = BaseApiController.getlogid('GET', 'InventoryListController', CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class MmsController(View):
    "to receive MMS from the customers"
    def post(self, request, numMedia=1):
        "accept parameters in POST to process" 
        # POST servicequick/api/mmscontroller
        SimpleLogger.do_log(">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        #Getting the received parameters
        SmsSid = request.POST.get('SmsSid')
        Body = request.POST.get("Body")
        MessageStatus = request.POST.get("MessageStatus")
        AccountSid = request.POST.get("AccountSid")
        From = request.POST.getlist("From")
        To = request.POST.get("To")
        FromCity = request.POST.get("FromCity")
        FromState = request.POST.get("FromState")
        FromZip = request.POST.get("FromZip")
        FromCountry = request.POST.get("FromCountry")
        ToCity = request.POST.get("ToCity")
        MediaUrl = request.POST.getlist("MediaUrl")
        mediacontenttype = request.POST.getlist("mediacontenttype")
        #Defining some constants
        SAVEPATH = settings.MEDIA_ROOT + '/pictures'
        MMS_RECEIVED = "Received picture(s) from the customer" 
        #Logging the request
        sPhone = From
        sMessage = Body
        fromAddr = settings.NSP_INFO_EMAIL
        reqData = json.dumps(request.POST)
        jsonString = json.dumps(request.POST)
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request)
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(sPhone), 'POST', 'MmsController', jsonString, callerApp, AppVersion)
        if authstat is not True:
            return JsonResponse(authstat, status=401)
        #Processing the data for every phone request
        for phone in From:
            if len(str(phone)) < 10:
                email_title = "[MMS]" + phone
                email_content = "PhoneNo is invalid"
                to_address = settings.NSC_ADMIN_EMAIL
                sendmailoversmtp(to_address, email_title, email_content, fromAddr)
        for i in range(0, numMedia):
            try:
                mediaUrl = MediaUrl[i]
                contenttype = mediacontenttype[i]
                GetDefaultExtension = mimetypes.guess_extension(contenttype, strict=False)
                GetMediaFileName = os.path.basename(mediaUrl).split(".")[0] + GetDefaultExtension
                filepathname = SAVEPATH + '/' + GetMediaFileName
                FileActions.DownloadFromURL(mediaUrl, filepathname)
                ticket = ContactSupport.GetTicketByMobile(sPhone[i])
                if ticket is not None:
                    iPictureID = DBIDGENERATOR.process_id('Pictures_SEQ')
                    picture = PictureTrans.SaveTicketPicture(request,ticket,filepathname, iPictureID)
                    if ticket['SystemID']==SystemIDEnum.GSPN.value:
                        wsResult = NSPWSClient.SyncTicketPictureToGSPN("", iPictureID) #sync to GSPN
                        try:
                            wsreserror = get_xml_node(wsResult.text, "ERROR")
                            if wsreserror:
                                email_title = "[MMS]" + sPhone[i]
                                email_content = wsreserror
                                to_address = settings.NSC_ADMIN_EMAIL
                                sendmailoversmtp(to_address, email_title, email_content, fromAddr)
                        except Exception as e:
                            email_title = "[MMS]" + sPhone[i]
                            email_content = str(e)
                            to_address = settings.NSC_ADMIN_EMAIL
                            sendmailoversmtp(to_address, email_title, email_content, fromAddr)
            except Exception as e:
                print(e)                
        #Running function for Call Fire Text
        try:
            if numMedia > 0 and not sMessage:
                sMessage = MMS_RECEIVED
                wsResult = NSPWSClient.SyncTicketPictureToGSPN("", iPictureID) #sync to GSPN
                try:
                    wsreserror = get_xml_node(wsResult.text, "ERROR")
                    if wsreserror:
                        email_title = "[MMS]" + sPhone[i]
                        email_content = wsreserror
                        to_address = settings.NSC_ADMIN_EMAIL
                        sendmailoversmtp(to_address, email_title, email_content, fromAddr)
                except:
                    pass
        except Exception as e:
            email_title = "[MMS]" + str(sPhone)
            email_content = str(e)
            to_address = settings.NSC_ADMIN_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, fromAddr)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, "Twilio MMS saved.")    
        return HttpResponse("Twilio MMS saved.")                                                                                                           
                                                                


                              
                           

                        






            




        

