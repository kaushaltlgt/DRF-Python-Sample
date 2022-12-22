import datetime, json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from nsp_user.authentication import KWAuthentication
from functions.querymethods import SingleCursor
from functions.xmlfunctions import get_xml_node
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from functions.kwlogging import SimpleLogger, AdvancedLogger, BaseApiController
from picking_tasks.models import NspPickingBatches
from picking_tasks.support import PickingSupport
from schedules_list_map.schedules import ReserveStatus, DOStatus, DODetailStatus
from schedules_list_map.support import NSPWSClient
from schedules_detail.schedules2 import SchedulesService
from nsp_user.support import DjangoOverRideJSONEncoder
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class PickingBatchesController(View):
    "method to list picking batch"
    def get(self, request):
        "accept GET request to process"
        #GET /servicequick/api/pickingbatches?date=2022-01-06&warehouseId=W0001
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Logging and checking passed parameters
        warehouseId = request.GET.get('warehouseId')
        date = request.GET.get('date')
        SimpleLogger.do_log(f"warehouseId= {warehouseId}") 
        SimpleLogger.do_log(f"date= {date}") 
        reqData = f"warehouseId : {warehouseId}, date : {date}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, "", "GET", "PickingBatchesController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
       
        #Preparing for the dataList from the table NSPPICKINGBATCHES
        if warehouseId and date:
            dataList = NspPickingBatches.objects.filter(warehouseid=warehouseId, createdon__gt=datetime.datetime.strptime(date, "%Y-%m-%d"), createdon__lt=datetime.datetime.strptime(date, "%Y-%m-%d")+datetime.timedelta(days=1)).order_by('createdon')
        elif warehouseId and not date:
            dataList = NspPickingBatches.objects.filter(warehouseid=warehouseId).order_by('createdon') 
        elif date and not warehouseId: 
            dataList = NspPickingBatches.objects.filter(createdon__gt=date, createdon__lt=datetime.date(date)+datetime.timedelta(days=1)).order_by('createdon')
        else:
            dataList = NspPickingBatches.objects.filter(warehouseid=warehouseId).order_by('createdon')
        GetDataList = []
        for x in dataList:
            xd = {}
            xd['BatchID'] = x.batchid
            xd['WarehouseID'] = x.warehouseid
            xd['BatchDTime'] = x.createdon
            xd['TicketCount'] = x.ticketcount
            xd['PartCount'] = x.partcount
            xd['CreatedOn'] = x.createdon
            xd['CreatedBy'] = x.createdby
            xd['UpdatedOn'] = x.updatedon
            xd['UpdatedBy'] = x.updatedby
            if x.createdby is not None:
                xd['LogBy'] = x.createdby
            else:
                xd['LogBy'] = x.updatedby    
            xd['LogByName'] = None
            GetDataList.append(xd)
        #Preparing for other data
        PickingBatchList = {}
        PickingBatchList['WarehouseID'] = warehouseId
        PickingBatchList['Date'] = date
        #Getting QueueTicketCount from SQL query
        ticketcount_query = f"SELECT CAST(COUNT(DISTINCT b.PID) AS NUMBER(9)) FROM NSPPartDetails a, OpBase b, OpWorkOrder c , NSPWarehouses WH WHERE a.OpWorkOrderID=b.ID AND b.ID=c.ID AND b.Status < 60 AND c.PartWarehouseID = WH.WarehouseID AND a.ReserveStatus={ReserveStatus.RESERVED.value} AND (WH.WarehouseID='{warehouseId}' OR WH.RDCWarehouseID = '{warehouseId}')" 
        res = SingleCursor.send_query(ticketcount_query)
        if type(res) is str:
            QueueTicketCount = 0
        else:
            QueueTicketCount = res['CAST(COUNT(DISTINCTB.PID)ASNUMBER(9))']
        #Getting QueuePartCount from SQL query
        partcount_query = f"SELECT CAST(COUNT(a.PartDetailID) AS NUMBER(9)) FROM NSPPartDetails a, OpBase b, OpWorkOrder c, NSPWarehouses WH WHERE a.OpWorkOrderID=b.ID AND b.ID=c.ID AND b.Status < 60 AND c.PartWarehouseID = WH.WarehouseID AND a.ReserveStatus={ReserveStatus.RESERVED.value} AND (WH.WarehouseID='{warehouseId}' OR WH.RDCWarehouseID = '{warehouseId}')"
        res = SingleCursor.send_query(partcount_query)
        if type(res) is str:
            QueuePartCount = 0
        else:
            QueuePartCount = res['CAST(COUNT(A.PARTDETAILID)ASNUMBER(9))']
        #Finalizing the data and accumulating all the values in the dictionary PickingBatchList
        PickingBatchList['QueueTicketCount'] = QueueTicketCount
        PickingBatchList['QueuePartCount'] = QueuePartCount
        PickingBatchList['ListSize'] = dataList.count()
        PickingBatchList['List'] = GetDataList
        PickingBatchList['LogID'] = warehouseId
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString) 
        return JsonResponse(PickingBatchList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
    def post(self, request):
        "accept parameters in POST to process"
        #API : /servicequick/api/pickingbatches
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
        WarehouseID = received_json_data.get('WarehouseID')
        SimpleLogger.do_log(f">>> reqData= {received_json_data}")
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':received_json_data}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(WarehouseID), "POST", "PickingBatchesController", jsonString, callerApp, AppVersion)
        if authstat is not True:
            return JsonResponse(authstat, status=401)
            
        token = request.META.get('HTTP_KW_TOKEN')
        wsResult = NSPWSClient.CreatePickingBatch(token, WarehouseID)
        try:
            wsreserror = get_xml_node(wsResult.text, "ERROR")
            if wsreserror:
                return HttpResponseServerError(wsreserror)
        except:
            pass

        try:
            batchId = get_xml_node(wsResult.text, "BatchID")
            SimpleLogger.do_log(f"batchId= {batchId}")
        except:
            batchId = 0

        pickingBatch = PickingSupport.GetPickingBatch(batchId) 
        if pickingBatch is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='No picking batch has been created.')
            return JsonResponse({'message':'No picking batch has been created.'}, safe=False, status=400)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)    
        return JsonResponse(pickingBatch, safe=False, status=200)       


