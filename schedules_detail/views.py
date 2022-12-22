import json, datetime
from nsp_user.support import DjangoOverRideJSONEncoder
from django.http.response import HttpResponseServerError
from django.utils import timezone
from django.views import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from nsp_user.authentication import KWAuthentication
from functions.smtpgateway import sendmailoversmtp
from django.http import HttpResponseNotFound, JsonResponse, HttpResponseBadRequest, HttpResponse
from functions.kwlogging import SimpleLogger, AdvancedLogger, BaseApiController
from functions.querymethods import SingleCursor, DBIDGENERATOR
from functions.xmlfunctions import get_xml_node
from schedules_list_map.schedules import WorkOrderStatus, UsageType, PartType, LocationType, ReserveStatus, WorkOrderAdditionalInfoVO, RepairResultCodeEnum, RepairFailCodeEnum, PaymentTypeEnum, OpType, LogType, ContactResultCode, NoteTypeEnum, GspnWebServiceClient
from schedules_list_map.models import OpWorkOrder, OpWorkOrderAudit, OpBase, OpTicket, OpTicketAudit, OpContactCustomer
from schedules_detail.models import NspPartDetails, GetPartMaster, NspPartSerials, NspLocations, NspPartDetailsAudit, NspWareHouses, NspDocs, OpNote, NspAccounts, NspCompanyContacts, NspAddresses, NspPartMasters
from schedules_detail.soap_actions import XMLActions
from schedules_detail.schedules2 import SchedulesService, PictureTrans, TechEmailService, ReportGeneration
from nsp_user.models import Nspusers, getuserinfo, getboolvalue
from nsp_user.support import NSPSupport
from schedules_detail.support import PartSupport, TicketSupport
# Create your views here.


@method_decorator(csrf_exempt, name='dispatch')
class RepairStartController(View):
    "saves a work order"
    def post(self, request):
        "accept values in POST to process"
        #API - /servicequick/api/repairstart
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data
        content = request.body.decode("utf-8")
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        SimpleLogger.do_log(f"content = {content}")
        WorkOrderID = received_json_data.get("WorkOrderID") 
        StartDTime = received_json_data.get("StartDTime")
        Odometer = received_json_data.get("Odometer")

        SimpleLogger.do_log(f"reqData = {received_json_data}")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, WorkOrderID, "POST", "RepairStartController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        #Validation
        if WorkOrderID==0 or not WorkOrderID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Value not found: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Value not found: {str(WorkOrderID)}"}, safe=False, status=400)
        SQService = SchedulesService
        resworkorder = SQService.GetWorkOrder(int(WorkOrderID))
        if resworkorder is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work Order not found: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Work Order not found: {str(WorkOrderID)}"}, safe=False, status=400)
        if StartDTime is None or not StartDTime:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Value not found: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Value not found: {str(WorkOrderID)}"}, safe=False, status=400)
        try:
            StartDTime = datetime.datetime.strptime(StartDTime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid StartDtime value: {StartDTime}, must be in format yyyy-MM-dd HH:mm:ss")            
            return JsonResponse({'message':f"Invalid StartDtime value: {StartDTime}, must be in format yyyy-MM-dd HH:mm:ss"}, safe=False, status=400)
        SimpleLogger.do_log(f">>> workOrder= {str(WorkOrderID)}")
        if WorkOrderStatus(int(resworkorder['Status'])).name=='CLOSED':
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='410', errMsg=f"Work order has already been closed: {WorkOrderID}")            
            return JsonResponse({'message':f"Work order has already been closed: {WorkOrderID}"}, safe=False, status=410)
        query_ticket = f"select * from opworkorder w, opticket t, obase b where w.ID = b.ID and t.ID = b.PID and w.ID = {int(WorkOrderID)};"
        res = SingleCursor.send_query(query_ticket)
        if type(res) is str or len(res)==0:
            ticket = 'ticket not found'
        else:
            ticket = res['TICKETNO']
        SimpleLogger.do_log(f"Ticket= {str(ticket)}") 

        #Defining some values
        wo_status = WorkOrderStatus.PROCESSING.value
        #checking status of a record in the OPBASE table and if found, update the record accordingly
        check_query = OpBase.objects.filter(id=int(WorkOrderID))
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
        audit_id = DBIDGENERATOR.process_id('OpWorkOrderAudit_SEQ')
        #updating OpworkOrder table and copying data to the table OPworkOrderAudit       
        try:
            OpWorkOrder.objects.filter(id=int(WorkOrderID)).update(startdtime=StartDTime, odometer=Odometer)
            w = OpWorkOrder.objects.get(id=int(WorkOrderID)) #getting the updated workorder record
            OpWorkOrderAudit.objects.create(auditid=audit_id, method='POST', type="U", id=w.id, auditdtime=timezone.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=wo_status, pid=original_pid_value) 
        except Exception as e:
            #send an email if updation/save failed 
            print(e)   
            email_title = f"[SQ_API]WorkOrderAudit : AuditID {audit_id}, POST" 
            email_content = f"WorkOrder: {str(WorkOrderID)} \n {e}"
            TO_ADDRESS = settings.NSC_ADMIN_EMAIL
            FROM_ADDRESS = settings.NSP_INFO_EMAIL
            sendmailoversmtp(TO_ADDRESS, email_title, email_content, FROM_ADDRESS)
        if WorkOrderStatus(int(resworkorder['Status'])).name=='CLOSED':
            OpTicket.objects.filter(id=int(WorkOrderID)).update(lastworepairresult=resworkorder['RepairResultCode'])
        SimpleLogger.do_log(f"Work order saved:  {WorkOrderID}")
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse("WorkOrder saved.")

@method_decorator(csrf_exempt, name='dispatch')
class RepairDetailsController(View):
    "saves work order"
    def post(self, request):
        "accepts values in POST to process"
        #API -  /servicequick/api/RepairDetails
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data
        content = request.body.decode("utf-8")
        SimpleLogger.do_log(f"content = {content}")
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        SimpleLogger.do_log(f"reqData = {received_json_data}")
        WorkOrderID = received_json_data.get("WorkOrderID") 
        DefectCode = received_json_data.get("DefectCode")
        DefectSymptom = received_json_data.get("DefectSymptom")
        RepairCode = received_json_data.get("RepairCode")
        RepairAction = received_json_data.get("RepairAction")
        Note = received_json_data.get("Note")

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, WorkOrderID, "POST", "RepairDetailsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        
        #Validation
        if WorkOrderID==0 or not WorkOrderID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Value not found: {WorkOrderID}")            
            return JsonResponse({'message':f"Value not found: {WorkOrderID}"}, safe=False, status=400)

        SimpleLogger.do_log(f">>> workOrder= {WorkOrderID}")

        SQService = SchedulesService
        resworkorder = SQService.GetWorkOrder(int(WorkOrderID))
        if resworkorder is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work Order not found: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Work Order not found: {str(WorkOrderID)}"}, safe=False, status=400)
        if int(resworkorder['Status']) < WorkOrderStatus.PROCESSING.value:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='406', errMsg=f"Repair has not been started: {str(WorkOrderID)}")            
            return JsonResponse({'message':f"Repair has not been started: {str(WorkOrderID)}"}, safe=False, status=406)

        #Preparing for DB updation/save, define the required variables
        WorkOrder = {}
        WorkOrder['DefectCode'] = DefectCode
        WorkOrder['RepairCode'] = RepairCode
        WorkOrder['RepairAction'] = RepairAction
        WorkOrder['DefectSymptom'] = DefectSymptom
        WorkOrder['Note'] = Note

        if RepairAction is not None and len(RepairAction) > 255:
            WorkOrder['RepairAction'] = RepairAction[:255]

        if DefectSymptom is not None and len(DefectSymptom) > 255:
            WorkOrder['DefectSymptom'] = DefectSymptom[:255]

        #Defining some values
        audit_id = DBIDGENERATOR.process_id('OpWorkOrderAudit_SEQ')
        wo_status = WorkOrderStatus.PROCESSING.value
        #checking status of a record in the OPBASE table and if found, update the record accordingly
        check_query = OpBase.objects.filter(id=int(WorkOrderID))
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
        #Updating details into the workorder table and Copying workorder data to opworkorderaudit table    
        try:
            OpWorkOrder.objects.filter(id=int(WorkOrderID)).update(defectcode=WorkOrder['DefectCode'], repaircode=WorkOrder['RepairCode'], repairaction=WorkOrder['RepairAction'], defectsymptom=WorkOrder['DefectSymptom'], note=WorkOrder['Note'])
            w = OpWorkOrder.objects.get(id=int(WorkOrderID)) #getting the updated workorder record
            OpWorkOrderAudit.objects.create(auditid=audit_id, method='POST', type="U", id=w.id, auditdtime=timezone.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=wo_status, pid=original_pid_value)
        except Exception as e:    
            #send an email
            email_title = f"[SQ_API]WorkOrderAudit : AuditID {audit_id}, POST" 
            email_content = f"WorkOrder: {str(WorkOrderID)} \n {e}"
            to_address = settings.NSC_ADMIN_EMAIL
            from_address = settings.NSP_INFO_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, from_address)
        SimpleLogger.do_log(f"Work order saved:  {WorkOrderID}")
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse("WorkOrder saved.")

