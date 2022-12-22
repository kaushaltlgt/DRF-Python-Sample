import datetime, json, re
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from nsp_user.authentication import KWAuthentication
from django.http import HttpResponseGone, HttpResponseNotFound, HttpResponseServerError, JsonResponse, HttpResponseBadRequest, HttpResponse
from functions.kwlogging import SimpleLogger, AdvancedLogger, BaseApiController
from functions.querymethods import DBIDGENERATOR
from functions.xmlfunctions import get_xml_node
from functions.smtpgateway import sendmailoversmtp
from repair_tasks.models import NspConfigs
from schedules_detail.support import PartSupport
from schedules_detail.schedules2 import SchedulesService
from schedules_detail.models import NspPartSerials, NspDoDetails, NspPos
from repair_tasks.support import JobSupport, WareHouseSupport
from schedules_list_map.schedules import JobType, JobStatus, JobDetailStatus, PartSerialStatus, OutType, GspnWebServiceClient, WarehouseType
from schedules_list_map.support import NSPWSClient
from nsp_user.support import NSPSupport
from nsp_user.support import DjangoOverRideJSONEncoder

# Create your views here.

class RAReasonCodesController(View):
    "to list repair(ra) reasons"
    def get(self, request):
        "accept request in GET to process"
        #GET api/rareasons
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
       
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':""}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, "", "GET", "RAReasonCodesController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        
        #Defining list variables
        SUBREASON_807 = ["1|Panel Scratch/Scuff", "2|Chassis Scratch", "9|Non-Panel"]
        SUBREASON_809 = ["1|Panel Broken", "2|Panel Bent", "3|Panel Scratched", "4|Concealed Damage", "5|Broken", "6|Bent", "7|Scratched"]
        SUBREASON_816 = ["1|No Video", "2|Picture Distortion (Abnormal Video)", "3|Backlight Failure (Dark Dim, Light Leak)", "4|Line Defect (H-Line, V-Line, H-Block, V-Block)", "5|Pixel Defect (Dead Pixel, Bright Dot)", "6|Foreign Substance (Particle, Spot, Stain)",  "9|Non-Panel"]
        #Getting List of config value
        configValue = ''
        RAReasonList = []
        run_sql = NspConfigs.objects.filter(code='RAREASONS').values('value')
        for x in run_sql:
            configValue += x['value']
        #print(configValue)    
        if configValue:
            for raVal in configValue.split('|'):
                raReason = {}
                subReason = {}
                reason1 = raVal.split(',')
                try:
                    raReason['Code'] = reason1[0].strip()
                except IndexError:
                    pass
                try:    
                    raReason['Description'] = reason1[1].strip()
                except IndexError:
                    pass     
                if raReason['Code']=='807':
                    for subVal in SUBREASON_807:
                        reason2 = subVal.split('|')
                        try:
                            subReason['Code'] = reason2[0].strip()
                        except IndexError:
                            pass
                        try:    
                            subReason['Description'] = reason2[1].strip()
                        except IndexError:
                            pass    
                        raReason['SubReason'] = subReason
                elif raReason['Code']=='809':
                    for subVal in SUBREASON_809:
                        reason2 = subVal.split('|')
                        try:
                            subReason['Code'] = reason2[0].strip()
                        except IndexError:
                            pass
                        try:    
                            subReason['Description'] = reason2[1].strip()
                        except IndexError:
                            pass    
                        raReason['SubReason'] = subReason 
                elif raReason['Code']=='816':
                    for subVal in SUBREASON_816:
                        reason2 = subVal.split('|')
                        try:
                            subReason['Code'] = reason2[0].strip()
                        except IndexError:
                            pass
                        try:    
                            subReason['Description'] = reason2[1].strip()
                        except IndexError:
                            pass    
                        raReason['SubReason'] = subReason
                else:
                    pass
                RAReasonList += [raReason] #adding the repair reasons to the Result List
                resultList = {}
                resultList['ListSize'] = len(RAReasonList)
                resultList['List'] = RAReasonList
                resultList['LogID'] = BaseApiController.getlogid('GET', 'RAReasonCodesController', CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)        
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class RAShippingController(View):
    "to check about RA Shipping"
    def post(self, request):
        "accept parameters in POST to proceed"
        # POST servicequick/api/rashipping
        SimpleLogger.do_log(">>> Post()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        token = request.META.get('HTTP_KW_TOKEN')
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        SimpleLogger.do_log(f"content= {content}")
        PSID = received_json_data.get("PSID")
        WarehouseID = received_json_data.get('WarehouseID')
        TrackingNo = received_json_data.get('TrackingNo')
        try:
            PSID = int(PSID)
        except:
            pass

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(PSID), "POST", "RAShippingController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)    
        
        SimpleLogger.do_log(f"reqData= {received_json_data}") 
        #Validating the request
        if not PSID or PSID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Value not found: PSID')            
            return JsonResponse({'message':'Value not found: PSID'}, safe=False, status=404)
        if not WarehouseID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Value not found: WarehouseID')            
            return JsonResponse({'message':'Value not found: WarehouseID'}, safe=False, status=404)
        if not TrackingNo:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Value not found: TrackingNo')            
            return JsonResponse({'message':'Value not found: TrackingNo'}, safe=False, status=404)
        if TrackingNo.upper()[:2]!='PL' and TrackingNo.upper()[:2]!='1Z':
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Invalid Tracking No')            
            return JsonResponse({'message':'Invalid Tracking No'}, safe=False, status=404)
        #Processing the data
        partSerial = PartSupport.GetPartSerial(PSID)
        if partSerial is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"PartSerial '{PSID}' was not found.")            
            return JsonResponse({'message':f"PartSerial '{PSID}' was not found."}, safe=False, status=500)
        if partSerial['WarehouseID']!=WarehouseID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"PartSerial '{PSID}' does not belong to the warehouse '{WarehouseID}'.")            
            return JsonResponse({'message':f"PartSerial '{PSID}' does not belong to the warehouse '{WarehouseID}'."}, safe=False, status=500)
        if partSerial['RANo'] is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"RA has not been issued yet. {PSID}")            
            return JsonResponse({'message':f"RA has not been issued yet. {PSID}"}, safe=False, status=500)
        if partSerial['JobDetailID']!=0:
            jd = JobSupport.GetNSPJobDetail(partSerial['JobDetailID'])
            if jd is None:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='CANNOT ship RA without any order.')            
                return JsonResponse({'message':'CANNOT ship RA without any order.'}, safe=False, status=500)
            elif jd['NSPJob']['JobType']!=JobType.RA_SHIP.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The part is on another job.')            
                return JsonResponse({'message':'The part is on another job.'}, safe=False, status=500)
            elif jd['NSPJob']['Status']==JobStatus.COMPLETED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The job was completed already.')            
                return JsonResponse({'message':'The job was completed already.'}, safe=False, status=500)
            elif jd['NSPJob']['Status']==JobStatus.CANCELLED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The job was cancelled.')            
                return JsonResponse({'message':'The job was cancelled.'}, safe=False, status=500)
            elif jd['Status']==JobDetailStatus.COMPLETED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The jobDetail was completed already.')            
                return JsonResponse({'message':'The jobDetail was completed already.'}, safe=False, status=500)
            elif jd['Status']==JobDetailStatus.CANCELLED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The jobDetail was cancelled.')            
                return JsonResponse({'message':'The jobDetail was cancelled.'}, safe=False, status=500)
            else:
                pass
        # Setting different values for partSerial dict
        partSerial['TrackingNo'] = TrackingNo
        partSerial['ShipDate'] = datetime.datetime.today()
        if TrackingNo.upper()[:2]=='PL' or TrackingNo.upper()[:2]=='1Z':
            partSerial['Status'] = PartSerialStatus.RA_SHIPPED.value
        else:
            return HttpResponseServerError("Invalid Tracking No.") 
        partSerial['AuditID'] = DBIDGENERATOR.process_id("NSPPartSerialsAudit_SEQ")
        partSerial['Method'] = "POST" 
        # Saving Part Serial
        NspPartSerials.objects.filter(psid=partSerial['PSID']).update(trackingno=partSerial['TrackingNo'], shipdate=partSerial['ShipDate'],status=partSerial['Status'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
        PartSupport.SavePartSerialAudit(partSerial, CurrentUserID)
        SimpleLogger.do_log(f"PartSerial saved: {partSerial}", "debug")
        # Sending XML data to the remote server
        if partSerial['JobDetailID']!=0:
            NSPWSClient.ExecuteJobDetail(token, JobType.RA_SHIP.value, partSerial['JobDetailID'])
        # Finally returns the JSON response
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(partSerial, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class RAIssueRequestController(View):
    "to issue RA(repair) tasks"
    def post(self, request):
        "accept parameters in POST to process"
        # POST servicequick/api/rarequest
        SimpleLogger.do_log(">>> Post()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        token = request.META.get('HTTP_KW_TOKEN')
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        SimpleLogger.do_log(f"content= {content}")
        PSID = received_json_data.get("PSID")
        WarehouseID = received_json_data.get('WarehouseID')
        ReturnCode = received_json_data.get('ReturnCode')
        ReturnReason = received_json_data.get('ReturnReason')
        SubReasonCode = received_json_data.get('SubReasonCode')
        Note = received_json_data.get('Note')
        FileName = received_json_data.get('FileName')
        Binary = received_json_data.get('Binary')
        try:
            PSID = int(PSID)
        except:
            pass

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(PSID), "POST", "RAIssueRequestController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)       
       
        SimpleLogger.do_log(f"reqData= {received_json_data}") 
        # Validating the request parameters
        if not PSID or PSID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: PSID')            
            return JsonResponse({'message':'Value not found: PSID'}, safe=False, status=500)
        if not WarehouseID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: WarehouseID')            
            return JsonResponse({'message':'Value not found: WarehouseID'}, safe=False, status=500)
        if not ReturnCode:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: ReturnCode')            
            return JsonResponse({'message':'Value not found: ReturnCode'}, safe=False, status=500)
        if not ReturnReason:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: ReturnReason')            
            return JsonResponse({'message':'Value not found: ReturnReason'}, safe=False, status=500)
        if ReturnCode=='807' or ReturnCode=='809' or ReturnCode=='816':
            if not SubReasonCode:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: SubReasonCode')            
                return JsonResponse({'message':'Value not found: SubReasonCode'}, safe=False, status=500)
        if ReturnCode=='813' and FileName is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='813 : Require 1 or more picture')            
            return JsonResponse({'message':'813 : Require 1 or more picture'}, safe=False, status=500)
        elif ReturnCode=='807' and FileName is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='807 : Require 4 or more picture')            
            return JsonResponse({'message':'807 : Require 4 or more picture'}, safe=False, status=500)
        else:
            pass
        # Defining some constants
        BEING_PROCCESSED = "is currently being processed"
        BALANCE_CHECK_FAIL = "W/B Parts Balance Check Failure" 
        TOO_MANY_REQUESTS = "Too many requests. Please try it later."
        # Processing the data
        partSerial = PartSupport.GetPartSerial(PSID)
        if partSerial is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"PartSerial '{PSID}' was not found.")            
            return JsonResponse({'message':f"PartSerial '{PSID}' was not found."}, safe=False, status=500)
        if partSerial['RANo']: # If a RA has already been issued
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return JsonResponse(partSerial, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
        if partSerial['OutType']!=OutType.RA.value:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Please move the part to RA location first.')            
            return JsonResponse({'message':'Please move the part to RA location first.'}, safe=False, status=500)
        if partSerial['JobDetailID']!=0:
            jd = JobSupport.GetNSPJobDetail(partSerial['JobDetailID'])
            if jd is None:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='CANNOT ship RA without any order.')            
                return JsonResponse({'message':'CANNOT ship RA without any order.'}, safe=False, status=500)
            elif jd['NSPJob']['JobType']!=JobType.RA_SUBMIT.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The part is on another job.')            
                return JsonResponse({'message':'The part is on another job.'}, safe=False, status=500)
            elif jd['NSPJob']['Status']==JobStatus.COMPLETED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The job was completed already.')            
                return JsonResponse({'message':'The job was completed already.'}, safe=False, status=500)
            elif jd['NSPJob']['Status']==JobStatus.CANCELLED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The job was cancelled.')            
                return JsonResponse({'message':'The job was cancelled.'}, safe=False, status=500)
            elif jd['Status']==JobDetailStatus.COMPLETED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The jobDetail was completed already.')            
                return JsonResponse({'message':'The jobDetail was completed already.'}, safe=False, status=500)
            elif jd['Status']==JobDetailStatus.CANCELLED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='The jobDetail was cancelled.')            
                return JsonResponse({'message':'The jobDetail was cancelled.'}, safe=False, status=500)
            else:
                pass
        else:
            if ReturnCode=="839":
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='CANNOT submit PNN RA without any order.')            
                return JsonResponse({'message':'CANNOT submit PNN RA without any order.'}, safe=False, status=500)
        # Getting the data from NspDos table
        SQService = SchedulesService
        d = SQService.GetDOByNo(partSerial['DONo'])
        # Comparing different values
        if partSerial['IsOFS']:
            if ReturnCode=="839":
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='OFS part CANNOT be returned as PNN.')            
                return JsonResponse({'message':'OFS part CANNOT be returned as PNN.'}, safe=False, status=500)
            if d is not None:
                if d['DODate'] < datetime.datetime.strptime("2018-08-01", "%Y-%m-%d"):
                    KEPT_DAYS = 60
                else:
                    KEPT_DAYS = 45
            if ReturnCode=="840" and (datetime.datetime.today() - d['DODate']).days < KEPT_DAYS:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"OFS part must be kept for {KEPT_DAYS} days.")            
                return JsonResponse({'message':f"OFS part must be kept for {KEPT_DAYS} days."}, safe=False, status=500)
        # Setting DOVO values  
        strDate = datetime.date.today() + datetime.timedelta(days=90) #getting date after 90 days
        strDate = datetime.date.strftime(strDate, "%Y-%m-%d") #getting Date as string

        psDO = None
        nspDo = None
        if partSerial['DONo']:
            psDO = SQService.GetDOByNo(partSerial['DONo'])
        if psDO is not None:
            nspDo['ACCOUNTNO'] = psDO['AccountNo']
            nspDo['DODATE'] = psDO['DODate']
            nspDo['DONO'] = psDO['DONo']
            nspDo['REFNO'] = psDO['RefNo']
        if nspDo is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"DO was not found by {PSID}.")            
            return JsonResponse({'message':f"DO was not found by {PSID}."}, safe=False, status=500)

        doDetail = SQService.GetDODetailByPSID(nspDo['DONO'], partSerial['PartNo'], partSerial['ItemNo'])

        if doDetail is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=f"DO detail was not found by {PSID}.")            
            return JsonResponse({'message':f"DO detail was not found by {PSID}."}, safe=False, status=500)

        itemNo = str(doDetail['InvoiceItemNo']).rjust(6, '0') #pads the string with 0 on the left to get total string length as 6
        if not doDetail['RefNo']:
            invoiceNo = nspDo['REFNO']
        else:
            invoiceNo = doDetail['RefNo']
        if settings.DEBUG is True: #if project is running in development mode
            partSerial['RANo'] = "12345678790"
            partSerial['RAReason'] = ReturnCode + ": " + ReturnReason
            partSerial['RADTime'] = datetime.datetime.now()
            partSerial['RANote'] = Note + ">>" + invoiceNo + ">>" + itemNo
            partSerial['RADONo'] = nspDo['DONO']
            partSerial['RAAccountNo'] = nspDo['ACCOUNTNO']
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
            return JsonResponse(partSerial, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

        sSubReasonCode = SubReasonCode
        if ReturnCode=="839" and not sSubReasonCode:
            sSubReasonCode = "1"
        #Calling gspnWsCient
        sBinary = Binary
        if sBinary:
            sBinary = re.sub(r'\s+', '', sBinary) #removing all whitespaces, tabs, new lines etc from the string
        xmlData = GspnWebServiceClient.SetPartReturnRequest(partSerial['PSID'],nspDo['ACCOUNTNO'],invoiceNo,ReturnCode,ReturnReason,sSubReasonCode,itemNo,"1",FileName,sBinary,CurrentUserID)
        # if temporary error from GSPN
        # Try again later.
        sErrorMsg = get_xml_node(xmlData, "ErrMsg")
        from_address = settings.NSP_INFO_EMAIL
        to_address = "developer_nsp@kwitech.com"
        email_content = sErrorMsg
        if sErrorMsg:
            if BEING_PROCCESSED in sErrorMsg:
                email_title = f"[SQ_API]RA Temp Error : PS {PSID}"
                sendmailoversmtp(to_address, email_title, email_content, from_address)
                return HttpResponseServerError("Temporary Error!!" + "\n" + "Please try again later.")
            if TOO_MANY_REQUESTS in sErrorMsg:
                email_title = f"[SQ_API]RA Error TOO_MANY_REQUESTS : PS {PSID}"
                sendmailoversmtp(to_address, email_title, email_content, from_address)
                return HttpResponseServerError("TOO MANY REQUESTS!!" + "\n" + "Please try again 30 minutes later.") 
            if BALANCE_CHECK_FAIL in sErrorMsg:
                email_title = f"[SQ_API]RA Balance Check Error : PS {PSID}"
                sendmailoversmtp(to_address, email_title, email_content, from_address)
                return HttpResponseServerError("GSPN Balance Check Fail!!" + "\n" + "Please contact manager.") 
        # Checking value for retCode in the xmlData received
        retCode = get_xml_node(xmlData, "RetCode")
        SimpleLogger.do_log(f"retCode= {retCode}")
        if retCode and retCode=='0':
            #indicates Success
            rmaNo = get_xml_node(xmlData, "//RMANo")
            if len(rmaNo)==9:
                partSerial['RANo'] = "0" + rmaNo
            else:
                partSerial['RANo'] = rmaNo
            partSerial['RAReason'] = ReturnCode + ": " + ReturnReason
            partSerial['RADTime'] = datetime.datetime.now()
            partSerial['RANote'] = Note
            partSerial['RADONo'] = nspDo['DONO']
            partSerial['RAAccountNo'] = nspDo['ACCOUNTNO']
            partSerial['Status'] = PartSerialStatus.RA_SUBMITTED.value

            partSerial['AuditID'] = DBIDGENERATOR.process_id("NSPPartSerialsAudit_SEQ")
            partSerial['Method'] = "POST"

            NspPartSerials.objects.filter(psid=partSerial['PSID']).update(rano=partSerial['RANo'],rareason=partSerial['RAReason'],ranote=partSerial['RANote'],radono=partSerial['RADONo'],raaccountno=partSerial['RAAccountNo'],status=partSerial['Status'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
            PartSupport.SavePartSerialAudit(partSerial, CurrentUserID)
            SimpleLogger.do_log(f"PartSerial saved: {partSerial}", "debug")

            # Job for RA submit
            if partSerial['JobDetailID']!=0:
                wsResult = NSPWSClient.ExecuteJobDetail(token, JobType.RA_SUBMIT.value, partSerial['JobDetailID'])
                try:
                    wsreserror = get_xml_node(wsResult.text, "ERROR")
                    if wsreserror:
                        return HttpResponseServerError(wsreserror)
                except:
                    pass
            if doDetail['DODetailID'] > 0:
                doDetail['RAQty'] = doDetail['RAQty'] + 1
                if (doDetail['RAQty'] + doDetail['ClaimQty'])==doDetail['Qty']:
                    doDetail['ISAvailable'] = True
                #Saving DoDetails
                NspDoDetails.objects.filter(dodetailid=doDetail['DODetailID']).update(raqty=doDetail['RAQty'],isavailable=doDetail['ISAvailable'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
                SimpleLogger.do_log(f"DoDetail saved: {doDetail}", "debug")

            SimpleLogger.do_log("SetStockAdjust >>>", "debug")
            try:
                ship_to = NspPos.objects.filter(pono=doDetail['PONo'])[0].shipto
            except:
                ship_to = None    
            xmlData = GspnWebServiceClient.SetStockAdjust(partSerial['RAAccountNo'], ship_to, "05", partSerial['PartNo'], 1, CurrentUserID)
            retCode = get_xml_node(xmlData, "RetCode")
            SimpleLogger.do_log(f"retCode= {retCode}")
        else:
            if doDetail['DODetailID'] > 0:
                doDetail['RAQty'] = doDetail['RAQty'] + 1
                doDetail['ISAvailable'] = True
                doDetail['ReturnMessage'] = sErrorMsg #Saving DoDetails:
                NspDoDetails.objects.filter(dodetailid=doDetail['DODetailID']).update(raqty=doDetail['RAQty'],isavailable=doDetail['ISAvailable'],returnmessage=doDetail['ReturnMessage'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
                SimpleLogger.do_log(f"DoDetail ErrMsg: {doDetail['ReturnMessage']}", "debug")
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=sErrorMsg)            
            return JsonResponse({'message':sErrorMsg}, safe=False, status=500)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)     
        return JsonResponse(partSerial, encoder=DjangoOverRideJSONEncoder, safe=False, status=200) 


@method_decorator(csrf_exempt, name='dispatch')
class CoreShippingController(View):
    "to do core shipping"
    def post(self, request):
        "to accept parameters in POST"
        # POST servicequick/api/CoreShipping
        SimpleLogger.do_log(">>> Post()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        if authstat is False:
            return JsonResponse({'message':'invalid headers'}, status=400)
        #decoding json data and logging the request
        content = request.body.decode("utf-8")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        token = request.META.get('HTTP_KW_TOKEN')
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")
        SimpleLogger.do_log(f"content= {content}")
        PSID = received_json_data.get("PSID")
        WarehouseID = received_json_data.get('WarehouseID')
        TrackingNo = received_json_data.get('TrackingNo')
        try:
            PSID = int(PSID)
        except:
            pass

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(PSID), "POST", "CoreShippingController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)        
        
        SimpleLogger.do_log(f"reqData= {received_json_data}")
        # Validating the request parameters
        if not PSID or PSID==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: PSID')            
            return JsonResponse({'message':'Value not found: PSID'}, safe=False, status=500)
        if not WarehouseID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: WarehouseID')            
            return JsonResponse({'message':'Value not found: WarehouseID'}, safe=False, status=500)
        if not TrackingNo:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Value not found: TrackingNo')            
            return JsonResponse({'message':'Value not found: TrackingNo'}, safe=False, status=500)
        if TrackingNo.upper()[:2]!='PL' and TrackingNo.upper()[:2]!='1Z':
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg='Invalid Tracking No"')            
            return JsonResponse({'message':'Invalid Tracking No"'}, safe=False, status=500)
        # Processing the data
        partSerial = PartSupport.GetPartSerial(PSID)
        if partSerial is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg='Value not found: PSID')            
            return JsonResponse({'message':'Value not found: PSID'}, safe=False, status=404)
        if partSerial['WarehouseID']!=WarehouseID:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"PartSerial '{PSID}' does not belong to the warehouse '{WarehouseID}'.")            
            return JsonResponse({'message':f"PartSerial '{PSID}' does not belong to the warehouse '{WarehouseID}'."}, safe=False, status=400)
        if not partSerial['CoreRANo']:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Core has not been issued yet. {partSerial['PSID']}")            
            return JsonResponse({'message':f"Core has not been issued yet. {partSerial['PSID']}"}, safe=False, status=400)
        if partSerial['CoreValue']==0:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"This part is not a Core part. {partSerial['PSID']}")            
            return JsonResponse({'message':f"This part is not a Core part. {partSerial['PSID']}"}, safe=False, status=400)
        if partSerial['JobDetailID']!=0:
            jd = JobSupport.GetNSPJobDetail(partSerial['JobDetailID'])
            if jd is None:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='CANNOT ship RA without any order.')            
                return JsonResponse({'message':'CANNOT ship RA without any order.'}, safe=False, status=400)
            elif jd['NSPJob']['JobType']!=JobType.CORE_SHIP.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='The part is on another job.')            
                return JsonResponse({'message':'The part is on another job.'}, safe=False, status=400)
            elif jd['NSPJob']['Status']==JobStatus.COMPLETED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='410', errMsg='The job was completed already.')            
                return JsonResponse({'message':'The job was completed already.'}, safe=False, status=410)
            elif jd['NSPJob']['Status']==JobStatus.CANCELLED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='410', errMsg='The job was cancelled.')            
                return JsonResponse({'message':'The job was cancelled.'}, safe=False, status=410)
            elif jd['Status']==JobDetailStatus.COMPLETED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='410', errMsg='The jobDetail was completed already.')            
                return JsonResponse({'message':'The jobDetail was completed already.'}, safe=False, status=410)
            elif jd['Status']==JobDetailStatus.CANCELLED.value:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='410', errMsg='The jobDetail was cancelled.')            
                return JsonResponse({'message':'The jobDetail was cancelled.'}, safe=False, status=410)
            else:
                pass 
        # Setting different values for partSerial dict
        partSerial['TrackingNo'] = TrackingNo
        partSerial['ShipDate'] = datetime.datetime.today()
        if TrackingNo.upper()[:2]=='PL' or TrackingNo.upper()[:2]=='1Z':
            partSerial['Status'] = PartSerialStatus.CORE_SHIPPED.value
        else:
            return HttpResponseBadRequest("Invalid Tracking No.") 
        partSerial['AuditID'] = DBIDGENERATOR.process_id("NSPPartSerialsAudit_SEQ")
        partSerial['Method'] = "POST" 
        # Saving Part Serial
        NspPartSerials.objects.filter(psid=partSerial['PSID']).update(trackingno=partSerial['TrackingNo'], shipdate=partSerial['ShipDate'],status=partSerial['Status'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
        PartSupport.SavePartSerialAudit(partSerial, CurrentUserID)
        SimpleLogger.do_log(f"PartSerial saved: {partSerial}", "debug")
        # Job for RA submit
        if partSerial['JobDetailID']!=0:
            wsResult = NSPWSClient.ExecuteJobDetail(token, JobType.CORE_SHIP.value, partSerial['JobDetailID'])
            try:
                wsreserror = get_xml_node(wsResult.text, "ERROR")
                if wsreserror:
                    return HttpResponseServerError(wsreserror)
            except:
                pass
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)     
        return JsonResponse(partSerial, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class RDCWarehousesController(View):
    "to get list of warehouses based on ID"
    def get(self, request):
        "accept warehouse ID in GET to process"
        # GET servicequick/api/RDCWarehouses?id=
        id = request.GET.get('id')
        SimpleLogger.do_log(f">>> Get()... {id}", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Logging and checking passed parameters
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'id':id}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(id), "GET", "RDCWarehousesController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)     
        # Validating warehouse ID
        id = id.upper()
        wh = WareHouseSupport.GetWarehouse(id) 
        if wh is None: #if None
            try:
                x = int(id)
            except:
                x = 0
            nspUser = NSPSupport.GetNSPUserByUserID(x)
            if nspUser is not None:    
                wh = WareHouseSupport.GetWarehouse(nspUser.get('WarehouseID'))

        if wh is None: #if it is still None
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"Warehouse not found: {id}")            
            return JsonResponse({'message':f"Warehouse not found: {id}"}, safe=False, status=404)

        resultList = []     
        if wh['WarehouseType']!=WarehouseType.RDC_WAREHOUSE.value:
            resultList.append(wh)
        else:
            resultList = WareHouseSupport.GetRDCWarehouse(wh['WarehouseID'])
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)    
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class RAUploadPictureController(View):
    "upload picture for the partSerial"
    def post(self, request):
        "accept parameters in multipart/form-data to process" 
        # POST servicequick/api/rauploadpicture
        SimpleLogger.do_log(">>> PostFormData()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Validating
        refId = request.POST.get("RefID")
        SimpleLogger.do_log(f"refId={refId}", "debug")

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'refId':refId}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(refId), "GET", "RAUploadPictureController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        if not refId:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Paramenter not found: refId')            
            return JsonResponse({'message':'Paramenter not found: refId'}, safe=False, status=400)
        #Checking partSerial
        responseResult = {}
        partSerial = None
        psId = 0
        try:
            psId = int(refId)
            isNumber = True
        except:
            isNumber = False
        if isNumber is True:
            partSerial = PartSupport.GetPartSerial(psId)
        if partSerial is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"PartSerial was not found by {refId}.")            
            return JsonResponse({'message':f"PartSerial was not found by {refId}."}, safe=False, status=400)
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
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f"Invalid or unsupported image type: {fileName}")            
                return JsonResponse({'message':f"Invalid or unsupported image type: {fileName}"}, safe=False, status=400)
            picture = PartSupport.SavePartSerialPicture(request, partSerial, fileName)
            if type(picture) is not dict:
                BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='500', errMsg=picture)            
                return JsonResponse({'message':picture}, safe=False, status=500)
            else:    
                responseResult.append(picture['picture'])
            SimpleLogger.do_log(f"Picture uploaded: {picture}", "debug")
            # Send file to GSPN
            if settings.DEBUG is False:
                xmlData = GspnWebServiceClient.SetPartReturnFileUpload(psId, partSerial['AccountNo'], partSerial['RANo'],picture['PictureID']+"."+picture['Ext'])
                SimpleLogger.do_log(f"xmlData.Length={len(xmlData)}", "debug")
                # Checking value for retCode in the xmlData received
                retCode = get_xml_node(xmlData, "RetCode")
                SimpleLogger.do_log(f"retCode= {retCode}")
                if retCode and retCode=='0':
                    pass #indicates success
                else:
                    ErrMsg = get_xml_node(xmlData, "ErrMsg")
                    #return HttpResponseServerError(ErrMsg)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)            
        return JsonResponse(responseResult, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)     

             



              




         