class PickingLabelsController(View):
    "to get information regarding picking labels"
    def get(self, request, id):
        "accept picking ID to process"
        # Get servicequick/api/pickinglabels/1234  
        SimpleLogger.do_log(f">>> Get()...{id}", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Logging and checking passed parameters
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'id':id}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(id), "GET", "PickingLabelsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
       
        #Processing the data
        pickingBatch = PickingSupport.GetPickingBatch(id)
        SimpleLogger.do_log(f">>> pickingBatch={pickingBatch}")
        if pickingBatch is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"Picking batch not found: {id}")            
            return JsonResponse({'message':f"Picking batch not found: {id}"}, safe=False, status=404)
        # Ticket Summary 
        ticketSummaryList = PickingSupport.GetPickingBatchTicketSummaryList(pickingBatch['BatchID'])
        # Label Data
        labelList = PickingSupport.GetPickingLabelListByDOOrder(pickingBatch['BatchID']) 
        # Summary Data 
        summary = {}
        summary['BatchID'] = pickingBatch['BatchID']
        summary['Tickets'] = pickingBatch['TicketCount']
        summary['Parts'] = pickingBatch['PartCount']
        summary['Date'] = datetime.date.today().strftime("%m/%d/%Y")
        summary['Time'] = datetime.datetime.now().strftime("%H:%M")
        # Response Data
        respData = {}
        respData['Summary'] = summary
        respData['TicketSummary'] = ticketSummaryList
        respData['Data'] = labelList
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString) 
        return JsonResponse(respData, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)