@method_decorator(csrf_exempt, name='dispatch')
class PartsUsageController(View):
    "details saved about parts usage"
    def post(self, request):
        "accept values in POST to process"
        #API : /servicequick/api/PartsUsage
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data
        content = request.body.decode("utf-8")
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")

        SimpleLogger.do_log(f"content = {content}")
        WorkOrderID = received_json_data.get("WorkOrderID") 
        ReqPartDetails = received_json_data.get("PartDetails")

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, WorkOrderID, "POST", "PartsUsageController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        #Validation
        if not WorkOrderID or WorkOrderID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Value not found: WorkOrderID')            
            return JsonResponse({'message':'Value not found: WorkOrderID'}, safe=False, status=400)

        SimpleLogger.do_log(f">>> workOrder= {WorkOrderID}") 

        check_work_order = OpWorkOrder.objects.filter(id=int(WorkOrderID))
        if not check_work_order.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {WorkOrderID}")            
            return JsonResponse({'message':f"Work order not found: {WorkOrderID}"}, safe=False, status=400)

        #setting variables
        partCost = 0
        laborCost = 0
        partdetail_dict = {}
        part_details_data = NspPartDetails.objects.filter(partdetailid=ReqPartDetails[0]['PartDetailID']) 
        for wo in check_work_order:
            if part_details_data.exists():
                partdetail = NspPartDetails.objects.get(partdetailid=ReqPartDetails[0]['PartDetailID'])
                if UsageType(ReqPartDetails[0]['Usage']).name!='UNKNOWN':
                    if wo.aptstartdtime is not None and wo.aptstartdtime==datetime.date.today() or UsageType(partdetail.usage)=='UNKNOWN':
                        partdetail_dict['USAGE'] = ReqPartDetails[0]['Usage']
                        if UsageType(ReqPartDetails[0]['Usage']).name=='USED' and partdetail.unitprice!=0:
                            pm = GetPartMaster(partdetail.partno)
                            if pm.get('data')==0 or PartType(pm.get('data')['parttype']).name=='PART':
                                partCost += partdetail.unitprice
                            else:
                                laborCost += partdetail.unitprice
                if partdetail.psid==0 or ReqPartDetails[0]['PSID'] > 0:
                    partdetail_dict['PSID'] = ReqPartDetails[0]['PSID']
                partdetail_dict['AUDITID'] = DBIDGENERATOR.process_id('NSPPartDetailsAudit_SEQ')
                partdetail_dict['METHOD'] = 'POST'
                break

        #checking requested part details
        for reqDetail in ReqPartDetails:
            if reqDetail['PartDetailID']==0: #Adding New Parts
                workorder = OpWorkOrder.objects.get(id=int(WorkOrderID))
                ps = NspPartSerials.objects.get(psid=reqDetail['PSID']) #getting PART serials
                if workorder.partwarehouseid!=ps.warehouseid:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"This part cannot be used (part location): {ps.partno}")            
                    return JsonResponse({'message':f"This part cannot be used (part location): {ps.partno}"}, safe=False, status=400)

                lo = NspLocations.objects.get(warehouseid=ps.warehouseid, locationcode=ps.locationcode) 
                if lo.locationtype!=LocationType.VEHICLE.value:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"This part cannot be used (location type): {ps.partno}")            
                    return JsonResponse({'message':f"This part cannot be used (location type): {ps.partno}"}, safe=False, status=400)

                partdetail_dict['PSID'] = reqDetail['PSID']
                pm = GetPartMaster(ps.partno)
                partdetail_dict['PartDetailID'] = DBIDGENERATOR.process_id('NSPPartDetails_SEQ')
                partdetail_dict['PartDescription'] = pm.get('data')['partdescription']
                partdetail_dict['PartNo'] = ps.partno
                partdetail_dict['PartID'] = 'N/A'
                partdetail_dict['Qty'] = 1
                partdetail_dict['ReserveStatus'] = ReserveStatus.CONFIRMED.value
                partdetail_dict['Usage'] = reqDetail['Usage']
                partdetail_dict['WorkOrder'] = workorder
                partdetail_dict['AUDITID'] = DBIDGENERATOR.process_id('NSPPartDetailsAudit_SEQ')
                partdetail_dict['METHOD'] = 'POST'
                #creating new record for partdetails in the table NSPPARTDETAILS and NSPPARTDETAILSAUDIT
                try:
                    NspPartDetails.objects.create(partdetailid=partdetail_dict['PartDetailID'], opworkorderid=WorkOrderID, partid=partdetail_dict['PartID'],partdesc=partdetail_dict['PartDescription'],partno=partdetail_dict['PartNo'],qty=partdetail_dict['Qty'],reservestatus=partdetail_dict['ReserveStatus'],usage=partdetail_dict['Usage'],createdon=datetime.date.today(),createdby=CurrentUserID,psid=partdetail_dict['PSID'])
                    NspPartDetailsAudit.objects.create(auditid=partdetail_dict['AUDITID'], type='T', auditee=1, partdetailid=partdetail_dict['PartDetailID'], opworkorderid=WorkOrderID, partid=partdetail_dict['PartID'],createdon=datetime.date.today(),createdby=CurrentUserID,psid=partdetail_dict['PSID'],method=partdetail_dict['METHOD'])
                except Exception as e:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Adding New Parts failed: {str(e)}")            
                    return JsonResponse({'message':f"Adding New Parts failed: {str(e)}"}, safe=False, status=400)
                #make a soap request to a remote server and get the result
                wsResult = XMLActions.move_part(CurrentUserID, reqDetail['PSID'], ps.warehouseid, workorder.SQBOX, "On site part useage")
                SimpleLogger.do_log(f"result= {wsResult}")
                if wsResult['ErrorMsg']!="":
                    pass
                    #return HttpResponseServerError(f"InternalServerError: {wsResult['ErrorMsg']}")

        #preparing opworkorder updation
        workorder_dict = {}
        workorder_dict['PartCost'] = partCost
        workorder_dict['LaborCost'] = laborCost
        workorder_dict['AuditID'] = DBIDGENERATOR.process_id('OpWorkOrderAudit_SEQ')
        workorder_dict['Method'] = 'POST'
        OpWorkOrder.objects.filter(id=int(WorkOrderID)).update(partcost=workorder_dict['PartCost'],laborcost=workorder_dict['LaborCost'])
        audit_id = workorder_dict['AuditID']
        try:
            op = OpBase.objects.get(id=int(WorkOrderID))
            try:
                original_pid_value = OpTicket.objects.get(id=op.pid).id
            except:
                original_pid_value = None
            if op.createdon is None or op.createdon=='':
                OpBase.objects.filter(id=int(WorkOrderID)).update(createdon=timezone.now(), createdby=CurrentUserID, originalpid=original_pid_value)
            else:
                OpBase.objects.filter(id=int(WorkOrderID)).update(updatedon=timezone.now(), updatedby=CurrentUserID)    
            w = OpWorkOrder.objects.get(id=int(WorkOrderID)) #getting the updated workorder record
            OpWorkOrderAudit.objects.create(auditid=audit_id, method='POST', type="U", id=w.id, auditdtime=timezone.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=op.status, pid=original_pid_value)
        except Exception as e:    
            #send an email
            email_title = f"[SQ_API]WorkOrderAudit : AuditID {audit_id}, POST" 
            email_content = f"WorkOrder: {str(WorkOrderID)} \n {e}"
            to_address = settings.NSC_ADMIN_EMAIL
            from_address = settings.NSP_INFO_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, from_address)
        SimpleLogger.do_log(f"Work order saved:  {WorkOrderID}")
        #preparing for part details updation
        nsp_part_audit_id = DBIDGENERATOR.process_id('NSPPartDetailsAudit_SEQ')
        try:
            nsp_part_details = NspPartDetails.objects.filter(partdetailid=ReqPartDetails[0]['PartDetailID'])
            if nsp_part_details.exists():
                pd = NspPartDetails.objects.get(partdetailid=ReqPartDetails[0]['PartDetailID'])
                if pd.usage==UsageType.USED.value:
                    try:
                        partCost += pd.unitprice
                    except:
                        pass    
                if pd.createdon is None or pd.createdon=='':
                    NspPartDetails.objects.filter(partdetailid=ReqPartDetails[0]['PartDetailID']).update(createdon=datetime.date.today(),createdby=CurrentUserID)
                else:
                    NspPartDetails.objects.filter(partdetailid=ReqPartDetails[0]['PartDetailID']).update(updatedon=datetime.date.today(),updatedby=CurrentUserID)
                #creating new record in NSPPARTDETAILSAUDIT table
                NspPartDetailsAudit.objects.create(auditid=nsp_part_audit_id, type='T', auditee=1, auditdtime=timezone.now(), method='POST', partdetailid=pd.partdetailid, partid=pd.partid, opworkorderid=pd.opworkorderid, createdon=pd.createdon,createdby=pd.createdby,updatedon=pd.updatedon,updatedby=pd.updatedby,qty=pd.qty,unitprice=pd.unitprice,refno=pd.refno,trackingno=pd.trackingno,parteta=pd.parteta,partno=pd.partno,partdesc=pd.partdesc,usage=pd.usage,reservestatus=pd.reservestatus,pono=pd.pono,pickingbatchid=pd.pickingbatchid,popartno=pd.popartno,priority=pd.priority,dono=pd.dono,psid=pd.psid)
                SimpleLogger.do_log(f"Part usage saved.")
                SimpleLogger.do_log(f"partCost = {partCost}")
        except Exception as e:
            print(e)
            #send an email
            email_title = f"[SQ_API]PartDetailAudit : AuditID {nsp_part_audit_id}, POST" 
            email_content = f"PartDetails: {part_details_data} \n {e}"
            to_address = settings.NSC_ADMIN_EMAIL
            from_address = settings.NSP_INFO_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, from_address)
        #updating ticket
        op = OpBase.objects.get(id=int(WorkOrderID))
        try:
            t = OpTicket.objects.get(id=op.pid) #ticket SQL object
        except:
            t = 'Ticket Details not found'    
        work = OpWorkOrder.objects.get(id=int(WorkOrderID)) #WorkOrder SQL object
        if op.status==WorkOrderStatus.CLOSED.value:
            OpTicket.objects.filter(id=op.pid).update(lastworepairresult=work.repairresultcode)
        #creating new record in OPTicketAudit table
        ticket_audit_id = DBIDGENERATOR.process_id('OpTicketAudit_SEQ') 
        try:
            OpTicketAudit.objects.create(auditid=ticket_audit_id, type='U', method='POST', id=t.id, status=op.status,systemid=t.systemid,modelno=t.modelno,serialno=t.serialno,attentioncode=t.attentioncode,alertmessage=t.alertmessage,gspntechnicianid=t.gspntechnicianid,ticketno=t.ticketno,issuedtime=t.issuedtime,assigndtime=t.assigndtime,contactscheduledtime=t.contactscheduledtime,aptstartdtime=t.aptstartdtime,aptenddtime=t.aptenddtime,completedtime=t.completedtime,contactid=t.contactid,contactid2=t.contactid2,brand=t.brand,cancelreason=t.cancelreason,purchasedate=t.purchasedate,purchasedate2=t.purchasedate2,redoticketno=t.redoticketno,redoreason=t.redoreason,delayreason=t.delayreason,acknowledgedtime=t.acknowledgedtime,gspnstatus=t.gspnstatus,warehouseid=t.warehouseid,lastworepairresult=t.lastworepairresult,version=t.version,producttype=t.producttype,angerindex=t.angerindex,timezone=t.timezone,dst=t.dst,warrantystatus=t.warrantystatus,partwterm=t.partwterm,laborwterm=t.laborwterm,nspdelayreason=t.nspdelayreason,latitude=t.latitude,longitude=t.longitude,flag=t.flag,ascnumber=t.ascnumber,manufacturemonth=t.manufacturemonth,qosocsscore=t.qosocsscore,wtyexception=t.wtyexception,issueopendtime=t.issueopendtime,issueclosedtime=t.issueclosedtime,issuenoteid=t.issuenoteid,issuelatestid=t.issuelatestid,issuestatus=t.issuestatus,servicetype=t.servicetype,nspstatus=t.nspstatus,nspstatusdtime=t.nspstatusdtime,productcategory=t.productcategory,socount=t.socount,repeatcount=t.repeatcount,techid=t.techid,happycallfollowupdtime=t.happycallfollowupdtime,riskindex=t.riskindex,urgent=t.urgent,accountno=t.accountno,dplus1=t.dplus1,requestapptdtime=t.requestapptdtime,callfiredtime=t.callfiredtime,firstcontactdtime=t.firstcontactdtime,callfirestatus=t.callfirestatus,dontcheckcall=t.dontcheckcall,followupcheckcall=t.followupcheckcall,replacemodelno=t.replacemodelno,replaceserialno=t.replaceserialno,returntrackingno=t.returntrackingno,deliverytrackingno=t.deliverytrackingno,nscaccountno=t.nscaccountno,smsconsent=t.smsconsent)
            OpBase.objects.filter(id=int(WorkOrderID)).update(updatedon=datetime.datetime.today(), updatedby=CurrentUserID)
        except Exception as e:
            print(e)
            #send an email
            email_title = f"[SQ_API]TicketAudit : AuditID {ticket_audit_id}, POST" 
            email_content = f"TicketDetails: {t} \n {e}"
            to_address = settings.NSC_ADMIN_EMAIL
            from_address = settings.NSP_INFO_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, from_address)
        SimpleLogger.do_log(f"Part usage saved.")
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse({"message":"Part usage saved."}, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class UploadPictureController(View):
    "to upload picture"
    def post(self, request):
        "accept values in multi-part/form-data POST to upload picture"
        #API : /servicequick/api/uploadpicture
        SimpleLogger.do_log(f"PostFormData()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        
        RefId = request.POST.get('RefId')

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'RefId':RefId}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, RefId, "POST", "UploadPictureController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        #print(RefId)
        #print(request.FILES)
        if RefId is None or not RefId:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: RefId')            
            return JsonResponse({'message':'Parameter not found: RefId'}, safe=False, status=400)
        #checking ticketno
        try:
            check1 = OpTicket.objects.filter(id=int(RefId)).count()
        except:
            check1 = 0   
        check2 = OpTicket.objects.filter(ticketno=RefId).count()
        #print(check1)
        if check1==0 and check2==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Ticket {RefId} was not found")            
            return JsonResponse({'message':f"Ticket {RefId} was not found"}, safe=False, status=400)

        SimpleLogger.do_log(f"ERROR: Ticket {RefId} was not found")

        #checking GSPNSync
        GSPNSync = request.POST.get('GSPNSync') 
        sync = True
        if GSPNSync:
            try:
                sync = eval(GSPNSync.lower().title()) #checking if bool value for GSPNSync is True or False
            except:
                pass    
        SimpleLogger.do_log(f"sync= {sync}") 
        
        #checking filename and file extension
        files_list = request.FILES.getlist('fileName')
        if len(files_list)==0:
            try:
                files_list = [request.FILES['fileName']]
            except:
                return HttpResponseNotFound("No file found")    
        responseResult = []
        for f in files_list:
            fileName = f.name
            try:
                file_extension = fileName.split('.')[-1]
            except:
                return HttpResponseBadRequest(f"Invalid or unsupported image type: {fileName}")

            savepicture = PictureTrans
            res = savepicture.SavePictureNonTransaction(request, 'OpTicket', RefId, fileName, sync)
            if type(res) is not dict:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Error: {res}")            
                return JsonResponse({'message':f"Error: {res}"}, safe=False, status=400)
            else:
                responseResult.append(res['picture'])
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)            
        return JsonResponse(responseResult, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)    



class WorkOrderHistoryController(View):
    "returns work order details"
    def get(self, request):
        "accept WorkOrderID in GET to process"
        #API : /servicequick/api/WorkOrderHistory?workOrderId=$owrkOrderId
        SimpleLogger.do_log(f">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Validation and Logging
        WorkOrderID = request.GET.get('workOrderId')

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'WorkOrderID':WorkOrderID}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, WorkOrderID, "GET", "WorkOrderHistoryController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        if WorkOrderID is None or not WorkOrderID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: workOrderId')            
            return JsonResponse({'message':'Parameter not found: workOrderId'}, safe=False, status=400)

        token = request.META.get('HTTP_KW_TOKEN')

        try:
            WorkOrderID = int(WorkOrderID)
        except:
            pass    

        try:
            currentWorkOrder = OpWorkOrder.objects.get(id=WorkOrderID)
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {WorkOrderID}")            
            return JsonResponse({'message':f"Work order not found: {WorkOrderID}"}, safe=False, status=400)
        try:
            ticket = OpTicket.objects.filter(techid=currentWorkOrder.technicianid)[0]
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"No ticket found with WorkOrder: {WorkOrderID}")            
            return JsonResponse({'message':f"No ticket found with WorkOrder: {WorkOrderID}"}, safe=False, status=400)
        #Collecting data from functions        
        SQService = SchedulesService
        workOrderList = SQService.GetWorkOrderHistory(WorkOrderID, CurrentUserID, token)
        defectCodeList = WorkOrderAdditionalInfoVO.GetDefectCodeList(ticket.modelno, ticket.systemid, CurrentUserID, token)
        repairCodeList = WorkOrderAdditionalInfoVO.GetRepairCodeList(ticket.modelno, ticket.systemid, CurrentUserID, token)
        for workOrder in workOrderList:
            if workOrder['DEFECTCODE']:
                workOrder['DefectCodeDescription'] = WorkOrderAdditionalInfoVO.GetDefectCodeDescription(defectCodeList, workOrder['DEFECTCODE'])
            if workOrder['REPAIRCODE']:
                workOrder['RepairCodeDescription'] = WorkOrderAdditionalInfoVO.GetRepairCodeDescription(repairCodeList, workOrder['REPAIRCODE']) 

        #Preparing for the Response Data
        resultList = {}
        resultList['CurrentWorkOrderID'] = WorkOrderID
        resultList['ListSize'] = len(workOrderList)
        resultList['List'] = workOrderList
        resultList['LogID'] = BaseApiController.getlogid('GET', 'WorkOrderHistoryController', CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)         
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class SchedulableDateController(View):
    "it returns work SchedulableDate details"
    def get(self, request):
        "accept ticketno in GET request to process"
        #API : /servicequick/api/SchedulableDate?TicketNo=$ticketNo
        SimpleLogger.do_log(f">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)

        TicketNo = request.GET.get("ticketNo")
        IncludeWeekend = True
        WarehouseID = None

        reqData = {'TicketNo':TicketNo, 'IncludeWeekend':True}

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, TicketNo, "GET", "SchedulableDateController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        SimpleLogger.do_log(f"TicketNo= {TicketNo}")

        ticket = OpTicket.objects.filter(ticketno=TicketNo)

        if not ticket.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Ticket not found: {TicketNo}')            
            return JsonResponse({'message':f'Ticket not found: {TicketNo}'}, safe=False, status=400)
        
        ticket = ticket[0]
        WarehouseID = ticket.warehouseid

        #if warehouseID not found, get it from NSPWAREHOUSES tab;e
        if WarehouseID is None or WarehouseID=='':
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'NSP warehouse not found by ticketNo: {TicketNo}')            
            return JsonResponse({'message':f'NSP warehouse not found by ticketNo: {TicketNo}'}, safe=False, status=400)
        
        try:
            wh = NspWareHouses.objects.get(warehouseid=WarehouseID)
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'NSP warehouse not found by ticketNo: {TicketNo}')            
            return JsonResponse({'message':f'NSP warehouse not found by ticketNo: {TicketNo}'}, safe=False, status=400)

        sqzone_query = f"select a.Zone from NSPZones a, NSPAddresses b, NSPCompanyContacts c where a.WarehouseID='{WarehouseID}' and a.ProductCategory=ProductCategory and a.ZipCode=b.ZipCode and b.AddressID=c.AddressID and c.ContactID=ContactID"
        SQZone = SingleCursor.send_query(sqzone_query)
        dates = SchedulesService
        dates = dates.GetSchedulableDate(wh, SQZone['ZONE'], IncludeWeekend)

        SchedulableDate = {'WarehouseID':WarehouseID, 'SchedulableDates':dates}
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(SchedulableDate, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class CloseWorkOrderController(View):
    "to update/save the work order" 
    def post(self, request):
        "accept values in POST request to process" 
        #API : /servicequick/api/CloseWorkorder 
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        token = request.META.get('HTTP_KW_TOKEN')
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        
        SimpleLogger.do_log(f"content= {content}")
        WorkOrderID = received_json_data.get("WorkOrderID") 
        CompleteDTime = received_json_data.get("CompleteDTime")
        RepairResultCode = received_json_data.get("RepairResultCode")
        RepairFailCode = received_json_data.get("RepairFailCode")
        PaymentType = received_json_data.get("PaymentType")
        IsCxDissatisfied = received_json_data.get("IsCxDissatisfied")
        RescheduleStartDTime = received_json_data.get("RescheduleStartDTime")
        RescheduleEndDTime = received_json_data.get("RescheduleEndDTime")
        MsgConfirmDTime = received_json_data.get("MsgConfirmDTime") 
        SignName = received_json_data.get("SignName")
        SignData = received_json_data.get("SignData")
        SignData200 = received_json_data.get("SignData200")
        PaymentTransactionID = received_json_data.get("PaymentTransactionID") 
        Email = received_json_data.get("Email")

        SimpleLogger.do_log(f"reqData= {received_json_data}")

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(WorkOrderID), "POST", "CloseWorkOrderController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        #Validating the POST data received
        try:
            WorkOrderID = int(WorkOrderID)
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid WorkOrderID : {WorkOrderID}")            
            return JsonResponse({'message':f"Invalid WorkOrderID : {WorkOrderID}"}, safe=False, status=400)
        if not WorkOrderID or WorkOrderID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: WorkOrderID")            
            return JsonResponse({'message':"Value not found: WorkOrderID"}, safe=False, status=400)
        if not CompleteDTime:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: CompleteDTime")            
            return JsonResponse({'message':"Value not found: CompleteDTime"}, safe=False, status=400)
        if not RepairResultCode:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: RepairResultCode")            
            return JsonResponse({'message':"Value not found: RepairResultCode"}, safe=False, status=400)
        if not RepairFailCode:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: RepairFailCode")            
            return JsonResponse({'message':"Value not found: RepairFailCode"}, safe=False, status=400)

        try:
            CompleteDTime = datetime.datetime.strptime(CompleteDTime, "%Y-%m-%d %H:%M:%S") #AddHours(-((Ticket)workOrder.Ticket).TimeOffset); // Local Time to Server Time
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid CompleteDTime. Valid format is YYYY-MM-DD HH:MM:SS")            
            return JsonResponse({'message':f"Invalid CompleteDTime. Valid format is YYYY-MM-DD HH:MM:SS"}, safe=False, status=400)

        if MsgConfirmDTime:
            try:
                MsgConfirmDTime = datetime.datetime.strptime(MsgConfirmDTime, "%Y-%m-%d %H:%M:%S")
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid MsgConfirmDTime. Valid format is YYYY-MM-DD HH:MM:SS")            
                return JsonResponse({'message':f"Invalid MsgConfirmDTime. Valid format is YYYY-MM-DD HH:MM:SS"}, safe=False, status=400)

        if RescheduleStartDTime:
            try:
                RescheduleStartDTime = datetime.datetime.strptime(RescheduleStartDTime, "%Y-%m-%d %H:%M:%S")
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid RescheduleStartDTime. Valid format is YYYY-MM-DD HH:MM:SS")            
                return JsonResponse({'message':f"Invalid RescheduleStartDTime. Valid format is YYYY-MM-DD HH:MM:SS"}, safe=False, status=400)

        if RescheduleEndDTime:
            try:
                RescheduleEndDTime = datetime.datetime.strptime(RescheduleEndDTime, "%Y-%m-%d %H:%M:%S")
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid RescheduleEndDTime. Valid format is YYYY-MM-DD HH:MM:SS")            
                return JsonResponse({'message':f"Invalid RescheduleEndDTime. Valid format is YYYY-MM-DD HH:MM:SS"}, safe=False, status=400)                      

        def IsNotStartedFail():
            "compare different codes"
            if RepairResultCode==RepairResultCodeEnum.SUCCESS.value:
                return False
            if IsNotVisitedFail:
                return True
            NotStartedFailCodes = [RepairFailCodeEnum.DIFF_ASC_COMPLETED.value, RepairFailCodeEnum.UNIT_MOUNTED.value]
            if RepairFailCode in NotStartedFailCodes:
                return True
            else:
                return False

        def IsNotVisitedFail():
            "compare different coodes"
            if RepairResultCode==RepairResultCodeEnum.SUCCESS.value:
                return False
            NotVisitedFailCodes = [RepairFailCodeEnum.CUSTOMER_NOT_HOME.value, RepairFailCodeEnum.CX_REQUESTED_CANCEL.value, RepairFailCodeEnum.NOT_VISITED_CX_ISSUE.value, RepairFailCodeEnum.NOT_VISITED_LOCAL_ISSUE.value,RepairFailCodeEnum.NOT_VISITED_PART_ISSUE.value,RepairFailCodeEnum.RESCHEDULE.value]
            if RepairFailCode in NotVisitedFailCodes:
                return True
            else:
                return False

        if IsNotStartedFail:
            if not PaymentType:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: PaymentType")            
                return JsonResponse({'message':"Value not found: PaymentType"}, safe=False, status=400)

        if IsNotVisitedFail:
            if not SignName:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: SignName")            
                return JsonResponse({'message':"Value not found: SignName"}, safe=False, status=400)
            if not SignData:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: SignData")            
                return JsonResponse({'message':"Value not found: SignData"}, safe=False, status=400)

        if SignName and len(SignName) > 35:
            SignName = SignName[0:35]

        SimpleLogger.do_log(f">>> workOrder= {WorkOrderID}") 

        wo = OpWorkOrder.objects.filter(id=int(WorkOrderID))
        if not wo.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {WorkOrderID}")            
            return JsonResponse({'message':f"Work order not found: {WorkOrderID}"}, safe=False, status=400)

        op = OpBase.objects.filter(id=int(WorkOrderID))
        if op.exists():
            if op[0].status < WorkOrderStatus.PROCESSING.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Repair has not been started: {WorkOrderID}")            
                return JsonResponse({'message':f"Repair has not been started: {WorkOrderID}"}, safe=False, status=400)
        else:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Work order not found: {WorkOrderID}")            
            return JsonResponse({'message':f"Work order not found: {WorkOrderID}"}, safe=False, status=400)

        t = OpTicket.objects.filter(techid=int(wo[0].technicianid))
        if t.exists():
            SimpleLogger.do_log(f"Ticket= {t[0].ticketno}")
        else:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"No Ticket found with WorkOrderID : {WorkOrderID}")            
            return JsonResponse({'message':f"No Ticket found with WorkOrderID : {WorkOrderID}"}, safe=False, status=400)
            #pass    
        
        workorder_dict = {} 
        workorder_dict['ID'] = WorkOrderID   
        SaveSig = PictureTrans #creating an instance of the class PictureTrans
        #SignData Logic
        signURL = ''
        if SignData:
            SignDataBytes = bytes(SignData, encoding='utf-8') #converting base64 string to bytes and then to binary using base64
            SimpleLogger.do_log(f"delivery.SignDataBytes.Length= {len(SignDataBytes)}")

            folderId1 = DBIDGENERATOR.process_gid('DC')
            fileId1 = DBIDGENERATOR.process_gid('DC')

            SimpleLogger.do_log(f"GetDocID() = {folderId1}")
            SimpleLogger.do_log(f"GetDocID() = {fileId1}")

            if SignData200:
                folderId200 = DBIDGENERATOR.process_gid('DC')
                fileId200 = DBIDGENERATOR.process_gid('DC')
                SimpleLogger.do_log(f"GetDocID() = {folderId200}")
                SimpleLogger.do_log(f"GetDocID() = {fileId200}")
            
            res = SaveSig.SaveWorkOrderSignature(wo, SignDataBytes, folderId1, fileId1, wo[0].workorderno+'_SIGNATURE', CurrentUserID)
            print('res object is ', res)
            if type(res) is dict:
                sign_docid = res['docid'] #updating the NSPDOCS table
                try:
                    NspDocs.objects.create(docid=sign_docid, opticketid=t[0].id, doctype=settings.NSP_DOCTYPE_SIGNATURE, createdon=datetime.datetime.today(), createdby=CurrentUserID)
                except:
                    NspDocs.objects.filter(docid=sign_docid).update(opticketid=t[0].id, doctype=settings.NSP_DOCTYPE_SIGNATURE, updatedon=datetime.datetime.today(), updatedby=CurrentUserID)    
            else:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"Error in saving signature data as file: {res}")            
                return JsonResponse({'message':f"Error in saving signature data as file: {res}"}, safe=False, status=500)
            
            signURL = res['url']
            SimpleLogger.do_log(f"signDoc= {res}")
            workorder_dict['SignatureDocID'] = res['docid']
            workorder_dict['PaymentType'] = PaymentTypeEnum(int(PaymentType)).value
            workorder_dict['IsCxDissatisfied'] = IsCxDissatisfied
            workorder_dict['SmallSignatureDocID'] = None

            signURL200 = ''
            if SignData200:
                SignDataBytes200 = bytes(SignData200, encoding='utf-8') #converting base64 string to bytes and then to binary using base64
                SimpleLogger.do_log(f"delivery.SignDataBytes200.Length = {len(SignDataBytes)}")
                res200 = SaveSig.SaveWorkOrderSignature(wo, SignDataBytes200, folderId200, fileId200, wo[0].workorderno+'_SIGNATURE_200', CurrentUserID)
                SignData = SignData200 #in case user has uploaded SignData200 signature, we shall use this in report generation
                if type(res200) is dict:
                    sign_docid = res200['docid'] #updating the NSPDOCS table
                    try:
                        NspDocs.objects.create(docid=sign_docid, opticketid=t[0].id, doctype=settings.NSP_DOCTYPE_SIGNATURE, createdon=datetime.datetime.today(), createdby=CurrentUserID)
                    except:
                        NspDocs.objects.filter(docid=sign_docid).update(opticketid=t[0].id, doctype=settings.NSP_DOCTYPE_SIGNATURE, updatedon=datetime.datetime.today(), updatedby=CurrentUserID)    
                    signURL200 = res200['url']
                    workorder_dict['SmallSignatureDocID'] = res200['docid']
                else:
                    BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"Error in saving 200 signature data as file: {res}")            
                    return JsonResponse({'message':f"Error in saving 200 signature data as file: {res}"}, safe=False, status=500)

        #Save WorkOrder (SignatureDocID is required when creating report)
        workorder_dict['SignedName'] = SignName
        workorder_dict['FinishDTime'] = CompleteDTime #AddHours(-((Ticket)workOrder.Ticket).TimeOffset); // Local Time to Server Time
        workorder_dict['MsgConfirmDTime'] = MsgConfirmDTime
        workorder_dict['RepairResultCode'] = RepairResultCodeEnum(int(RepairResultCode)).value
        workorder_dict['RepairFailCode'] = RepairFailCodeEnum(int(RepairFailCode)).value
            
        workorder_dict['PaymentTransactionID'] = PaymentTransactionID
        workorder_dict['Status'] = WorkOrderStatus.CLOSED.value

        workorder_dict['AuditID'] = DBIDGENERATOR.process_id("OpWorkOrderAudit_SEQ")
        workorder_dict['Method'] = 'POST'

        #checking status of a record in the OPBASE table and if found, update the record accordingly
        check_query = OpBase.objects.filter(id=int(WorkOrderID))
        original_pid_value = None
        if check_query.exists():
            try:
                original_pid_value = OpTicket.objects.get(id=check_query[0].pid).id
            except:
                original_pid_value = None
            if check_query[0].createdon is None:
                check_query.update(createdon=timezone.now(), createdby=CurrentUserID, status=WorkOrderStatus.CLOSED.value, originalpid=original_pid_value)
            else:
                check_query.update(updatedon=timezone.now(), updatedby=CurrentUserID, status=WorkOrderStatus.CLOSED.value)
                original_pid_value = check_query[0].originalpid 
        #Updating details into the workorder table and Copying workorder data to opworkorderaudit table    
        try:
            OpWorkOrder.objects.filter(id=int(WorkOrderID)).update(signedname=workorder_dict['SignedName'], finishdtime=workorder_dict['FinishDTime'], repairresultcode=workorder_dict['RepairResultCode'], repairfailcode= workorder_dict['RepairFailCode'], msgconfirmdtime=workorder_dict['MsgConfirmDTime'], paymenttransactionid=workorder_dict['PaymentTransactionID'],smallsignaturedocid=workorder_dict.get('SmallSignatureDocID'),paymenttype=workorder_dict['PaymentType'],iscxdissatisfied=workorder_dict['IsCxDissatisfied'])
            w = OpWorkOrder.objects.get(id=int(WorkOrderID)) #getting the updated workorder record
            OpWorkOrderAudit.objects.create(auditid=workorder_dict['AuditID'], method=workorder_dict['Method'], type="U", id=w.id, auditdtime=timezone.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=workorder_dict['Status'], pid=original_pid_value)
        except Exception as e: 
            print('line-755, error - ', e)   
            #send an email
            email_title = f"[SQ_API]WorkOrderAudit : AuditID {workorder_dict['AuditID']}, POST" 
            email_content = f"WorkOrder: {str(WorkOrderID)} \n {e}"
            to_address = settings.NSC_ADMIN_EMAIL
            from_address = settings.NSP_INFO_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, from_address)
        #If workorder is closed, then also update the ticket table
        OpTicket.objects.filter(id=int(WorkOrderID)).update(lastworepairresult=workorder_dict['RepairResultCode'])
        SimpleLogger.do_log(f"Work order saved: {WorkOrderID} ({WorkOrderStatus.CLOSED.value})")

        #Saving WorkSheet
        receiptFile = ""
        if signURL or signURL200:
            getreport = ReportGeneration
            receiptFile = getreport.CreateWorksheetReport(workorder_dict, SignData);  #function(related to CrystalReports/JasperReports)
            receiptFile = receiptFile.decode('utf-8')
            receiptFile = json.loads(receiptFile)
        
        if type(receiptFile) is dict and receiptFile['message']=='Success':
            folderId2 = DBIDGENERATOR.process_gid('DC')
            fileId2 = DBIDGENERATOR.process_gid('DC')
            receiptDoc = SaveSig.SaveReceiptDocument(wo, receiptFile, folderId2, fileId2, wo[0].workorderno+'_MOBILE', CurrentUserID)
            if type(receiptDoc) is dict:
                workorder_dict['FinalWorkOrderDocID'] = receiptDoc['docid']
                try:
                    NspDocs.objects.create(docid=receiptDoc['docid'], opticketid=t[0].id, doctype=settings.NSP_DOCTYPE_SERVICE_ORDER, createdon=datetime.datetime.today(), createdby=CurrentUserID)
                except:
                    try:
                        NspDocs.objects.filter(docid=receiptDoc['docid']).update(opticketid=t[0].id, doctype=settings.NSP_DOCTYPE_SERVICE_ORDER, updatedon=datetime.datetime.today(), updatedby=CurrentUserID)
                    except Exception as e:
                        print(e)        
                SimpleLogger.do_log(f"Receipt generated: {receiptDoc}")
                #creating Audit record again
                workorder_dict['AuditID'] = DBIDGENERATOR.process_id("OpWorkOrderAudit_SEQ")
                workorder_dict['Method'] = 'POST'
                try:
                    original_pid_value = OpTicket.objects.get(id=int(WorkOrderID)).id
                except:
                    original_pid_value = None
                try:
                    OpWorkOrder.objects.filter(id=int(WorkOrderID)).update(finalworkorderdocid=workorder_dict['FinalWorkOrderDocID'])
                    w = OpWorkOrder.objects.get(id=int(WorkOrderID)) #getting the updated workorder record
                    OpWorkOrderAudit.objects.create(auditid=workorder_dict['AuditID'], method=workorder_dict['Method'], type="U", id=w.id, auditdtime=timezone.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=workorder_dict['Status'], pid=original_pid_value)
                except Exception as e:
                    print('line-793, Error - ', e)
                    #send an email
                    email_title = f"[SQ_API]WorkOrderAudit : AuditID {workorder_dict['AuditID']}, POST" 
                    email_content = f"WorkOrder: {str(WorkOrderID)} \n {e}"
                    to_address = settings.NSC_ADMIN_EMAIL
                    from_address = settings.NSP_INFO_EMAIL
                    sendmailoversmtp(to_address, email_title, email_content, from_address)
        #Call FinalizeWorkOrder            
        try:
            WarehouseID = t[0].warehouseid
            wh = NspWareHouses.objects.get(warehouseid=WarehouseID)
        except:
            WarehouseID = 0

        sqzone_query = f"select a.Zone from NSPZones a, NSPAddresses b, NSPCompanyContacts c where a.WarehouseID='{WarehouseID}' and a.ProductCategory=ProductCategory and a.ZipCode=b.ZipCode and b.AddressID=c.AddressID and c.ContactID={wo[0].contactid};"
        SQZone = SingleCursor.send_query(sqzone_query)
        print('sqzone_query = ', SQZone)
        if type(SQZone) is dict:
            SQZone = SQZone['ZONE']
        else:
            SQZone = None    
        sq = SchedulesService
        dates = sq.GetSchedulableDate(wh, SQZone, True)
        
        if RescheduleStartDTime and RescheduleEndDTime:
            RescheduleStartDTimeStr = RescheduleStartDTime.strftime("%Y-%m-%d %H:%M:%S") #converting date to string format
            if RescheduleStartDTimeStr not in dates:
                ContactLog = {}
                ContactLog['ID'] = DBIDGENERATOR.process_id("OpBase_SEQ")
                ContactLog['OpType'] = OpType.CONTACT_LOG.value
                ContactLog['LogType'] = LogType.CUSTOMER_CALL.value
                ContactLog['StartDTime'] = datetime.datetime.today()
                ContactLog['Status'] = 60
                ContactLog['Ticket'] = t
                ContactLog['Content'] = f"CX wanted next schedule at {RescheduleStartDTime}. But Slot is fully booked."
                ContactLog['ContactResult'] = ContactResultCode.SUCCESS.value
                ContactLog['OpDTime'] = ContactLog['StartDTime']
                #Saving Contact Log
                OpBase.objects.create(id=ContactLog['ID'], createdon=datetime.datetime.today(), createdby=CurrentUserID, originalpid=t[0].id, status=ContactLog['Status'], optype=ContactLog['OpType'], opdtime=ContactLog['OpDTime'], pid=t[0].id)
                OpContactCustomer.objects.create(id=ContactLog['ID'], startdtime=ContactLog['StartDTime'], logtype=ContactLog['LogType'],contactlog=ContactLog['Content'], contactresult=ContactLog['ContactResult'])
                task_run_async = sq.FinalizeWorkOrder(token, WorkOrderID)
            else:
                #checking if both t1 and t2 have the same time
                t1 = RescheduleEndDTime
                t2 = datetime.datetime.today() + datetime.timedelta(hours=8, minutes=0, seconds=0)
                if t1.time()==t2.time():
                    RescheduleEndDTime = t1 + datetime.timedelta(hours=10, minutes=0, seconds=0) #add 10 hours to t1
                task_run_async = sq.RescheduleWorkOrder(token, WorkOrderID, RescheduleStartDTime, RescheduleEndDTime)
        else:
            task_run_async = sq.FinalizeWorkOrder(token, WorkOrderID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)    
        return HttpResponse("WorkOrder saved.")                