class ReceivingLabelsController(View):
    "get data for ReceivingLabels based on ID"
    def get(self, request, id):
        "accept ID in GET request to process"
        # Get servicequick/api/receivinglabels/435864
        SimpleLogger.do_log(f">>> Get()...{id}", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        #Logging
        token = request.META.get('HTTP_KW_TOKEN')

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'id':id}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(id), "GET", "ReceivingLabelsController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        #Getting data from the table NSPDOS 
        nspDo = None
        try:
            entityId = int(id)
        except:
            entityId = 0
        SQLService = SchedulesService
        nspDo = SQLService.GetDOByID(entityId)
        if nspDo is None:
            nspDo = SQLService.GetDOByNo(id)
        SimpleLogger.do_log(f">>> nspDo={nspDo}", "debug")
        #Getting data for DODetails
        itemNo = 0
        dd = None
        if nspDo is None:
            doNo = id[0:min(10, len(id))]
            nspDo = SQLService.GetDOByNo(doNo)
            if nspDo is not None:
                integer_try_parse = False
                if len(id) > 10:
                    try:
                        integer_try_parse = bool(int(id[10:len(id)-10]))
                    except:
                        pass
                    if integer_try_parse is True:
                        itemNo = int(id[10:len(id)-10])
                        dd = SQLService.GetDODetailByDONoAndItemNo(doNo, itemNo)
        if nspDo is None:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='404', errMsg=f"DO not found: {id}")            
            return JsonResponse({'message':f"DO not found: {id}"}, safe=False, status=404)
        #Preparing for the response data
        respData = {}
        if dd is not None:
            if nspDo['Status'] < DOStatus.CLOSED.value and nspDo['Status'] < DODetailStatus.CLOSED.value:
                wsResult = NSPWSClient.CreatePartSerial4DODetail(token, nspDo['DOID'], dd['ItemNo'])
                try:
                    wsreserror = get_xml_node(wsResult.text, "ERROR")
                    if wsreserror:
                        return HttpResponseServerError(wsreserror)
                except:
                    pass
            # getting Label Data
            labelList =  PickingSupport.GetReceivingLabelList(nspDo['DONo'], dd['ItemNo'])
            totalLabelCount = len(labelList)
            for label in labelList:
                if label['ToLocationCode']:
                    totalLabelCount += 1
            # Summary Data
            summary = {}
            summary['DONo'] = id
            summary['AccountNo'] = nspDo['AccountNo']
            summary['TrackingNo'] = nspDo['TrackingNo']
            summary['Lines'] = 1
            summary['Parts'] = len(labelList)
            summary['Labels'] = totalLabelCount
            summary['Date'] = datetime.date.today().strftime("%m/%d/%Y")
            summary['Time'] = datetime.datetime.now().strftime("%H:%M")

            respData['Summary'] = summary
            respData['Data'] = labelList
        else:
            if nspDo['Status'] < DOStatus.CLOSED.value:
                wsResult = NSPWSClient.CreatePartSerial4DeliveryOrder(token, nspDo['DOID'])
                try:
                    wsreserror = get_xml_node(wsResult.text, "ERROR")
                    if wsreserror:
                        return HttpResponseServerError(wsreserror)
                except:
                    pass
            # CompleteDOReceiving
            wsResult = NSPWSClient.CompleteDOReceiving(token, nspDo['DOID'])
            try:
                wsreserror = get_xml_node(wsResult.text, "ERROR")
                if wsreserror:
                    return HttpResponseServerError(wsreserror)
            except:
                pass

            # Label Data
            labelList =  PickingSupport.GetReceivingLabelList(nspDo['DONo'])
            totalLabelCount = len(labelList)
            for label in labelList:
                if label['ToLocationCode']:
                    totalLabelCount += 1

            # Summary Data
            summary = {}
            summary['DONo'] = nspDo['DONo']
            summary['AccountNo'] = nspDo['AccountNo']
            summary['TrackingNo'] = nspDo['TrackingNo']
            summary['Lines'] = len(nspDo['DODetails'])
            summary['Parts'] = len(labelList)
            summary['Labels'] = totalLabelCount
            summary['Date'] = datetime.date.today().strftime("%m/%d/%Y")
            summary['Time'] = datetime.datetime.now().strftime("%H:%M")

            respData['Summary'] = summary
            respData['Data'] = labelList
        #Returning the Response Data
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString) 
        return JsonResponse(respData, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)                                              

                   