@method_decorator(csrf_exempt, name='dispatch')
class TechNoteController(View):
    "class to save technician notes" 
    def post(self, request):
        "accept POST parameters to process"
        #API : /servicequick/api/TechNote
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")

        SimpleLogger.do_log(f"content= {content}")
        TicketNo = received_json_data.get('TicketNo') 
        Note = received_json_data.get('Note')
        MailTo = received_json_data.get('MailTo')
        NoteID = received_json_data.get('NoteID')

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(TicketNo), "POST", "TechNoteController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        #Validation
        SimpleLogger.do_log(f"TicketNo= {TicketNo}")
        ticket = OpTicket.objects.filter(ticketno=TicketNo)
        if not ticket.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Ticket was not found")            
            return JsonResponse({'message':"Ticket was not found"}, safe=False, status=400)
        #Updating the tables OPNOTE and OPBASE and thus saving the notes
        note_dict = {}
        note_dict['Status'] = 60
        note_dict['Ticket'] = ticket
        note_dict['RefNo'] = ticket[0].ticketno
        note_dict['Content'] = Note
        note_dict['NoteType'] = NoteTypeEnum.TECH_NOTE.value
        note_dict['MailTo'] = MailTo

        if not NoteID:
            NoteID = 0

        try:
            NoteID = int(NoteID)
        except:
            NoteID = 0         
        
        try:
            notesql = OpNote.objects.filter(id=NoteID) #checking if Notes exist by NoteID 
            if not notesql.exists():
                note_dict['ID'] = DBIDGENERATOR.process_id("OpBase_SEQ")
                note_dict['OpType'] = OpType.NOTE.value
                OpBase.objects.create(id=note_dict['ID'], optype=note_dict['OpType'], createdon=datetime.datetime.today(), createdby=CurrentUserID, originalpid=ticket[0].id, status=note_dict['Status'], opdtime=datetime.datetime.today())
                OpNote.objects.create(id=note_dict['ID'], refno=note_dict['RefNo'],note=note_dict['Content'],notetype=note_dict['NoteType'],mailto=note_dict['MailTo'])
            else:
                note_dict['ID'] = notesql[0].id
                OpNote.objects.filter(id=NoteID).update(refno=note_dict['RefNo'],note=note_dict['Content'],notetype=note_dict['NoteType'],mailto=note_dict['MailTo'])
                OpBase.objects.filter(id=NoteID).update(updatedon=datetime.datetime.today(), updatedby=CurrentUserID, opdtime=datetime.datetime.today())

            SimpleLogger.do_log(f"Tech Note Saved: {note_dict['ID']}")
            #Sending Email
            if MailTo and '@' in MailTo:
                u = Nspusers.objects.filter(userid=CurrentUserID)
                if u.exists and u[0].firstname is not None and u[0].lastname is not None:
                    fullname = str(u[0].firstname) + ' ' + str(u[0].lastname)
                else:
                    fullname = 'User ID: N/A'
                etech = TechEmailService #getting the class instance
                etech.SendEmail(Note, MailTo, TicketNo, note_dict['ID'], fullname)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)     
            return JsonResponse({'message':f"success to save Tech Note : {note_dict['ID']}"}, safe=False, status=200)
        except Exception as e:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"ERROR in saving notes : {str(e)}")            
            return JsonResponse({'message':f"ERROR in saving notes : {str(e)}"}, safe=False, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class EmailReceiptController(View):
    "to send email based on WorkOrderID" 
    def post(self, request):
        "accept parameters in POST to process"
        #API : /servicequick/api/EmailReceipt
        SimpleLogger.do_log(f">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")

        SimpleLogger.do_log(f"content= {content}")
        WorkOrderID = received_json_data.get("WorkOrderId")
        Email = received_json_data.get('Email')

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(WorkOrderID), "POST", "EmailReceiptController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        #Validation
        if not WorkOrderID or WorkOrderID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: WorkOrderID")            
            return JsonResponse({'message':"Value not found: WorkOrderID"}, safe=False, status=400)
        if not Email:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Value not found: Email")            
            return JsonResponse({'message':"Value not found: Email"}, safe=False, status=400)

        SimpleLogger.do_log(f">>> workOrder= {WorkOrderID}")
        wo = OpWorkOrder.objects.filter(id=int(WorkOrderID))
        if not wo.exists():
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"WorkOrder not found: {WorkOrderID}")            
            return JsonResponse({'message':f"WorkOrder not found: {WorkOrderID}"}, safe=False, status=400)

        #Sending Email
        newtech = TechEmailService
        wsResult = newtech.EmailReceipt(request.META.get('HTTP_KW_TOKEN'), int(WorkOrderID), Email)
        print(wsResult)
        SimpleLogger.do_log(f"xml.InnerText= {wsResult}")
        xml_error = get_xml_node(wsResult, 'ERROR') 
        if xml_error:
            return HttpResponseServerError(f"InternalServerError: {xml_error}")

        SimpleLogger.do_log(f"Email sent: {Email} ({WorkOrderID})")
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse("Email sent successfully.")


class PartSerialsController(View):
    "to get the details of partSerial" 
    def get(self, request, psid=None):
        "accept parameters in GET to process"
        #API : GET /servicequick/api/partserials/{PSID}
        if psid is not None:
            SimpleLogger.do_log(f">>> Get()...{psid}")
            p1 = KWAuthentication
            authstat = p1.authenticate(request)

            CurrentUserID = KWAuthentication.getcurrentuser(request)
            jsonString = str(json.dumps({'psid':psid}))
            AppVersion = request.META.get('HTTP_APPVERSION')
            callerApp = BaseApiController.CallerApp(request) 
            sqAPILog = BaseApiController.StartLog(CurrentUserID, str(psid), "GET", "PartSerialsController", jsonString, callerApp, AppVersion)

            if authstat is not True:
                return JsonResponse(authstat, status=401)

            #Validation
            try:
                ps = NspPartSerials.objects.get(psid=psid)
            except Exception as e:
                SimpleLogger.do_log(f"PartSerial not found - {psid} : {e}")
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"PartSerial '{psid}' was not found.")            
                return JsonResponse({'message':f"PartSerial '{psid}' was not found."}, safe=False, status=400)
            try:
                psid = int(psid)
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"PSID not valid : {psid}")            
                return JsonResponse({'message':f"PSID not valid : {psid}"}, safe=False, status=400)
            #returns the data
            result = PartSupport.GetPartSerial(psid)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return JsonResponse(result, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
        else: #API: GET /servicequick/api/partserials?warehouseId=1&locationCode=A&partNo=B
            SimpleLogger.do_log(">>> Get()...")
            p1 = KWAuthentication
            authstat = p1.authenticate(request)
            warehouseId = request.GET.get('warehouseId')
            locationCode = request.GET.get('locationCode') 
            partNo = request.GET.get('partNo')

            reqData = f"warehouseId : {warehouseId}, locationCode : {locationCode}, partNo : {partNo}" 

            CurrentUserID = KWAuthentication.getcurrentuser(request)
            jsonString = str(json.dumps({'reqData':reqData}))
            AppVersion = request.META.get('HTTP_APPVERSION')
            callerApp = BaseApiController.CallerApp(request) 
            sqAPILog = BaseApiController.StartLog(CurrentUserID, str(psid), "GET", "PartSerialsController", jsonString, callerApp, AppVersion)

            if authstat is not True:
                return JsonResponse(authstat, status=401)

            if not warehouseId:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Parameter required: warehouseId")            
                return JsonResponse({'message':"Parameter required: warehouseId"}, safe=False, status=400)

            SimpleLogger.do_log(f"warehouseId={warehouseId}", "debug") 
            SimpleLogger.do_log(f"locationCode={locationCode}", "debug")
            SimpleLogger.do_log(f"partNo={partNo}", "debug")
           
            #Validating/Checking the supplied parameters
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
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="Parameter required: LocationCode or PartNo")            
                return JsonResponse({'message':"Parameter required: LocationCode or PartNo"}, safe=False, status=400)

            itemList = PartSupport.GetPartSerialList(warehouseId, locationCode, partNo, 1, 2147483647) #2147483647 is int.MaxValue as per C# code
            #Preparing the response data
            resultList = {}
            resultList['WarehouseID'] = warehouseId
            resultList['LocationCode'] = locationCode
            resultList['PartNo'] = partNo
            resultList['ListSize'] = len(itemList)
            resultList['List'] = itemList
            resultList['LogID'] = BaseApiController.getlogid('GET', 'PartSerialsController', CurrentUserID)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)         



class WarehousesController(View):
    "to get list of ware houses" 
    def get(self, request, id=None):
        "accept request in GET to process"
        #api/warehouses
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        if id is None:
            SimpleLogger.do_log(">>> Get()...")
            jsonString = str(json.dumps({'reqData':" "}))
            AppVersion = request.META.get('HTTP_APPVERSION')
            callerApp = BaseApiController.CallerApp(request) 
            sqAPILog = BaseApiController.StartLog(CurrentUserID, " ", "GET", "WarehousesController", jsonString, callerApp, AppVersion)

            if authstat is not True:
                return JsonResponse(authstat, status=401)
            #Preparing WareHouses List
            query_ware = NspWareHouses.objects.filter(isactive=True).all().order_by('nickname')
            WList = []
            for x in query_ware:
                xdict = {}
                xdict['WarehouseID'] = x.warehouseid
                xdict['NickName'] = x.nickname
                xdict['Color'] = x.color
                xdict['Latitude'] = x.latitude
                xdict['Longitude'] = x.longitude
                try:
                    xdict['MarkerAdjX'] = float(x.markeradjx)
                except:
                    xdict['MarkerAdjX'] = x.markeradjx
                try:        
                    xdict['MarkerAdjY'] = float(x.markeradjy)
                except:
                    xdict['MarkerAdjY'] = x.markeradjy    
                xdict['Code'] = x.code
                xdict['CompanyID'] = x.companyid
                xdict['TimeZone'] = x.timezone
                xdict['IsActive'] = x.isactive
                xdict['RDCWarehouseID'] = x.rdcwarehouseid
                xdict['WarehouseType'] = x.warehousetype
                xdict['PartTAT'] = x.parttat
                xdict['CreatedOn'] = x.createdon
                xdict['CreatedBy'] = x.createdby
                xdict['UpdatedOn'] = x.updatedon
                xdict['UpdatedBy'] = x.updatedby
                if x.updatedby is not None:
                    xdict['LogBy'] = x.updatedby
                else:
                    xdict['LogBy'] = x.createdby    
                xdict['LogByName'] = None #this is always null as per C# code
                for key, value in xdict.items():
                    if value=="":
                        xdict[key] = None
                WList.append(xdict)
            LogID = BaseApiController.getlogid('GET', 'WarehousesController', CurrentUserID)    
            ResultList = {'ListSize':query_ware.count(),'List':WList, 'LogID':LogID}
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return JsonResponse(ResultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
        else:
            SimpleLogger.do_log(f">>> Get()...{id}")
            jsonString = str(json.dumps({'id':id}))
            AppVersion = request.META.get('HTTP_APPVERSION')
            callerApp = BaseApiController.CallerApp(request) 
            sqAPILog = BaseApiController.StartLog(CurrentUserID, str(id), "GET", "WarehousesController", jsonString, callerApp, AppVersion)

            if authstat is not True:
                return JsonResponse(authstat, status=401)
           
            #Preparing WareHouses List
            query_ware = NspWareHouses.objects.filter(isactive=True, warehouseid=id).all().order_by('nickname')
            #WList = NspWareHousesSerializer(query_ware, many=True)
            WList = []
            for x in query_ware:
                xdict = {}
                xdict['WarehouseID'] = x.warehouseid
                xdict['NickName'] = x.nickname
                xdict['Color'] = x.color
                xdict['Latitude'] = x.latitude
                xdict['Longitude'] = x.longitude
                try:
                    xdict['MarkerAdjX'] = float(x.markeradjx)
                except:
                    xdict['MarkerAdjX'] = x.markeradjx
                try:        
                    xdict['MarkerAdjY'] = float(x.markeradjy)
                except:
                    xdict['MarkerAdjY'] = x.markeradjy    
                xdict['Code'] = x.code
                xdict['CompanyID'] = x.companyid
                xdict['TimeZone'] = x.timezone
                xdict['IsActive'] = x.isactive
                xdict['RDCWarehouseID'] = x.rdcwarehouseid
                xdict['WarehouseType'] = x.warehousetype
                xdict['PartTAT'] = x.parttat
                xdict['CreatedOn'] = x.createdon
                xdict['CreatedBy'] = x.createdby
                xdict['UpdatedOn'] = x.updatedon
                xdict['UpdatedBy'] = x.updatedby
                if x.updatedby is not None:
                    xdict['LogBy'] = x.updatedby
                else:
                    xdict['LogBy'] = x.createdby    
                xdict['LogByName'] = None #this is always null as per C# code
                for key, value in xdict.items():
                    if value=="":
                        xdict[key] = None
                WList.append(xdict)
            LogID = BaseApiController.getlogid('GET', 'WarehousesController', CurrentUserID)    
            ResultList = {'ListSize':query_ware.count(),'List':WList, 'LogID':LogID}
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return JsonResponse(ResultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class MovePartController(View):
    "helps in validating movement of parts"
    def get(self, request):
        "accept GET request to process"
        #API : /servicequick/api/movepart 
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Decoding the GET request
        workOrderNo = request.GET.get('workOrderNo')
        PSID = request.GET.get('PSID')
        try:
            PSID = int(PSID)
        except:
            pass     
        reqData = f"workOrderNo : {workOrderNo}, PSID : {PSID}" 
       
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(PSID), "GET", "MovePartController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        #Checking data from different tables
        # Getting WorkOrder record by WorkOrder number
        try:
            wo = OpWorkOrder.objects.filter(workorderno=workOrderNo)[0]
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"workOrderNo {workOrderNo} not found")            
            return JsonResponse({'message':f"workOrderNo {workOrderNo} not found"}, safe=False, status=400)
        # Getting ticket by workorder ID
        try:
            tk = OpTicket.objects.filter(techid=wo.technicianid)[0]
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"No ticket exists for the workOrderNo {workOrderNo}")            
            return JsonResponse({'message':f"No ticket exists for the workOrderNo {workOrderNo}"}, safe=False, status=400)
        # Getting account no
        try:
            ac = NspAccounts.objects.filter(accountno=tk.accountno)[0]
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"No accountno exists for the workOrderNo {workOrderNo}")            
            return JsonResponse({'message':f"No accountno exists for the workOrderNo {workOrderNo}"}, safe=False, status=400)
        # Comparing the values obtained
        partAccountNo = ac.partaccountno
        try:
            ps = NspPartSerials.objects.filter(psid=PSID)[0]
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"No PartSerial exists for the workOrderNo {workOrderNo}")            
            return JsonResponse({'message':f"No PartSerial exists for the workOrderNo {workOrderNo}"}, safe=False, status=400)
        if ps.accountno!=partAccountNo:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Part Account does not match')            
            return JsonResponse({'message':'Part Account does not match'}, safe=False, status=500)
        else:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return HttpResponse("Part Account Matched")
    def post(self, request):
        "accept parameters in POST to process"
        #API : /servicequick/api/movepart
        SimpleLogger.do_log(">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")

        SimpleLogger.do_log(f"content= {content}")
        PSID = received_json_data.get("PSID")
        WarehouseID = received_json_data.get('WarehouseID')
        ToLocationCode = received_json_data.get('ToLocationCode')
        Reason = received_json_data.get('Reason')

        try:
            PSID = int(PSID)
        except:
            pass 

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(PSID), "POST", "MovePartController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)   
       
        SimpleLogger.do_log(f"reqData= {received_json_data}")
        #Validation of part serial
        try:
            ps = NspPartSerials.objects.filter(psid=PSID)[0] #getting part serial
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"PartSerial not found: {PSID}")            
            return JsonResponse({'message':f"PartSerial not found: {PSID}"}, safe=False, status=400)
        #Defining variables
        DELIMETER = '|'
        sWarehouseID = ''
        sToLocationCode = ''
        location = None
        #Running conditions
        if DELIMETER in ToLocationCode:
            loc = ToLocationCode.split(DELIMETER)
            try:
                if loc[0].upper()=='NULL' or not loc[0]:
                    sWarehouseID = WarehouseID
                else:
                    sWarehouseID = loc[0]
            except:
                sWarehouseID = WarehouseID
            try:
                sToLocationCode = loc[1]
            except:
                pass
        else:
            sWarehouseID = WarehouseID
            sToLocationCode = ToLocationCode
        #checking data in the table NspLocations
        try:
            location = NspLocations.objects.filter(warehouseid=sWarehouseID, locationcode=sToLocationCode)[0]
        except Exception as e:
            print(e)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Warehouse location not found: {ToLocationCode}")            
            return JsonResponse({'message':f"Warehouse location not found: {ToLocationCode}"}, safe=False, status=400)
        #Call NSP W/S by making a soap request to a remote server and get the result
        wsResult = XMLActions.move_part(CurrentUserID, PSID, sWarehouseID, sToLocationCode, Reason)
        SimpleLogger.do_log(f"result= {wsResult}")
        if wsResult['ErrorMsg']!="":
            #pass
            return JsonResponse({"message": f"{wsResult['ErrorMsg']}"}, safe=False, status=400)
        #Preparing for the Response Data
        resData = {}
        resData['PSID'] = PSID
        resData['PartNo'] = ps.partno
        resData['WarehouseID'] = WarehouseID
        resData['LocationCode'] = ToLocationCode
        resData['LocationType'] = location.locationtype 
        wores = {}
        if location.locationtype==LocationType.SQBOX.value:
            try:
                workOrder = OpWorkOrder.objects.filter(partwarehouseid=location.warehouseid, sqbox=location.locationcode).order_by('-id')
                for x in workOrder:
                    try:
                        b = OpBase.objects.get(id=x.id)
                        if b.status <= WorkOrderStatus.CLOSED.value:
                            workOrder = OpWorkOrder.objects.filter(id=x.id, partwarehouseid=location.warehouseid, sqbox=location.locationcode)[0]
                            wores['WarrantyStatus'] = workOrder.warrantystatus
                            wores['RepairResultCode'] = workOrder.repairresultcode
                            wores['PaymentType'] = workOrder.paymenttype
                            wores['RepairFailCode'] = workOrder.repairfailcode
                            pd = NspPartDetails.objects.filter(opworkorderid=x.id).order_by('partdetailid')
                            PartDetails = []
                            for p in pd:
                                partdict = {}
                                partdict['PartDetailID'] = p.partdetailid
                                partdict['PartNo'] = p.partno
                                partdict['PartDescription'] = p.partdesc
                                partdict['Qty'] = p.qty
                                try:
                                    partdict['UnitPrice'] = float(p.unitprice)
                                except:
                                    partdict['UnitPrice'] = 0.0
                                partdict['Usage'] = p.usage
                                partdict['ReserveStatus'] = p.reservestatus
                                partdict['PONo'] = p.pono
                                partdict['PSID'] = p.psid
                                partdict['DONo'] = p.dono
                                partdict['PartETA'] = p.parteta
                                partdict['TrackingNo'] = p.trackingno
                                for key, value in partdict.items():
                                    if value=='':
                                        partdict[key] = None
                                PartDetails.append(partdict)
                            wores['PartDetails'] = PartDetails
                            wores['WorkOrderNo'] = workOrder.workorderno
                            wores['AptStartDTime'] = workOrder.aptstartdtime
                            wores['AptEndDTime'] = workOrder.aptenddtime
                            wores['StartDTime'] = workOrder.startdtime
                            wores['FinishDTime'] = workOrder.finishdtime
                            ct = NspCompanyContacts.objects.filter(contactid=x.contactid)
                            contacts = {}
                            for c in ct:
                                contacts['ContactID'] = x.contactid
                                nspadd = NspAddresses.objects.filter(addressid=c.addressid)
                                address = {}
                                for ad in nspadd:
                                    address['Addr'] = ad.address
                                    address['City'] = ad.city
                                    address['State'] = ad.state
                                    address['ZipCode'] = ad.zipcode
                                    address['Country'] = ad.country
                                    address['CreatedOn'] = ad.createdon
                                    address['CreatedBy'] = ad.createdby
                                    address['UpdatedOn'] = ad.updatedon
                                    address['UpdatedBy'] = ad.updatedby
                                    if ad.createdby is not None:
                                        address['LogBy'] = ad.createdby
                                    else:
                                        address['LogBy'] = ad.updatedby
                                    address['LogByName'] = None
                                contacts['Address'] = address
                                contacts['Name'] = c.name
                                contacts['Tel'] = c.tel
                                contacts['Fax'] = c.fax
                                contacts['Email'] = c.email
                                contacts['Mobile'] = c.mobile
                                contacts['CreatedOn'] = c.createdon
                                contacts['CreatedBy'] = c.createdby
                                contacts['UpdatedOn'] = c.updatedon
                                contacts['UpdatedBy'] = c.updatedby
                                if c.createdby is not None:
                                    contacts['LogBy'] = c.createdby
                                else:
                                    contacts['LogBy'] = c.updatedby
                                contacts['LogByName'] = None         
                            wores['Contact'] = contacts
                            wores['Technician'] = getuserinfo(workOrder.technicianid)
                            wores['TechnicianNote'] = workOrder.techniciannote
                            wores['TriageNote'] = workOrder.triagenote
                            wores['DefectCode'] = workOrder.defectcode
                            wores['DefectCodeDescription'] = WorkOrderAdditionalInfoVO.DefectCodeDescription(workOrder.defectcode) #needs to be analysed
                            wores['RepairCode'] = workOrder.repaircode
                            wores['RepairCodeDescription'] = WorkOrderAdditionalInfoVO.RepairCodeDescription(workOrder.repaircode) #further analysis needed
                            wores['Odometer'] = workOrder.odometer
                            wores['Note'] = workOrder.note
                            wores['RepairAction'] = workOrder.repairaction
                            wores['DefectSymptom'] = workOrder.defectsymptom
                            try:
                                wores['PartCost'] = float(workOrder.partcost)
                            except:
                                wores['PartCost'] = 0.0 
                            try:       
                                wores['LaborCost'] = float(workOrder.laborcost)
                            except:
                                wores['LaborCost'] = 0.0 
                            try:    
                                wores['OtherCost'] = float(workOrder.othercost)
                            except:
                                wores['OtherCost'] = 0.0
                            try:        
                                wores['SalesTax'] = float(workOrder.salestax)
                            except:
                                wores['SalesTax'] = 0.0
                            wores['CheckList1'] = getboolvalue(workOrder.checklist1)
                            wores['CheckList2'] = getboolvalue(workOrder.checklist2)
                            wores['CheckList3'] = getboolvalue(workOrder.checklist3)
                            wores['CheckList4'] = getboolvalue(workOrder.checklist4)
                            wores['IsPartInfoClear'] = getboolvalue(workOrder.ispartinfoclear)
                            wores['SignatureDocID'] = workOrder.signaturedocid
                            wores['SmallSignatureDocID'] = workOrder.smallsignaturedocid
                            wores['SignedName'] = workOrder.signedname
                            wores['FinalWorkOrderDocID'] = workOrder.finalworkorderdocid
                            wores['DiagnosedBy'] = getuserinfo(workOrder.diagnosedby)
                            wores['IsCxDissatisfied'] = workOrder.iscxdissatisfied
                            wores['IsPartOrdered'] = workOrder.ispartordered
                            wores['PartOrderBy'] = getuserinfo(workOrder.partorderby)
                            wores['SOPrintDTime'] = workOrder.soprintdtime
                            wores['AptMadeBy'] = getuserinfo(workOrder.aptmadeby)
                            wores['AptMadeDTime'] = workOrder.aptmadedtime
                            wores['QuoteBy'] = getuserinfo(workOrder.quoteby)
                            wores['QuoteDTime'] = workOrder.quotedtime
                            wores['PartOrderDTime'] = workOrder.partorderdtime
                            wores['DiagnoseDTime'] = workOrder.diagnosedtime
                            wores['Triage'] = workOrder.triage
                            wores['ExtraMan'] = workOrder.extraman
                            wores['SealLevel'] = workOrder.seallevel
                            wores['Seq'] = workOrder.seq
                            wores['PartWarehouseID'] = workOrder.partwarehouseid
                            wores['SQBox'] = workOrder.sqbox
                            wores['ITSJobID'] = workOrder.itsjobid
                            wores['ReserveComplete'] = getboolvalue(workOrder.reservecomplete)
                            wores['ReverseITSJobID'] = workOrder.reverseitsjobid
                            wores['MsgToTech'] = workOrder.msgtotech
                            wores['MsgConfirmDTime'] = workOrder.msgconfirmdtime
                            wores['PaymentTransactionID'] = workOrder.paymenttransactionid
                            wores['DefectCodeList'] = None #needs analysis
                            wores['RepairCodeList'] = None #needs analysis
                            wores['Redo'] = WorkOrderAdditionalInfoVO.get_redo(x.id) #needs analysis
                            wores['VisitCount'] = WorkOrderAdditionalInfoVO.get_visitcount(x.id)  #needs analysis
                            wores['LastTechnician'] = None #needs analysis
                            wores['TicketNo'] = None #needs analysis
                            wores['ID'] = workOrder.id
                            wores['OpDTime'] = b.opdtime
                            wores['Status'] = b.status
                            try:
                                t = OpTicket.objects.filter(warehouseid=WarehouseID)[0]
                                ticketres = {}
                                ticketres['ID'] = t.id
                                try:
                                    ticketres['Status'] = OpBase.objects.get(pid=x.id).status
                                except:
                                    ticketres['Status'] = None
                                ticketres['SystemID'] = t.systemid
                                ticketres['TicketNo'] = t.ticketno
                                ticketres['WarehouseID'] = t.warehouseid
                                ticketres['IssueDTime'] = t.issuedtime
                                ticketres['AssignDTime'] = t.assigndtime
                                ticketres['CompleteDTime'] = t.completedtime
                                ticketres['Brand'] = t.brand
                                ticketres['ModelNo'] = t.modelno
                                ticketres['SerialNo'] = t.serialno
                                ticketres['Version'] = t.version
                                ticketres['ProductType'] = t.producttype
                                ticketres['ServiceType'] = t.servicetype
                                ticketres['ProductCategory'] = t.productcategory
                                ticketres['WarrantyStatus'] = t.warrantystatus
                                ticketres['TimeZone'] = t.timezone
                                ticketres['DST'] = t.dst
                                try:
                                    ticketres['Latitude'] = float(t.latitude)
                                except:
                                    ticketres['Latitude'] = t.latitude
                                try:       
                                    ticketres['Longitude'] = float(t.longitude)
                                except:
                                    ticketres['Longitude'] = t.longitude    
                                ticketres['Flag'] = t.flag
                                ticketres['AccountNo'] = t.accountno
                                ticketres['ReplaceModelNo'] = t.replacemodelno
                                ticketres['ReplaceSerialNo'] = t.replaceserialno
                                ticketres['ReturnTrackingNo'] = t.returntrackingno
                                ticketres['DeliveryTrackingNo'] = t.deliverytrackingno
                                try:
                                    ticketres['CreatedOn'] = OpBase.objects.get(id=t.id).createdon
                                except:
                                    ticketres['CreatedOn'] = None
                                ticketres['NSCAccountNo'] = t.nscaccountno
                                ct = NspCompanyContacts.objects.filter(contactid=t.contactid)
                                contacts = {}
                                for c in ct:
                                    contacts['ContactID'] = x.contactid
                                    nspadd = NspAddresses.objects.filter(addressid=c.addressid)
                                    address = {}
                                    for ad in nspadd:
                                        address['Addr'] = ad.address
                                        address['City'] = ad.city
                                        address['State'] = ad.state
                                        address['ZipCode'] = ad.zipcode
                                        address['Country'] = ad.country
                                        #address['CreatedOn'] = ad.createdon
                                        #address['CreatedBy'] = ad.createdby
                                        #address['UpdatedOn'] = ad.updatedon
                                        #address['UpdatedBy'] = ad.updatedby
                                        #if ad.createdby is not None:
                                        #    address['LogBy'] = ad.createdby
                                        #else:
                                        #    address['LogBy'] = ad.updatedby
                                        #address['LogByName'] = None
                                    contacts['Address'] = address
                                    contacts['Name'] = c.name
                                    contacts['Tel'] = c.tel
                                    contacts['Fax'] = c.fax
                                    contacts['Email'] = c.email
                                    contacts['Mobile'] = c.mobile
                                    #contacts['CreatedOn'] = c.createdon
                                    #contacts['CreatedBy'] = c.createdby
                                    #contacts['UpdatedOn'] = c.updatedon
                                    #contacts['UpdatedBy'] = c.updatedby
                                    #if c.createdby is not None:
                                    #    contacts['LogBy'] = c.createdby
                                    #else:
                                    #    contacts['LogBy'] = c.updatedby
                                    #contacts['LogByName'] = None         
                                ticketres['Contact'] = contacts
                                ticketres['Technician'] = getuserinfo(t.techid) 
                                ticketres['GSPNTechnicianID'] = t.gspntechnicianid
                                ticketres['AttentionCode'] = t.attentioncode
                                ticketres['LastAttentionCode'] = WorkOrderAdditionalInfoVO.GetLastAttentionCode(t.serialno) #needs analysis
                                ticketres['AlertMessage'] = t.alertmessage
                                ticketres['ContactLogs'] = WorkOrderAdditionalInfoVO.GetTicketContactLogs(t.id) #needs analysis
                                ticketres['Documents'] = WorkOrderAdditionalInfoVO.GetTicketDocuments(t.id, t.modelno) #needs analysis
                                ticketres['Notes'] = WorkOrderAdditionalInfoVO.GetTicketNotes(t.id) #needs analysis
                                ticketres['Pictures'] = WorkOrderAdditionalInfoVO.GetTicketPictures(t.id) #needs analysis
                                ticketres['SamsungModelDocuments'] = GspnWebServiceClient.GetModelDocuments(t.modelno, CurrentUserID) #needs analysis 
                                for key, value in ticketres.items():
                                    if value=='':
                                        ticketres[key] = None   
                            except Exception as e:
                                print(e)
                                ticketres = None    
                            wores['Ticket'] = ticketres 
                            wores['CreatedOn'] = b.createdon
                            wores['CreatedBy'] = b.createdby
                            wores['UpdatedOn'] = b.updatedon
                            wores['UpdatedBy'] = b.updatedby
                            if b.updatedby is not None:
                                wores['LogBy'] = b.updatedby
                            else:
                                wores['LogBy'] = b.createdby    
                            wores['LogByName'] = None #this is always null as per C# code
                            break
                    except Exception as e:
                        print(e)
                        pass        
                SimpleLogger.do_log(f">>> workOrder= {wores}")
                #workOrder = (OpWorkOrderSerializer(workOrder, many=True)).data
            except Exception as e:
                print(e)
                wores = None
                #return HttpResponseBadRequest(f"WorkOrder not found by SQBox: {location.locationcode}")
        resData['WorkOrder'] = wores
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resData, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class ScheduledSQBoxesController(View):
    "this view is to get WarehouseID, Date, Today and Tomorrow" 
    def get(self, request):
        "accept parameters in GET to process" 
        #API : /servicequick/api/scheduledsqboxes?warehouseId=W0001
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        #Decoding/logging the GET request
        warehouseId = request.GET.get('warehouseId')
        baseDate = request.GET.get('date') 
        onlyTheDay = request.GET.get('onlyTheDay')
        try:
            bOnlyTheDay = eval(onlyTheDay.lower().title()) #converts to boolean type in case the string is true or false
        except:
            bOnlyTheDay = False    
        SimpleLogger.do_log(f"warehouseId= {warehouseId}")
        SimpleLogger.do_log(f"date= {baseDate}")

        reqData = f"WarehouseId : {warehouseId}, Date : {baseDate}, OnlyTheDay : {onlyTheDay}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, warehouseId, "GET", "ScheduledSQBoxesController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)   

        if not warehouseId:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='WarehouseId value not found')            
            return JsonResponse({'message':'WarehouseId value not found'}, safe=False, status=400)
        if not baseDate:
            baseDate = datetime.date.today()
        else:
            baseDate = datetime.datetime.strptime(baseDate, '%Y-%m-%d')    
        SimpleLogger.do_log(f"today= {baseDate}") 
        #Preparing Today Data
        MaxIntValue = 2147483647 # defining a maximum integer value
        SQService = SchedulesService
        todayWorkOrders = SQService.GetScheduledSQBoxes(warehouseId, baseDate, 1, MaxIntValue)
        #Preparing Tomorrow Data which includes data for the next 5 days
        tomorrowWorkOrders = []
        if not bOnlyTheDay or bOnlyTheDay is False:
            for i in [1,2,3,4,5]:
                tomorrow = baseDate + datetime.timedelta(days=i)
                SimpleLogger.do_log(f"tomorrow= {tomorrow}")
                SQService = SchedulesService
                WorkOrders = SQService.GetScheduledSQBoxes(warehouseId, tomorrow, 1, MaxIntValue)
                tomorrowWorkOrders += WorkOrders
        #Preparing for Today SQBoxes
        todaySQBoxes = []
        for wo in todayWorkOrders:
            if wo['SQBOX']:
                sqbox = {}
                sqbox['ApptDate'] = wo['APTSTARTDTIME'].strftime("%m/%d") #converting date to specified format
                sqbox['SQBox'] = wo['SQBOX']
                sqbox['WarehouseID'] = wo['PARTWAREHOUSEID']
                try:
                    wh = NspWareHouses.objects.filter(warehouseid=wo['PARTWAREHOUSEID']).values('nickname', 'code')
                except Exception as e:
                    print(e)
                    wh = [{'nickname':None, 'color':None}]
                sqbox['WarehouseName'] = wh[0].get('nickname')
                sqbox['WarehouseCode'] = wh[0].get('code')
                sqbox['WorkOrderNo'] = wo['WORKORDERNO']
                try:
                    sqbox['TicketNo'] = OpTicket.objects.filter(id=OpBase.objects.filter(id=wo['ID'])[0].pid)[0].ticketno
                except Exception as e:
                    print(e)
                    sqbox['TicketNo'] = "TicketNo not found"   
                sqbox['ReserveComplete'] = True 
                PartDetails = NspPartDetails.objects.filter(opworkorderid=wo['ID'])
                for partdetail in PartDetails:
                    if partdetail.reservestatus!=ReserveStatus.NOT_REQUIRED.value and partdetail.reservestatus!=ReserveStatus.CONFIRMED.value:
                        sqbox['ReserveComplete'] = False
                todaySQBoxes.append(sqbox) 
        #Preparing for Tomorrow SQBoxes
        tomorrowSQBoxes = []
        for wo in tomorrowWorkOrders:
            if wo['SQBOX']:
                sqbox = {}
                sqbox['ApptDate'] = wo['APTSTARTDTIME'].strftime("%m/%d") #converting date to specified format
                sqbox['SQBox'] = wo['SQBOX']
                sqbox['WarehouseID'] = wo['PARTWAREHOUSEID']
                try:
                    wh = NspWareHouses.objects.filter(warehouseid=wo['PARTWAREHOUSEID']).values('nickname', 'code')
                except Exception as e:
                    print(e)
                    wh = [{'nickname':None, 'color':None}]
                sqbox['WarehouseName'] = wh[0].get('nickname')
                sqbox['WarehouseCode'] = wh[0].get('code')
                sqbox['WorkOrderNo'] = wo['WORKORDERNO']
                try:
                    sqbox['TicketNo'] = OpTicket.objects.get(id=OpBase.objects.filter(id=wo['ID'])[0].pid).ticketno
                except Exception as e:
                    print(e)
                    sqbox['TicketNo'] = "TicketNo not found"    
                sqbox['ReserveComplete'] = True 
                PartDetails = NspPartDetails.objects.filter(opworkorderid=wo['ID'])
                for partdetail in PartDetails:
                    if partdetail.reservestatus!=ReserveStatus.NOT_REQUIRED.value and partdetail.reservestatus!=ReserveStatus.CONFIRMED.value:
                        sqbox['ReserveComplete'] = False
                tomorrowSQBoxes.append(sqbox)
        #Preparing for the Response Data by accumulating all the data obtained from the above functions
        resData = {}
        resData['WarehouseID'] = warehouseId
        resData['Date'] = baseDate
        resData['Today'] = todaySQBoxes
        resData['Tomorrow'] = tomorrowSQBoxes
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resData, encoder=DjangoOverRideJSONEncoder, safe=False, status=200) 

class SQBoxLabelsController(View):
    "view to get list of SQBoxLabels"
    def get(self, request):
        "accept parameters in GET to process"
        #API : /servicequick/api/sqboxlabels?PSID=, /servicequick/api/sqboxlabels?warehouseId=&sqbox=
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        if authstat is False:
            return JsonResponse({'message':'invalid headers'}, status=400)
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        #Decoding/logging the GET request
        WarehouseID = request.GET.get('WarehouseID')
        SQBox = request.GET.get('SQBox') 
        PSID = request.GET.get('PSID')
        SimpleLogger.do_log(f"WarehouseID = {WarehouseID}")
        SimpleLogger.do_log(f"SQBox = {SQBox}")
        SimpleLogger.do_log(f"PSID = {PSID}")
        reqData = f"WarehouseId : {WarehouseID}, SQBox : {SQBox}, PSID : {PSID}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, WarehouseID, "GET", "SQBoxLabelsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401) 

        #Validating the passed parameters
        DELIMETER = '|'
        wo = {}
        if not PSID:
            if not WarehouseID or not SQBox:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: PSID or (WarehouseID and SQBox)')            
                return JsonResponse({'message':'Parameter not found: PSID or (WarehouseID and SQBox)'}, safe=False, status=400)
            else:
                sWarehouseID = ''
                sToLocationCode = ''
                if DELIMETER in SQBox:
                    loc = SQBox.split(DELIMETER)
                    try:
                        if loc[0].upper()=='NULL' or not loc[0]:
                            sWarehouseID = WarehouseID
                        else:
                            sWarehouseID = loc[0]
                    except:
                        sWarehouseID = WarehouseID
                    try:
                        sToLocationCode = loc[1]
                    except:
                        pass
                else:
                    sWarehouseID = WarehouseID
                    sToLocationCode = SQBox
                SQService = SchedulesService
                wo = SQService.GetWorkOrderBySQBox(sWarehouseID, sToLocationCode) #getting workorders 
                if wo is not None:
                    wo['Status'] = wo.get('STATUS')
                  
        else:
            iPSID = 0
            if "PS" in PSID[0:2]:
                iPSID = int(PSID[2:len(PSID)-2])
            else:
                iPSID = int(PSID) 
            ps = NspPartSerials.objects.filter(psid=iPSID)
            if not ps.exists():
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='PSID is not in WorkOrder.')            
                return JsonResponse({'message':'PSID is not in WorkOrder.'}, safe=False, status=400)
            else:
                SQService = SchedulesService
                wo = SQService.GetWorkOrder(ps[0].workorderid)
        #in case no data in the workorder(wo)
        if wo is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='401', errMsg="WorkOrder doesn't exist.")            
            return JsonResponse({'message':"WorkOrder doesn't exist."}, safe=False, status=401)
        if wo['Status'] >= WorkOrderStatus.CLOSED.value:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="WorkOrder was already closed.")            
            return JsonResponse({'message':"WorkOrder was already closed."}, safe=False, status=400)
        #Preparing for getting data for SQBox Labels
        SQService = SchedulesService
        getlabelList = SQService.GetSQBoxLabelList(wo['ID'])
        LabelListCount = len(getlabelList)
        if LabelListCount==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg="WorkOrder has no PSID.")            
            return JsonResponse({'message':"WorkOrder has no PSID."}, safe=False, status=400)
        #Preparing for the Summary Data
        Summary = {}
        Summary['Parts'] = LabelListCount
        Summary['Date'] = timezone.now().today().strftime('%m-%d-%Y')
        Summary['Time'] = timezone.now().strftime('%H:%M') 
        #Preparing for the Response Data
        respData = {}
        respData['Summary'] = Summary
        LabelListData = []
        #print("getlabelList = ", getlabelList)
        for x in getlabelList:
            xdict = {}
            xdict['PartNo'] = x.get('PARTNO')
            xdict['BatchID'] = x.get('BATCHID')
            xdict['AccountNo'] = x.get('ACCOUNTNO')
            xdict['WorkOrderNo'] = x.get('WORKORDERNO')
            xdict['AptStartDTime'] = x.get('APTSTARTDTIME')
            xdict['SQBox'] = x.get('SQBOX')
            xdict['WarehouseID'] = x.get('WAREHOUSEID')
            xdict['WarehouseCode'] = x.get('WAREHOUSECODE')
            xdict['LocationCode1'] = x.get('LOCATIONCODE1')
            xdict['LocationCode2'] = x.get('LOCATIONCODE2')
            xdict['LocationCode3'] = x.get('LOCATIONCODE3')
            xdict['PrevDate'] = x.get('PREVTICKETDATE')
            if x.get('TICKETDATE') and x.get('PREVTICKETDATE'):
                try:
                    xdict['PrevDate'] = f"Prev. {x.get('PREVTICKETDATE').strftime('%m-%d-%Y')} ({(x.get('TICKETDATE') - x.get('PREVTICKETDATE')).days}d)"
                except:
                    pass   
            LabelListData.append(xdict)
        respData['Data'] = LabelListData
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(respData, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

class DOsController(View):
    "to get list of DOVO4API"
    def get(self, request):
        "accept params in GET to process"
        #API : /servicequick/api/dos?RefNo=123&closed=true&cancelled=false&open=true
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Decoding/logging the GET request
        warehouseId = request.GET.get('warehouseId')
        date = request.GET.get('date')
        refNo = request.GET.get('refNo')
        strOpen = request.GET.get('open')
        strClosed = request.GET.get('closed')
        strCancelled = request.GET.get('cancelled')
        strPage = request.GET.get('page') 
        strSize = request.GET.get('pageSize')
        SimpleLogger.do_log(f"warehouseId = {warehouseId}")
        SimpleLogger.do_log(f"date = {date}")
        SimpleLogger.do_log(f"refNo = {refNo}")
        SimpleLogger.do_log(f"open = {strOpen}")
        SimpleLogger.do_log(f"closed = {strClosed}")
        SimpleLogger.do_log(f"cancelled = {strCancelled}")
        SimpleLogger.do_log(f"page = {strPage}")
        SimpleLogger.do_log(f"pageSize = {strSize}")
        reqData = f"WarehouseId : {warehouseId}, Date : {date}, RefNo : {refNo}, Open : {strOpen}, Closed : {strClosed}, Cancelled : {strCancelled}, Page : {strPage}, PageSize : {strSize}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, refNo if refNo else warehouseId, "GET", "DOsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401) 
      
        #Defining variables
        if strOpen:
            if strOpen=='1' or strOpen.lower()=='true':
                includeOpen = True
            else:
                includeOpen = False
        else:
            includeOpen = False

        if strClosed:
            if strClosed=='1' or strClosed.lower()=='true':
                includeClosed = True
            else:
                includeClosed = False
        else:
            includeClosed = False

        if strCancelled:
            if strCancelled=='1' or strCancelled.lower()=='true':
                includeCancelled = True
            else:
                includeCancelled = False
        else:
            includeCancelled = False

        if strPage:
            try:
                pageNo = int(strPage)
                if pageNo==0:
                    pageNo = 1
            except:
                pageNo = 1
        else:
            pageNo = 1

        if strSize:
            try:
                pageSize = int(strSize)
            except:
                pageSize = settings.DEFAULT_PAGE_SIZE
        else:
            pageSize = settings.DEFAULT_PAGE_SIZE

        doNo = None
        isDODetail = False
        itemNo = 0
        dd = []
        #If refNo is available, try to get a list of data from the table NSPDODETAILS
        if refNo:
            doNo = refNo[0:min(10, len(refNo))]
            integer_try_parse = False
            if len(refNo) > 10:
                try:
                    integer_try_parse = bool(int(refNo[10:len(refNo)-10]))
                except:
                    pass
                if integer_try_parse is True:
                    itemNo = int(refNo[10:len(refNo)-10]) 
                    isDODetail = True
                    SQService = SchedulesService
                    dd = SQService.GetDODetailByDONoAndItemNo(doNo, itemNo)
                    print('dd is ', dd)
        #Running function to create a list of DOs
        SQService = SchedulesService
        itemList = SQService.GetDOList(warehouseId, date, refNo, includeOpen, includeClosed, includeCancelled, pageNo, pageSize) 
        #Preparing the List thus obtained for API Response
        itemList4Api = [] 
        for d in itemList:
            dv = {}
            dv['DOID'] = d['doid']
            dv['CreatedBy'] = d['createdby']
            dv['CreatedOn'] = d['createdon']
            dv['UpdatedBy'] = d['updatedby']
            dv['UpdatedOn'] = d['updatedon']
            dv['AccountNo'] = d['accountno']
            dv['WarehouseID'] = d['warehouseid']
            dv['DONo'] = d['dono']
            dv['DODate'] = d['dodate']
            dv['RefNo'] = d['refno']
            dv['ItemQty'] = d['itemqty']
            dv['TotalQty'] = d['totalqty']
            dv['Amount'] = d['amount']
            dv['Status'] = d['status']
            dv['ShipmentID'] = d['shipmentid']
            dv['ETA'] = d['eta']
            dv['TrackingNo'] = d['trackingno']
            dv['DODetails'] = dd
            itemList4Api.append(dv)
        #Getting total count of DOs items from a function
        totalItemCount = SQService.GetDOListCount(warehouseId, date, refNo, includeOpen, includeClosed, includeCancelled)
        #Creating a dict to be used for Json Response Data
        resultList = {}
        resultList['WarehouseID'] = warehouseId
        resultList['Date'] = date
        resultList['RefNo'] = request.GET.get('refNo')
        resultList['Open'] = includeOpen
        resultList['Closed'] = includeClosed
        resultList['Cancelled'] = includeCancelled
        resultList['Page'] = pageNo
        resultList['PageSize'] = pageSize
        resultList['TotalItemCount'] = totalItemCount
        resultList['ListSize'] = len(itemList4Api)
        resultList['List'] = itemList4Api
        resultList['LogID'] = BaseApiController.getlogid('GET', 'DOsController', CurrentUserID) 
        #Running a condition to modify the resultList dict
        if isDODetail is True and itemNo > 0:
            for d in itemList4Api:
                resultList['TotalItemCount'] = 1
                d['DONo'] = refNo
                d['DODetails'] = None
                d['DODetails'] = dd
        #Finally returning the ResultList as API response
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class PartSerialListController(View):
    "to get list of parts and part info"
    def get(self, request):
        "accept params in GET to process"
        # GET api/partseriallist?warehouseId=1&locationCode=A&partNo=B
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Decoding/logging the GET request
        warehouseId = request.GET.get('warehouseId')
        locationCode = request.GET.get('locationCode') 
        partNo = request.GET.get('partNo')
        if not warehouseId:
            return HttpResponseBadRequest("Parameter required: warehouseId")
        SimpleLogger.do_log(f"warehouseId={warehouseId}") 
        SimpleLogger.do_log(f"locationCode={locationCode}")
        SimpleLogger.do_log(f"partNo={partNo}")
        token = request.META.get('HTTP_KW_TOKEN')
        reqData = f"warehouseId : {warehouseId}, locationCode : {locationCode}, partNo : {partNo}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(warehouseId), "GET", "PartSerialListController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401) 

        #Validating/Checking the supplied parameters
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

        itemList = PartSupport.GetPartSerialList(warehouseId, locationCode, partNo, 1, 2147483647) #2147483647 is int.MaxValue as per C# code
        #Preparing the response data
        resultList = {}
        resultList['WarehouseID'] = warehouseId
        resultList['LocationCode'] = locationCode
        resultList['PartNo'] = partNo
        resultList['ListSize'] = len(itemList)
        resultList['List'] = itemList
        resultList['LogID'] = BaseApiController.getlogid('GET', "PartSerialListController", CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class DispatchTicketsController(View):
    "to get the list of dispatch tickets based on warehouse id"
    def get(self, request):
        "accept WareHouseID in GET to process"
        # API : GET servicequick/api/dispatchtickets
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Decoding/logging the GET request
        warehouseId = request.GET.get('warehouseId')
        apptDate = request.GET.get('apptDate')

        reqData = f"warehouseId : {warehouseId}, apptDate : {apptDate}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(warehouseId), "GET", "DispatchTicketsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        if not warehouseId:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: warehouseId')            
            return JsonResponse({'message':'Parameter not found: warehouseId'}, safe=False, status=400)
        if apptDate:
            try:
                apptDate = datetime.datetime.strptime(apptDate, "%Y-%m-%d")
            except:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='apptDate has invalid date format. Must be in YYYY-MM-DD"')            
                return JsonResponse({'message':'apptDate has invalid date format. Must be in YYYY-MM-DD"'}, safe=False, status=400)
        if not apptDate:
            apptDate = datetime.date.strftime("%Y-%m-%d")
        #Validation for includeNew parameter    
        includeNew = True
        strIncludeNew = request.GET.get('includeNew')
        if strIncludeNew:
            if strIncludeNew=='1' or strIncludeNew.lower()=='true':
                includeNew = True
            else:
                includeNew = False
        #Validation for multiRegion
        multiRegion = True
        strMultiRegion = request.GET.get('multiRegion')
        if strMultiRegion:
            if strMultiRegion=='1' or strMultiRegion.lower()=='true':
                multiRegion = True
            else:
                multiRegion = False
        
        SimpleLogger.do_log(f"warehouseId={warehouseId}", "debug") 
        SimpleLogger.do_log(f"apptDate={apptDate}", "debug")
        SimpleLogger.do_log(f"includeNew={includeNew}", "debug")
        SimpleLogger.do_log(f"multiRegion={multiRegion}", "debug")
        itemList = TicketSupport.GetDispatchTickets(warehouseId, apptDate, includeNew, multiRegion) 
        resultList = {}
        resultList['WarehouseId'] = warehouseId
        resultList['ApptDate'] = apptDate
        resultList['IncludeNew'] = includeNew
        resultList['MultiRegion'] = multiRegion 
        resultList['ListSize'] = len(itemList)
        resultList['List'] = itemList
        resultList['LogID'] = BaseApiController.getlogid("GET", "DispatchTicketsController", CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class LastUserTicketController(View):
    "to get simple ticket assigned to user"
    def get(self, request):
        "accept userID in GET to process"
        # GET servicequick/api/lastuserticket?userId=12345
        userId = request.GET.get('userId')
        try:
            userId = int(userId)
        except:
            pass
        SimpleLogger.do_log(f">>> Get()...{userId}")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        # Logging and Validating the request
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'userId':userId}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(userId), "GET", "LastUserTicketController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
      
        nspUser = NSPSupport.GetNSPUserByUserID(userId)
        if nspUser is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='401', errMsg=f"NSPUser not found: {userId}")            
            return JsonResponse({'message':f"NSPUser not found: {userId}"}, safe=False, status=401)
        # Preparing for the Simple Ticket
        ticket = TicketSupport.GetSimpleTicketByTicketNo(nspUser['CurrentTicketNo'])
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(ticket, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
    def post(self, request):
        "to update currentTicketNo for an user"
        # POST servicequick/api/lastuserticket
        SimpleLogger.do_log(">>> Post()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        if authstat is False:
            return JsonResponse({'message':'invalid headers'}, status=400)
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")

        SimpleLogger.do_log(f"content= {content}", "debug")
        UserID = received_json_data.get("UserID")
        TicketNo = received_json_data.get('TicketNo')
        try:
            UserID = int(UserID)
        except:
            pass
        userTicket = f"UserID : {UserID}, TicketNo : {TicketNo}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'userTicket':userTicket}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(UserID), "POST", "LastUserTicketController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        
        SimpleLogger.do_log(f"userTicket= {userTicket}", "debug")
        # Validation
        nspUser = NSPSupport.GetNSPUserByUserID(UserID)
        if nspUser is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='401', errMsg=f"NSPUser not found: {UserID}")            
            return JsonResponse({'message':f"NSPUser not found: {UserID}"}, safe=False, status=401)
        # Updating nspUser with new TicketNo
        ns = Nspusers.objects.filter(userid=UserID)
        if ns[0].createdon is None:
            ns.update(createdon=timezone.now(), createdby=CurrentUserID, currentticketno=TicketNo)
        else:
            ns.update(updatedon=timezone.now(), updatedby=CurrentUserID, currentticketno=TicketNo)
        SimpleLogger.do_log("NSPUser saved", "debug")
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return HttpResponse("NSPUser saved successfully")                                                    

                                                                                                              
                     
                                           




                        





                                                                        


                


                                        




                

        



        
               
 


            

           

       
                           



                







                                                                     

