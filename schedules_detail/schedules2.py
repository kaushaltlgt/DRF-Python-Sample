#extra functions for this app
import datetime, os, requests, json, base64
from itertools import chain
from django.conf import settings
from django.db.models import Q
from functions.querymethods import MultipleCursor, SingleCursor
from nsp_user.authentication import KWAuthentication
from nsp_user.models import getuserinfo, getboolvalue
from functions.querymethods import DBIDGENERATOR, MultipleCursor
from functions.kwlogging import SimpleLogger
from django.core.files.storage import FileSystemStorage
from schedules_list_map.models import Pictures, OpBase, OpWorkOrder, OpTicket
from schedules_detail.soap_actions import XMLActions
from schedules_detail.models import DocFolders, DocNodes, DocFiles, NspDos, NspPartDetails, NspCompanyContacts, NspAddresses, NspDoDetails, NspPartMasters, NspDocs
from functions.xmlfunctions import get_xml_node
from schedules_list_map.schedules import DocSystemID, DocNodeType, DocNodeStatus, DocIDType, WorkOrderStatus, DOStatus, WorkOrderAdditionalInfoVO, GspnWebServiceClient, PaymentTypeEnum, WarrantyStatus
from functions.smtpgateway import sendmailoversmtp
from django.utils import timezone


class SchedulesService:
    "define functions to be derived using SQL and dates"
    def __init__(self) -> None:
        pass

    def GetSchedulableDate(wh, SQZone, IncludeWeekend):
        "get schedule date using warehouse ID and other parameters"
        WarehouseID = wh.warehouseid
        START_RURAL_AREA = "M"
        LIMIT_HOUR_FOR_NEXTDAY = 15
        LAST_SCHEDULABLE_DATE_FROM_TODAY = 42
        GAP_TO_NEXT_BUSINESS_DAY = 0
        nowtime = datetime.datetime.now()
        today = nowtime.today()
        timespan = datetime.timedelta(hours=0, minutes=0, seconds=0)
        bRural = False

        if SQZone:
            x = len(SQZone.upper()[0:1])
            y = len(START_RURAL_AREA)
            if x==y:
                compare_value = 0
            elif y > x:
                compare_value = 1
            else:
                compare_value = -1
             
        if SQZone and compare_value >= 0:
            bRural = True

        if wh.timezone=='MST':
            timespan = datetime.timedelta(hours=1, minutes=0, seconds=0)
        elif wh.timezone=='CST':
            timespan = datetime.timedelta(hours=2, minutes=0, seconds=0)
        elif wh.timezone=='EST':
            timespan = datetime.timedelta(hours=3, minutes=0, seconds=0)
        else:
            pass
        nowtime = nowtime + timespan
        if today.hour >= LIMIT_HOUR_FOR_NEXTDAY:
            limit_hour = 2
        else:
            limit_hour = 1
        if wh.parttat:        
            GAP_TO_NEXT_BUSINESS_DAY = max(wh.parttat, 1)
        else:
            GAP_TO_NEXT_BUSINESS_DAY = 1    
        GAP_TO_NEXT_BUSINESS_DAY += limit_hour

        i = 0
        while i < GAP_TO_NEXT_BUSINESS_DAY:
            i = i + 1
            nowtime = nowtime + datetime.timedelta(hours=1, minutes=0, seconds=0) 
            while nowtime.weekday()==5 or nowtime.weekday()==6: #5 is Saturday and 6 is Sunday
                nowtime = nowtime + datetime.timedelta(hours=1, minutes=0, seconds=0)

        fromDate = f"TO_DATE('{nowtime.date().strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        if SQZone:
            query_exec = f"SELECT Slot.Day FROM (SELECT TRUNC(FromDTime) AS Day, SUM(Slot) AS TotalSlot , SUM(DECODE(Zone, '{SQZone}', Slot, 0)) AS ZoneSlot FROM NSPTimeSlots WHERE WarehouseID = '{WarehouseID}' AND FromDTime >= TRUNC(CURRENT_DATE) + 1 AND FromDTime >= {fromDate} AND FromDTime < TRUNC(CURRENT_DATE) + {LAST_SCHEDULABLE_DATE_FROM_TODAY + 1} GROUP BY TRUNC(FromDTime) ) Slot LEFT OUTER JOIN (SELECT /*+ ORDERED USE_NL(WB TB T C A Z) */  TRUNC(W.AptStartDTime) AS Day, SUM(DECODE(W.SealLevel, 2, 2, 1)) AS TotalSO , SUM(DECODE(Z.Zone, '{SQZone}', DECODE(W.SealLevel, 2, 2, 1), 0)) AS ZoneSO FROM OpWorkOrder W INNER JOIN OpBase WB ON W.ID = WB.ID INNER JOIN OpBase TB ON WB.PID = TB.ID INNER JOIN OpTicket T ON TB.ID = T.ID INNER JOIN NSPCompanyContacts C ON T.ContactID = C.ContactID INNER JOIN NSPAddresses A ON C.AddressID = A.AddressID INNER JOIN NSPZones Z ON T.WarehouseID = Z.WarehouseID AND T.ProductCategory = Z.ProductCategory  AND A.Zipcode = Z.ZipCode WHERE TB.Status <= 60 AND WB.Status >= 5 AND WB.Status <= 60 AND T.WarehouseID = '{WarehouseID}' AND W.AptStartDTime >= TRUNC(CURRENT_DATE) + 1 AND W.AptStartDTime >= {fromDate} AND W.AptStartDTime < TRUNC(CURRENT_DATE) + {LAST_SCHEDULABLE_DATE_FROM_TODAY + 1} GROUP BY TRUNC(W.AptStartDTime) ) SO ON Slot.Day = SO.Day WHERE Slot.TotalSlot > NVL(SO.TotalSO, 0) AND Slot.ZoneSlot IS NOT NULL AND Slot.ZoneSlot > 0 ORDER BY Slot.Day ASC" 
        if bRural is True:
            print('I am true...', SQZone)
            query_exec = f"SELECT Slot.Day FROM (SELECT TRUNC(FromDTime) AS Day, SUM(Slot) AS TotalSlot , SUM(DECODE(Zone, '{SQZone}', Slot, 0)) AS ZoneSlot FROM NSPTimeSlots WHERE WarehouseID = '{WarehouseID}' AND FromDTime >= TRUNC(CURRENT_DATE) + 1 AND FromDTime >= {fromDate} AND FromDTime < TRUNC(CURRENT_DATE) + {LAST_SCHEDULABLE_DATE_FROM_TODAY + 1} GROUP BY TRUNC(FromDTime) ) Slot LEFT OUTER JOIN (SELECT /*+ ORDERED USE_NL(WB TB T C A Z) */  TRUNC(W.AptStartDTime) AS Day, SUM(DECODE(W.SealLevel, 2, 2, 1)) AS TotalSO , SUM(DECODE(Z.Zone, '{SQZone}', DECODE(W.SealLevel, 2, 2, 1), 0)) AS ZoneSO FROM OpWorkOrder W INNER JOIN OpBase WB ON W.ID = WB.ID INNER JOIN OpBase TB ON WB.PID = TB.ID INNER JOIN OpTicket T ON TB.ID = T.ID INNER JOIN NSPCompanyContacts C ON T.ContactID = C.ContactID INNER JOIN NSPAddresses A ON C.AddressID = A.AddressID INNER JOIN NSPZones Z ON T.WarehouseID = Z.WarehouseID AND T.ProductCategory = Z.ProductCategory  AND A.Zipcode = Z.ZipCode WHERE TB.Status <= 60 AND WB.Status >= 5 AND WB.Status <= 60 AND T.WarehouseID = '{WarehouseID}' AND W.AptStartDTime >= TRUNC(CURRENT_DATE) + 1 AND W.AptStartDTime >= {fromDate} AND W.AptStartDTime < TRUNC(CURRENT_DATE) + {LAST_SCHEDULABLE_DATE_FROM_TODAY + 1} GROUP BY TRUNC(W.AptStartDTime) ) SO ON Slot.Day = SO.Day WHERE Slot.TotalSlot > NVL(SO.TotalSO, 0) AND Slot.ZoneSlot IS NOT NULL AND Slot.ZoneSlot > 0 AND Slot.ZoneSlot > NVL(SO.ZoneSO, 0) ORDER BY Slot.Day ASC"
        if IncludeWeekend is False:
            query_exec = f"SELECT Slot.Day FROM (SELECT TRUNC(FromDTime) AS Day, SUM(Slot) AS TotalSlot , SUM(DECODE(Zone, '{SQZone}', Slot, 0)) AS ZoneSlot FROM NSPTimeSlots WHERE WarehouseID = '{WarehouseID}' AND FromDTime >= TRUNC(CURRENT_DATE) + 1 AND FromDTime >= {fromDate} AND FromDTime < TRUNC(CURRENT_DATE) + {LAST_SCHEDULABLE_DATE_FROM_TODAY + 1} GROUP BY TRUNC(FromDTime) ) Slot LEFT OUTER JOIN (SELECT /*+ ORDERED USE_NL(WB TB T C A Z) */  TRUNC(W.AptStartDTime) AS Day, SUM(DECODE(W.SealLevel, 2, 2, 1)) AS TotalSO , SUM(DECODE(Z.Zone, '{SQZone}', DECODE(W.SealLevel, 2, 2, 1), 0)) AS ZoneSO FROM OpWorkOrder W INNER JOIN OpBase WB ON W.ID = WB.ID INNER JOIN OpBase TB ON WB.PID = TB.ID INNER JOIN OpTicket T ON TB.ID = T.ID INNER JOIN NSPCompanyContacts C ON T.ContactID = C.ContactID INNER JOIN NSPAddresses A ON C.AddressID = A.AddressID INNER JOIN NSPZones Z ON T.WarehouseID = Z.WarehouseID AND T.ProductCategory = Z.ProductCategory  AND A.Zipcode = Z.ZipCode WHERE TB.Status <= 60 AND WB.Status >= 5 AND WB.Status <= 60 AND T.WarehouseID = '{WarehouseID}' AND W.AptStartDTime >= TRUNC(CURRENT_DATE) + 1 AND W.AptStartDTime >= {fromDate} AND W.AptStartDTime < TRUNC(CURRENT_DATE) + {LAST_SCHEDULABLE_DATE_FROM_TODAY + 1} GROUP BY TRUNC(W.AptStartDTime) ) SO ON Slot.Day = SO.Day WHERE Slot.TotalSlot > NVL(SO.TotalSO, 0) AND Slot.ZoneSlot IS NOT NULL AND Slot.ZoneSlot > 0 AND Slot.ZoneSlot > NVL(SO.ZoneSO, 0) AND TO_CHAR(Slot.Day, 'd') NOT IN (7, 1) ORDER BY Slot.Day ASC"

        res = MultipleCursor.send_query(query_exec)
        datesList = []
        if type(res) is not str and len(res) > 0:
            for x in res:
                datesList.append(x['DAY'])
        return datesList
            

    def GetScheduledSQBoxes(warehouseId, apptDate, pageNo, pageSize):
        "to run a SQL query to get SQBoxes warehouse data"
        apptDate = f"TO_DATE('{apptDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        run_query = f"SELECT * FROM OpBase B, OpWorkOrder W, NspWareHouses WH WHERE B.ID = W.ID AND W.PartWarehouseID = WH.WarehouseID AND (WH.WarehouseID = '{warehouseId}' OR WH.RDCWarehouseID = '{warehouseId}') AND W.AptStartDTime >= {apptDate} AND W.AptStartDTime < {apptDate} + 1 AND B.Status < 60 ORDER BY WH.WarehouseID ASC, TO_NUMBER(SUBSTR(W.SQBox, 6, 10)) ASC"
        try:
            res = MultipleCursor.send_query(run_query, 50)
            if type(res) is str:
                print(res)
                return []
        except Exception as e:
            print(e)
            res = []
        return res

    def GetWorkOrderBySQBox(warehouseId, sqBox):
        "to run a SQL query to fetch data from the tables OPBASE and OPWORKORDER"
        run_query = f"select * from OPBASE B, OPWORKORDER W where B.ID = W.ID AND W.partwarehouseid = '{warehouseId}' AND W.sqbox = '{sqBox}' AND B.STATUS <= {WorkOrderStatus.CLOSED.value} ORDER BY W.ID DESC" 
        res = SingleCursor.send_query(run_query)
        if type(res) is str: #this means there is some SQL error
            print(res)
            return None
        else:
            return res    

    def GetWorkOrder(workorderid, CurrentUserID=None):
        "to get workorder with status based on ID value"
        run_query = f"select * from OPBASE B, OPWORKORDER W where B.ID = W.ID AND W.ID = {workorderid};"
        res = SingleCursor.send_query(run_query)
        if type(res) is str: #this means there is some SQL error
            print(res)
            return None
        else:
            wores = {}
            x = res
            try:
                b = OpBase.objects.filter(id=x['ID']).first()
                wores['WarrantyStatus'] = x['WARRANTYSTATUS']
                wores['RepairResultCode'] = x['REPAIRRESULTCODE']
                wores['PaymentType'] = x['PAYMENTTYPE']
                wores['RepairFailCode'] = x['REPAIRFAILCODE']
                pd = NspPartDetails.objects.filter(opworkorderid=x['ID']).order_by('partdetailid')
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
                wores['WorkOrderNo'] = x['WORKORDERNO']
                wores['AptStartDTime'] = x['APTSTARTDTIME']
                wores['AptEndDTime'] = x['APTENDDTIME']
                wores['StartDTime'] = x['STARTDTIME']
                wores['FinishDTime'] = x['FINISHDTIME']
                ct = NspCompanyContacts.objects.filter(contactid=x['CONTACTID'])
                contacts = {}
                for c in ct:
                    contacts['ContactID'] = x['CONTACTID']
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
                wores['Technician'] = getuserinfo(x['TECHNICIANID'])
                wores['TechnicianNote'] = x['TECHNICIANNOTE']
                wores['TriageNote'] = x['TRIAGENOTE']
                wores['DefectCode'] = x['DEFECTCODE']
                wores['DefectCodeDescription'] = None
                wores['RepairCode'] = x['REPAIRCODE']
                wores['RepairCodeDescription'] = None
                wores['Odometer'] = x['ODOMETER']
                wores['Note'] = x['NOTE']
                wores['RepairAction'] = x['REPAIRACTION']
                wores['DefectSymptom'] = x['DEFECTSYMPTOM']
                try:
                    wores['PartCost'] = float(x['PARTCOST'])
                except:
                    wores['PartCost'] = 0.0 
                try:       
                    wores['LaborCost'] = float(x['LABORCOST'])
                except:
                    wores['LaborCost'] = 0.0 
                try:    
                    wores['OtherCost'] = float(x['OTHERCOST'])
                except:
                    wores['OtherCost'] = 0.0
                try:        
                    wores['SalesTax'] = float(x['SALESTAX'])
                except:
                    wores['SalesTax'] = 0.0
                wores['CheckList1'] = getboolvalue(x['CHECKLIST1'])
                wores['CheckList2'] = getboolvalue(x['CHECKLIST2'])
                wores['CheckList3'] = getboolvalue(x['CHECKLIST3'])
                wores['CheckList4'] = getboolvalue(x['CHECKLIST4'])
                wores['IsPartInfoClear'] = getboolvalue(x['ISPARTINFOCLEAR'])
                wores['SignatureDocID'] = x['SIGNATUREDOCID']
                wores['SmallSignatureDocID'] = x['SMALLSIGNATUREDOCID']
                wores['SignedName'] = x['SIGNEDNAME']
                wores['FinalWorkOrderDocID'] = x['FINALWORKORDERDOCID']
                wores['DiagnosedBy'] = getuserinfo(x['DIAGNOSEDBY'])
                wores['IsCxDissatisfied'] = getboolvalue(x['ISCXDISSATISFIED'])
                wores['IsPartOrdered'] = getboolvalue(x['ISPARTORDERED'])
                wores['PartOrderBy'] = getuserinfo(x['PARTORDERBY'])
                wores['SOPrintDTime'] = x['SOPRINTDTIME']
                wores['AptMadeBy'] = getuserinfo(x['APTMADEBY'])
                wores['AptMadeDTime'] = x['APTMADEDTIME']
                wores['QuoteBy'] = getuserinfo(x['QUOTEBY'])
                wores['QuoteDTime'] = x['QUOTEDTIME']
                wores['PartOrderDTime'] = x['PARTORDERDTIME']
                wores['DiagnoseDTime'] = x['DIAGNOSEDTIME']
                wores['Triage'] = x['TRIAGE']
                wores['ExtraMan'] = x['EXTRAMAN']
                wores['SealLevel'] = x['SEALLEVEL']
                wores['Seq'] = x['SEQ']
                wores['PartWarehouseID'] = x['PARTWAREHOUSEID']
                wores['SQBox'] = x['SQBOX']
                wores['ITSJobID'] = x['ITSJOBID']
                wores['ReserveComplete'] = getboolvalue(x['RESERVECOMPLETE'])
                wores['ReverseITSJobID'] = x['REVERSEITSJOBID']
                wores['MsgToTech'] = x['MSGTOTECH']
                wores['MsgConfirmDTime'] = x['MSGCONFIRMDTIME']
                wores['PaymentTransactionID'] = x['PAYMENTTRANSACTIONID']
                wores['DefectCodeList'] = None
                wores['RepairCodeList'] = None
                ai = WorkOrderAdditionalInfoVO.get_info(x['ID'])
                wores['Redo'] = ai['REDO']
                wores['VisitCount'] = ai['VISITCOUNT']
                wores['LastTechnician'] = ai['LASTTECHNICIAN']
                wores['TicketNo'] = WorkOrderAdditionalInfoVO.GetTicket(x['ID'])
                wores['ID'] = x['ID']
                wores['OpDTime'] = b.opdtime
                wores['Status'] = b.status
                try:
                    t = OpTicket.objects.filter(id=b.pid)[0]
                    ticketres = {}
                    ticketres['ID'] = t.id
                    try:
                        ticketres['Status'] = OpBase.objects.get(pid=t.id).status
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
                        contacts['ContactID'] = t.contactid
                        nspadd = NspAddresses.objects.filter(addressid=c.addressid)
                        address = {}
                        for ad in nspadd:
                            address['Addr'] = ad.address
                            address['City'] = ad.city
                            address['State'] = ad.state
                            address['ZipCode'] = ad.zipcode
                            address['Country'] = ad.country
                        contacts['Address'] = address
                        contacts['Name'] = c.name
                        contacts['Tel'] = c.tel
                        contacts['Fax'] = c.fax
                        contacts['Email'] = c.email
                        contacts['Mobile'] = c.mobile
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
            except Exception as e:
                print(e)
            return wores 

    def GetWorkOrderByWorkOrderNo(workOrderNo, CurrentUserID):
        "to get workorder with status based on workOrderNo"
        run_query = f"select * from OPBASE B, OPWORKORDER W where B.ID = W.ID AND W.workorderno = '{workOrderNo}';"
        res = SingleCursor.send_query(run_query)
        if type(res) is str: #this means there is some SQL error
            print(res)
            return None
        else:
            wores = {}
            x = res
            try:
                b = OpBase.objects.get(id=x['ID'])
                wores['WarrantyStatus'] = x['WARRANTYSTATUS']
                wores['RepairResultCode'] = x['REPAIRRESULTCODE']
                wores['PaymentType'] = x['PAYMENTTYPE']
                wores['RepairFailCode'] = x['REPAIRFAILCODE']
                pd = NspPartDetails.objects.filter(opworkorderid=x['ID']).order_by('partdetailid')
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
                wores['WorkOrderNo'] = x['WORKORDERNO']
                wores['AptStartDTime'] = x['APTSTARTDTIME']
                wores['AptEndDTime'] = x['APTENDDTIME']
                wores['StartDTime'] = x['STARTDTIME']
                wores['FinishDTime'] = x['FINISHDTIME']
                ct = NspCompanyContacts.objects.filter(contactid=x['CONTACTID'])
                contacts = {}
                for c in ct:
                    contacts['ContactID'] = x['CONTACTID']
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
                wores['Technician'] = getuserinfo(x['TECHNICIANID'])
                wores['TechnicianNote'] = x['TECHNICIANNOTE']
                wores['TriageNote'] = x['TRIAGENOTE']
                wores['DefectCode'] = x['DEFECTCODE']
                wores['DefectCodeDescription'] = None
                wores['RepairCode'] = x['REPAIRCODE']
                wores['RepairCodeDescription'] = None
                wores['Odometer'] = x['ODOMETER']
                wores['Note'] = x['NOTE']
                wores['RepairAction'] = x['REPAIRACTION']
                wores['DefectSymptom'] = x['DEFECTSYMPTOM']
                try:
                    wores['PartCost'] = float(x['PARTCOST'])
                except:
                    wores['PartCost'] = 0.0 
                try:       
                    wores['LaborCost'] = float(x['LABORCOST'])
                except:
                    wores['LaborCost'] = 0.0 
                try:    
                    wores['OtherCost'] = float(x['OTHERCOST'])
                except:
                    wores['OtherCost'] = 0.0
                try:        
                    wores['SalesTax'] = float(x['SALESTAX'])
                except:
                    wores['SalesTax'] = 0.0
                wores['CheckList1'] = getboolvalue(x['CHECKLIST1'])
                wores['CheckList2'] = getboolvalue(x['CHECKLIST2'])
                wores['CheckList3'] = getboolvalue(x['CHECKLIST3'])
                wores['CheckList4'] = getboolvalue(x['CHECKLIST4'])
                wores['IsPartInfoClear'] = getboolvalue(x['ISPARTINFOCLEAR'])
                wores['SignatureDocID'] = x['SIGNATUREDOCID']
                wores['SmallSignatureDocID'] = x['SMALLSIGNATUREDOCID']
                wores['SignedName'] = x['SIGNEDNAME']
                wores['FinalWorkOrderDocID'] = x['FINALWORKORDERDOCID']
                wores['DiagnosedBy'] = getuserinfo(x['DIAGNOSEDBY'])
                wores['IsCxDissatisfied'] = getboolvalue(x['ISCXDISSATISFIED'])
                wores['IsPartOrdered'] = getboolvalue(x['ISPARTORDERED'])
                wores['PartOrderBy'] = getuserinfo(x['PARTORDERBY'])
                wores['SOPrintDTime'] = x['SOPRINTDTIME']
                wores['AptMadeBy'] = getuserinfo(x['APTMADEBY'])
                wores['AptMadeDTime'] = x['APTMADEDTIME']
                wores['QuoteBy'] = getuserinfo(x['QUOTEBY'])
                wores['QuoteDTime'] = x['QUOTEDTIME']
                wores['PartOrderDTime'] = x['PARTORDERDTIME']
                wores['DiagnoseDTime'] = x['DIAGNOSEDTIME']
                wores['Triage'] = x['TRIAGE']
                wores['ExtraMan'] = x['EXTRAMAN']
                wores['SealLevel'] = x['SEALLEVEL']
                wores['Seq'] = x['SEQ']
                wores['PartWarehouseID'] = x['PARTWAREHOUSEID']
                wores['SQBox'] = x['SQBOX']
                wores['ITSJobID'] = x['ITSJOBID']
                wores['ReserveComplete'] = getboolvalue(x['RESERVECOMPLETE'])
                wores['ReverseITSJobID'] = x['REVERSEITSJOBID']
                wores['MsgToTech'] = x['MSGTOTECH']
                wores['MsgConfirmDTime'] = x['MSGCONFIRMDTIME']
                wores['PaymentTransactionID'] = x['PAYMENTTRANSACTIONID']
                wores['DefectCodeList'] = None
                wores['RepairCodeList'] = None
                ai = WorkOrderAdditionalInfoVO.get_info(x['ID'])
                wores['Redo'] = ai['REDO']
                wores['VisitCount'] = ai['VISITCOUNT']
                wores['LastTechnician'] = ai['LASTTECHNICIAN']
                wores['TicketNo'] = WorkOrderAdditionalInfoVO.GetTicket(x['ID'])
                wores['ID'] = x['ID']
                wores['OpDTime'] = b.opdtime
                wores['Status'] = b.status
                try:
                    t = OpTicket.objects.filter(id=b.pid)[0]
                    ticketres = {}
                    ticketres['ID'] = t.id
                    try:
                        ticketres['Status'] = OpBase.objects.filter(pid=t.id)[0].status
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
                        contacts['ContactID'] = t.contactid
                        nspadd = NspAddresses.objects.filter(addressid=c.addressid)
                        address = {}
                        for ad in nspadd:
                            address['Addr'] = ad.address
                            address['City'] = ad.city
                            address['State'] = ad.state
                            address['ZipCode'] = ad.zipcode
                            address['Country'] = ad.country
                        contacts['Address'] = address
                        contacts['Name'] = c.name
                        contacts['Tel'] = c.tel
                        contacts['Fax'] = c.fax
                        contacts['Email'] = c.email
                        contacts['Mobile'] = c.mobile
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
            except Exception as e:
                print(e)
            return wores

    def GetWorkOrderHistory(WorkOrderID, CurrentUserID, token):
        "to get workorder history by running a SQL query based on input workorder value"
        workorder_query = f"SELECT * FROM OpWorkOrder W, Opticket T, OpBase B WHERE T.ID = B.PID AND W.ID = B.ID AND ((T.SerialNo = 'M000') OR (T.SerialNo <> 'M000')) AND B.Status = 60 AND W.ID = {int(WorkOrderID)} AND NVL(W.StartDTime, W.AptStartDTime) < NVL(W.StartDTime, W.AptStartDTime) ORDER BY NVL(W.StartDTime, W.AptStartDTime) ASC;"
        result = MultipleCursor.send_query(workorder_query)
        if type(result) is str: #incase there is error
            return []
        wores = {}    
        for x in result:
            try:
                b = OpBase.objects.get(id=x['ID'])
                wores['WarrantyStatus'] = x['WARRANTYSTATUS']
                wores['RepairResultCode'] = x['REPAIRRESULTCODE']
                wores['PaymentType'] = x['PAYMENTTYPE']
                wores['RepairFailCode'] = x['REPAIRFAILCODE']
                pd = NspPartDetails.objects.filter(opworkorderid=x['ID'])
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
                wores['WorkOrderNo'] = x['WORKORDERNO']
                wores['AptStartDTime'] = x['APTSTARTDTIME']
                wores['AptEndDTime'] = x['APTENDDTIME']
                wores['StartDTime'] = x['STARTDTIME']
                wores['FinishDTime'] = x['FINISHDTIME']
                ct = NspCompanyContacts.objects.filter(contactid=x['CONTACTID'])
                contacts = {}
                for c in ct:
                    contacts['ContactID'] = x['CONTACTID']
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
                wores['Technician'] = getuserinfo(x['TECHNICIANID'])
                wores['TechnicianNote'] = x['TECHNICIANNOTE']
                wores['TriageNote'] = x['TRIAGENOTE']
                wores['DefectCode'] = x['DEFECTCODE']
                wores['DefectCodeDescription'] = WorkOrderAdditionalInfoVO.DefectCodeDescription(x['DEFECTCODE']) #needs to be analysed
                wores['RepairCode'] = x['REPAIRCODE']
                wores['RepairCodeDescription'] = WorkOrderAdditionalInfoVO.RepairCodeDescription(x['REPAIRCODE']) #further analysis needed
                wores['Odometer'] = x['ODOMETER']
                wores['Note'] = x['NOTE']
                wores['RepairAction'] = x['REPAIRACTION']
                wores['DefectSymptom'] = x['DEFECTSYMPTOM']
                try:
                    wores['PartCost'] = float(x['PARTCOST'])
                except:
                    wores['PartCost'] = 0.0 
                try:       
                    wores['LaborCost'] = float(x['LABORCOST'])
                except:
                    wores['LaborCost'] = 0.0 
                try:    
                    wores['OtherCost'] = float(x['OTHERCOST'])
                except:
                    wores['OtherCost'] = 0.0
                try:        
                    wores['SalesTax'] = float(x['SALESTAX'])
                except:
                    wores['SalesTax'] = 0.0
                wores['CheckList1'] = getboolvalue(x['CHECKLIST1'])
                wores['CheckList2'] = getboolvalue(x['CHECKLIST2'])
                wores['CheckList3'] = getboolvalue(x['CHECKLIST3'])
                wores['CheckList4'] = getboolvalue(x['CHECKLIST4'])
                wores['IsPartInfoClear'] = getboolvalue(x['ISPARTINFOCLEAR'])
                wores['SignatureDocID'] = x['SIGNATUREDOCID']
                wores['SmallSignatureDocID'] = x['SMALLSIGNATUREDOCID']
                wores['SignedName'] = x['SIGNEDNAME']
                wores['FinalWorkOrderDocID'] = x['FINALWORKORDERDOCID']
                wores['DiagnosedBy'] = getuserinfo(x['DIAGNOSEDBY'])
                wores['IsCxDissatisfied'] = getboolvalue(x['ISCXDISSATISFIED'])
                wores['IsPartOrdered'] = getboolvalue(x['ISPARTORDERED'])
                wores['PartOrderBy'] = getuserinfo(x['PARTORDERBY'])
                wores['SOPrintDTime'] = x['SOPRINTDTIME']
                wores['AptMadeBy'] = getuserinfo(x['APTMADEBY'])
                wores['AptMadeDTime'] = x['APTMADEDTIME']
                wores['QuoteBy'] = getuserinfo(x['QUOTEBY'])
                wores['QuoteDTime'] = x['QUOTEDTIME']
                wores['PartOrderDTime'] = x['PARTORDERDTIME']
                wores['DiagnoseDTime'] = x['DIAGNOSEDTIME']
                wores['Triage'] = x['TRIAGE']
                wores['ExtraMan'] = x['EXTRAMAN']
                wores['SealLevel'] = x['SEALLEVEL']
                wores['Seq'] = x['SEQ']
                wores['PartWarehouseID'] = x['PARTWAREHOUSEID']
                wores['SQBox'] = x['SQBOX']
                wores['ITSJobID'] = x['ITSJOBID']
                wores['ReserveComplete'] = getboolvalue(x['RESERVECOMPLETE'])
                wores['ReverseITSJobID'] = x['REVERSEITSJOBID']
                wores['MsgToTech'] = x['MSGTOTECH']
                wores['MsgConfirmDTime'] = x['MSGCONFIRMDTIME']
                wores['PaymentTransactionID'] = x['PAYMENTTRANSACTIONID']
                try:
                    b = OpBase.objects.get(id=x['ID'])
                    model_no = OpTicket.objects.get(id=b.pid).modelno
                    system_id = OpTicket.objects.get(id=b.pid).systemid
                    wores['DefectCodeList'] = WorkOrderAdditionalInfoVO.GetDefectCodeList(model_no, system_id, CurrentUserID, token)
                except:
                    wores['DefectCodeList'] = None 
                try:
                    b = OpBase.objects.get(id=x['ID'])
                    model_no = OpTicket.objects.get(id=b.pid).modelno
                    system_id = OpTicket.objects.get(id=b.pid).systemid
                    wores['RepairCodeList'] = WorkOrderAdditionalInfoVO.GetRepairCodeList(model_no, system_id, CurrentUserID, token)
                except:
                    wores['RepairCodeList'] = None
                ai = WorkOrderAdditionalInfoVO.get_info(x['ID'])
                wores['Redo'] = ai['REDO']
                wores['VisitCount'] = ai['VISITCOUNT']
                wores['LastTechnician'] = ai['LASTTECHNICIAN']
                wores['TicketNo'] = WorkOrderAdditionalInfoVO.GetTicket(x['ID'])
                wores['ID'] = x['ID']
                wores['OpDTime'] = b.opdtime
                wores['Status'] = b.status
                try:
                    t = OpTicket.objects.filter(id=b.pid)[0]
                    ticketres = {}
                    ticketres['ID'] = t.id
                    try:
                        ticketres['Status'] = OpBase.objects.get(pid=t.id).status
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
                        contacts['ContactID'] = t.contactid
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
        if len(wores)==0:
            return []
        else:                
            return wores

    def FinalizeWorkOrder(token, WorkOrderID):
        "send an XML request to the remote server mentioning finalization of a Work Order"
        SimpleLogger.do_log("FinalizeWorkOrder()...")
        soapAction = "\"http://office.kwinternational.com/FinalizeWorkOrder\""
        xml_string = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <FinalizeWorkOrder xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iWorkOrderID>{WorkOrderID}</iWorkOrderID>
                        </FinalizeWorkOrder>
                        </soap:Body>
                        </soap:Envelope>
                    """
        soapMessage = xml_string.encode('utf-8')
        SimpleLogger.do_log(f"soapAction= {soapAction}")
        SimpleLogger.do_log(f"soapMessage= {soapMessage}")
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL
        SimpleLogger.do_log(f"uri = {URL}")
        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}
        response = requests.post(url=URL,
                                headers=headers,
                                data=soapMessage,
                                verify=False)
        result = response.content
        SimpleLogger.do_log(f"result= {result}")
        return result

    def RescheduleWorkOrder(token, WorkOrderID, rescheduleStartDTime, rescheduleEndDtime):
        "send an XML request to the remote server mentioning rescheduling of a Work Order"
        SimpleLogger.do_log("FinalizeWorkOrder()...")
        soapAction = "\"http://office.kwinternational.com/RescheduleWorkOrder\""
        xml_string = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <RescheduleWorkOrder xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iWorkOrderID>{WorkOrderID}</iWorkOrderID>
                        <sStartDTime>{rescheduleStartDTime}</sStartDTime>
                        <sEndDTime>{rescheduleEndDtime}</sEndDTime>
                        </RescheduleWorkOrder>
                        </soap:Body>
                        </soap:Envelope>
                    """
        soapMessage = xml_string.encode('utf-8')
        SimpleLogger.do_log(f"soapAction= {soapAction}")
        SimpleLogger.do_log(f"soapMessage= {soapMessage}")
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL
        SimpleLogger.do_log(f"uri = {URL}")
        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}
        response = requests.post(url=URL,
                                headers=headers,
                                data=soapMessage,
                                verify=False)
        result = response.content
        SimpleLogger.do_log(f"result= {result}")
        return result                               

    def GetSQBoxLabelList(workorderid):
        "to run a sql query to get list of SQBox Labels" 
        run_query = f"SELECT PD.PartNo, W.WorkOrderNo, W.AptStartDTime, W.SQBox, T.TicketNo, WH.WarehouseID, WH.Code AS WarehouseCode, A.PartAccountNo AS AccountNo, T.IssueDTime AS TicketDate, ( SELECT TRUNC(MAX(T2.CompleteDTime)) FROM OpTicket T2 INNER JOIN OpBase B2 ON T2.ID = B2.PID INNER JOIN OpWorkOrder W2 ON B2.ID = W2.ID INNER JOIN NSPPartDetails PD2 ON W2.ID= PD2.OpWorkOrderID WHERE PD2.PartNo = PD.PartNo AND T2.SerialNo = T.SerialNo AND T2.CompleteDTime <= T.IssueDTime ) AS PrevTicketDate FROM OpTicket T INNER JOIN OpBase B ON T.ID = B.PID INNER JOIN OpWorkOrder W ON B.ID = W.ID INNER JOIN NSPPartDetails PD ON W.ID = PD.OpWorkOrderID INNER JOIN NSPWarehouses WH ON W.PartWarehouseID = WH.WarehouseID INNER JOIN NSPAccounts A ON T.AccountNo = A.AccountNo INNER JOIN NSPPartSerials PS ON PD.PSID = PS.PSID WHERE W.ID = {workorderid};"
        res = MultipleCursor.send_query(run_query)
        if type(res) is str: #this means there is some SQL error
            print(res)
            return []
        else:
            return res

    def GetDODetailByDONoAndItemNo(doNo, itemNo):
        "to run a SQL query to get list of data from the table NSPDODETAILS" 
        query = NspDoDetails.objects.filter(doid=doNo, itemno=itemNo)
        if query.exists():
            resList = []
            for x in query:
                xd = {}
                xd['DODetailID'] = x.dodetailid
                xd['ItemNo'] = x.itemno
                xd['PONo'] = x.pono
                xd['PartNo'] = x.partno
                xd['Qty'] = x.qty
                xd['Price'] = x.price
                xd['Total'] = x.total
                xd['CoreValue'] = x.corevalue
                xd['Status'] = x.status
                xd['SchQty'] = x.schqty
                xd['RcvQty'] = x.rcvqty
                xd['POItemNo'] = x.poitemno
                xd['RAQty'] = x.raqty
                xd['ClaimQty'] = x.claimqty
                xd['ReturnMessage'] = x.returnmessage
                xd['ISAvailable'] = x.isavailable
                xd['InvoiceItemNo'] = x.invoiceitemno
                try:
                    xd['PartDescription'] = NspPartMasters.objects.get(partno=x.partno).partdescription
                except:
                    xd['PartDescription'] = None    
                xd['RefNo'] = x.refno
                xd['CreatedOn'] = x.createdon
                xd['CreatedBy'] = x.createdby
                xd['UpdatedOn'] = x.updatedon
                xd['UpdatedBy'] = x.updatedby
                if x.createdby is not None:
                    xd['LogBy'] = x.createdby
                else:
                    xd['LogBy'] = x.updatedby
                xd['LogByName'] = None
                resList.append(xd)
            return resList    
        else:
            return []


    def GetDOByNo(doNO):
        "to get data from the table NspDos based on doNO number"
        dos = NspDos.objects.filter(dono=doNO).all()
        resList = []
        for x in dos:
            xd = {}
            xd['DOID'] = x.doid
            xd['AccountNo'] = x.accountno
            xd['WarehouseID'] = x.warehouseid
            xd['DODate'] = x.dodate
            xd['DONo'] = x.dono
            xd['RefNo'] = x.refno
            xd['ItemQty'] = x.itemqty
            xd['TotalQty'] = x.totalqty
            xd['Amount'] = x.amount
            xd['Status'] = x.status
            xd['ShipmentID'] = x.shipmentid
            xd['ETA'] = x.eta
            xd['TrackingNo'] = x.trackingno
            dodetailsList = []
            try:
                dodetails = NspDoDetails.objects.filter(doid=x.doid).all()
                for d in dodetails:
                    xdd = {}
                    xdd['DODetailID'] = d.dodetailid
                    xdd['ItemNo'] = d.itemno
                    xdd['PONo'] = d.pono
                    xdd['PartNo'] = d.partno
                    xdd['Qty'] = d.qty
                    xdd['Price'] = d.price
                    xdd['Total'] = d.total
                    xdd['CoreValue'] = d.corevalue
                    xdd['Status'] = d.status
                    xdd['SchQty'] = d.schqty
                    xdd['RcvQty'] = d.rcvqty
                    xdd['POItemNo'] = d.poitemno
                    xdd['RAQty'] = d.raqty
                    xdd['ClaimQty'] = d.claimqty
                    xdd['ReturnMessage'] = d.returnmessage
                    xdd['ISAvailable'] = d.isavailable
                    xdd['InvoiceItemNo'] = d.invoiceitemno
                    try:
                        xdd['PartDescription'] = NspPartMasters.objects.get(partno=d.partno).partdescription
                    except:
                        xdd['PartDescription'] = None
                    xdd['RefNo'] = d.refno
                    dodetailsList.append(xdd)
            except:
                pass        
            xd['DODetails'] = dodetailsList
            resList.append(xd)
        if len(resList) > 0:    
            return resList[0]
        else:
            return None

    def GetDOByID(doID):
        "to get data from the table NspDos based on do ID"
        dos = NspDos.objects.filter(doid=doID).all()
        resList = []
        for x in dos:
            xd = {}
            xd['DOID'] = x.doid
            xd['AccountNo'] = x.accountno
            xd['WarehouseID'] = x.warehouseid
            xd['DODate'] = x.dodate
            xd['DONo'] = x.dono
            xd['RefNo'] = x.refno
            xd['ItemQty'] = x.itemqty
            xd['TotalQty'] = x.totalqty
            xd['Amount'] = x.amount
            xd['Status'] = x.status
            xd['ShipmentID'] = x.shipmentid
            xd['ETA'] = x.eta
            xd['TrackingNo'] = x.trackingno
            dodetailsList = []
            try:
                dodetails = NspDoDetails.objects.filter(doid=x.doid).all()
                for d in dodetails:
                    xdd = {}
                    xdd['DODetailID'] = d.dodetailid
                    xdd['ItemNo'] = d.itemno
                    xdd['PONo'] = d.pono
                    xdd['PartNo'] = d.partno
                    xdd['Qty'] = d.qty
                    xdd['Price'] = d.price
                    xdd['Total'] = d.total
                    xdd['CoreValue'] = d.corevalue
                    xdd['Status'] = d.status
                    xdd['SchQty'] = d.schqty
                    xdd['RcvQty'] = d.rcvqty
                    xdd['POItemNo'] = d.poitemno
                    xdd['RAQty'] = d.raqty
                    xdd['ClaimQty'] = d.claimqty
                    xdd['ReturnMessage'] = d.returnmessage
                    xdd['ISAvailable'] = d.isavailable
                    xdd['InvoiceItemNo'] = d.invoiceitemno
                    try:
                        xdd['PartDescription'] = NspPartMasters.objects.get(partno=d.partno).partdescription
                    except:
                        xdd['PartDescription'] = None
                    xdd['RefNo'] = d.refno
                    dodetailsList.append(xdd)
            except:
                pass        
            xd['DODetails'] = dodetailsList
            resList.append(xd)
        if len(resList) > 0:    
            return resList[0]
        else:
            return None                          

    def GetDOList(warehouseId, date, refNo, includeOpen, includeClosed, includeCancelled, pageNo, pageSize):
        "to prepare a list based on conditions using the table NSPDOS"
        OffSet = pageNo-1 #SetFirstResult
        Limit = pageSize #SetMaxResults
        refNo = f"'{str(refNo)}'"
        if warehouseId:
            doList1 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), warehouseid=warehouseId, status__lte=60).values().order_by('dono')[OffSet:Limit]
        else:
            doList1 = []   
        if date:
            doList2 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), eta__gte=date, eta__lt=date + datetime.timedelta(days=1), status__lte=60).values().order_by('dono')[OffSet:Limit]
        else:
            doList2 = []        
        if refNo:
            #doList3 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), Q(Q(Q(dono=refNo) | Q(refno=refNo)) | Q(shipmentid=refNo)) | Q(trackingno=refNo), status__lte=60).values().order_by('dono')[OffSet:Limit]
            doList3Query = NspDos.objects.raw(f"SELECT * FROM NSPDOS WHERE (NOT (STATUS = {DOStatus.VOID.value} AND STATUS IS NOT NULL) AND (DONO = {refNo} OR REFNO = {refNo} OR SHIPMENTID = {refNo} OR TRACKINGNO = {refNo}) AND STATUS <= 60.0) ORDER BY DONO ASC OFFSET {OffSet} ROWS FETCH FIRST {Limit} ROWS ONLY")
            doList3 = []
            for p in doList3Query:
                doList3.append({'doid':p.doid,'createdby':p.createdby,'createdon':p.createdon,'updatedby':p.updatedby,'updatedon':p.updatedon,'accountno':p.accountno,'warehouseid':p.warehouseid,'dono':p.dono,'dodate':p.dodate,'refno':p.refno,'itemqty':p.itemqty,'totalqty':p.totalqty,'amount':p.amount,'status':p.status,'shipmentid':p.shipmentid,'eta':p.eta,'trackingno':p.trackingno})
        else:
            doList3 = []  
        if includeOpen is True:
            doList4 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), status__gte=DOStatus.CLOSED.value, status__lte=60).values().order_by('dono')[OffSet:Limit]
        else:
            doList4 = []
        if includeClosed is True:
            doList5 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), Q(status__lt=DOStatus.CLOSED.value) | Q(status__gte=DOStatus.CANCELLED.value), status__lte=60).values().order_by('dono')[OffSet:Limit]
        else:
            doList5 = []
        if includeCancelled is True:
            doList6 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), status__lt=DOStatus.CANCELLED.value).values().order_by('dono')[OffSet:Limit]
        else:
            doList6 = []
        doList = list(chain(doList1, doList2, doList3, doList4, doList5, doList6))
        #SetResult = Paginator(doList, pageSize) 
        #result
        # L
        # lkgfist = SetResult.page(pageNo) 
        #print('processed..')
        #print('doList3 is ', doList3)
        return doList

    def GetDOListCount(warehouseId, date, refNo, includeOpen, includeClosed, includeCancelled):
        "to prepare a list based on conditions using the table NSPDOS and return the total count of the result"
        refNo = f"'{str(refNo)}'"
        if warehouseId:
            doList1 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), warehouseid=warehouseId, status__lte=60).count()
        else:
            doList1 = 0    
        if date:
            doList2 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), eta__gte=date, eta__lt=date + datetime.timedelta(days=1), status__lte=60).count()
        else:
            doList2 = 0       
        if refNo:
            doList3 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), Q(Q(Q(dono=refNo) | Q(refno=refNo)) | Q(shipmentid=refNo)) | Q(trackingno=refNo), status__lte=60).count()
        else:
            doList3 = 0    
        if includeOpen is True:
            doList4 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), status__gte=DOStatus.CLOSED.value, status__lte=60).count()
        else:
            doList4 = 0   
        if includeClosed is True:
            doList5 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), Q(status__lt=DOStatus.CLOSED.value) | Q(status__gte=DOStatus.CANCELLED.value), status__lte=60).count()
        else:
            doList5 = 0    
        if includeCancelled is True:
            doList6 = NspDos.objects.filter(~Q(status=DOStatus.VOID.value), status__lt=DOStatus.CANCELLED.value).count()
        else:
            doList6 = 0
        doList = doList1 + doList2 + doList3 + doList4 + doList5 + doList6
        print('GetDOListCount  -  processing')
        return doList


    def GetDODetailByPSID(DONo, partNo, itemNo):
        "to get records from the table NspDoDetails based on DONo(from partserial by PSID), partNo and itemNO"
        query = f"SELECT * FROM NSPDODETAILS DD RIGHT JOIN NSPDOS DO ON DD.DOID = DO.DOID WHERE DO.DONo = '{DONo}' AND DD.PartNo = '{partNo}' AND DD.Qty - (DD.ClaimQty + DD.RAQty) > 0 ORDER BY DECODE(ItemNo, {itemNo}, 0, 1) ASC, DD.Qty - (DD.ClaimQty + DD.RAQty) DESC" 
        result = MultipleCursor.send_query(query)
        if type(result) is str or len(result)==0:
            return None
        else:
            d = result[0]
            xdd = {}
            xdd['DODetailID'] = d['DODETAILID']
            xdd['ItemNo'] = d['ITEMNO']
            xdd['PONo'] = d['PONO']
            xdd['PartNo'] = d['PARTNO']
            xdd['Qty'] = d['QTY']
            xdd['Price'] = d['PRICE']
            xdd['Total'] = d['TOTAL']
            xdd['CoreValue'] = d['COREVALUE']
            xdd['Status'] = d['STATUS']
            xdd['SchQty'] = d['SCHQTY']
            xdd['RcvQty'] = d['RCVQTY']
            xdd['POItemNo'] = d['POITEMNO']
            xdd['RAQty'] = d['RAQTY']
            xdd['ClaimQty'] = d['CLAIMQTY']
            xdd['ReturnMessage'] = d['RETURNMESSAGE']
            xdd['ISAvailable'] = d['ISAVAILABLE']
            xdd['InvoiceItemNo'] = d['INVOICEITEMNO']
            try:
                xdd['PartDescription'] = NspPartMasters.objects.get(partno=d['PARTNO']).partdescription
            except:
                xdd['PartDescription'] = None
            xdd['RefNo'] = d['REFNO']
            return xdd       


class PictureTrans:
    "define functions related to picture/signature upload controller"
    def __init__(self) -> None:
        pass    

    def SavePictureNonTransaction(request, tablename, refId, fileName, sync, description=None):
        "to save picture-related data"
        file_extension = fileName.split('.')[-1]
        if file_extension!='gif' and file_extension!='jpg' and file_extension!='jpeg' and file_extension!='png' and file_extension!='bmp':
            return f"Invalid or unsupported image type: {fileName}"
        if file_extension=='jpeg':
            file_extension = 'jpg'

        #creating unique filename               
        #unique_filename = str(uuid.uuid4().hex) + '.' + file_extension.lower()
        SimpleLogger.do_log("before get iPictureID") 
        #creating picture object
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        picture_dict = {}
        picture_dict['PictureID'] = DBIDGENERATOR.process_id('Pictures_SEQ')
        picture_dict['TableName'] = tablename
        picture_dict['FilterStr'] = None #no logic found in the C# code for this variable
        picture_dict['FieldName'] = None #no logic found in the C# code for this variable
        picture_dict['Ext'] = file_extension
        picture_dict['Keyword'] = None #no logic found in the C# code for this variable
        picture_dict['Description'] = description
        picture_dict['RefCD'] = refId
        SimpleLogger.do_log(f"iPictureID  {picture_dict['PictureID']}")
        #saving the uploaded file
        SimpleLogger.do_log(f"fileName = {fileName}")
        myfile = request.FILES['fileName']
        fs = FileSystemStorage(location=settings.MEDIA_ROOT+'/pictures')
        save_file_name = str(picture_dict['PictureID']) + '.' + file_extension #saves the file with name of PictureID
        filename = fs.save(save_file_name, myfile)
        uploaded_file_url = settings.MEDIA_ROOT+'/pictures/'+save_file_name
        print(uploaded_file_url)
        picture_dict['FileSize'] = os.path.getsize(uploaded_file_url)
        picture_dict['URL'] = request.scheme + '://' + request.get_host() + '/media/pictures/' + save_file_name
        SimpleLogger.do_log(f"filePath = {uploaded_file_url}")
        SimpleLogger.do_log(f"Picture uploaded: {uploaded_file_url}")
        try:
            Pictures.objects.using('docdb').create(pictureid=picture_dict['PictureID'], createdon=datetime.datetime.today(), createdby=CurrentUserID, tablename=picture_dict['TableName'], ext=picture_dict['Ext'],description=picture_dict['Description'], refcd=picture_dict['RefCD'])
        except:
            Pictures.objects.using('docdb').filter(pictureid=picture_dict['PictureID']).update(updatedon=datetime.datetime.today(), updatedby=CurrentUserID, tablename=picture_dict['TableName'], ext=picture_dict['Ext'],description=picture_dict['Description'], refcd=picture_dict['RefCD'])
        pic = Pictures.objects.using('docdb').get(pictureid=picture_dict['PictureID'])     
        picture_dict['CreatedOn'] = pic.createdon
        picture_dict['CreatedBy'] = pic.createdby
        picture_dict['UpdatedOn'] = pic.updatedon
        picture_dict['UpdatedBy'] = pic.updatedby       
        #make a soap request to a remote server and get the result
        if sync is True:
            wsResult = XMLActions.SyncTicketPictureToGSPN(request.META.get('HTTP_KW_TOKEN'), picture_dict['PictureID'])
            from xml.etree.ElementTree import fromstring
            if wsResult.status_code==400 or wsResult.status_code==500:
                wsResult = '<ERROR>400/500</ERROR>'
            else:
                try:    
                    wsResult = fromstring(wsResult.text) #converting soap response to XML document 
                except:
                    wsResult = '<ERROR>400/500</ERROR>'    
            SimpleLogger.do_log(f"xml.InnerText= {wsResult}")
            xml_error = get_xml_node(wsResult, 'ERROR') 
            if xml_error is not None or xml_error=='':
                pass
                #return f"InternalServerError: {xml_error}"
        return {'picture':picture_dict}

    def SaveWorkOrderSignature(wo, signData, folderId, fileId, refName, CurrentUserID):
        "to save signature data, uploaded by user, as a file"
        #checks if foldername exists in the database by checking NODENAME
        docfolder = {}
        refId = wo[0].workorderno
        f = DocNodes.objects.using('docdb').filter(nodename=refId)
        if not f.exists():
            docfolder['docid'] = folderId
            docfolder['createdon'] = datetime.datetime.today()
            docfolder['createdby'] = CurrentUserID
            try:
                pdocid = DocFolders.objects.using('docdb').get(foldername=refId).docid
            except:
                DocFolders.objects.using('docdb').create(docid=docfolder['docid'], foldername=refId)
                pdocid = DocFolders.objects.using('docdb').get(foldername=refId).docid 
            docfolder['pdocid'] = pdocid
            docfolder['nodetype'] = DocNodeType.FOLDER.value
            docfolder['nodename'] = refId
            docfolder['status'] = DocNodeStatus.OPEN.value
            docfolder['systemid'] = DocSystemID.NONE.value
            docfolder['idtype'] = DocIDType.NORMAL_DOC.value
            DocNodes.objects.using('docdb').create(docid=fileId, createdon=docfolder['createdon'], createdby=docfolder['createdby'], pdocid=docfolder['pdocid'], nodetype=docfolder['nodetype'], nodename=docfolder['nodename'], status=docfolder['status'], systemid=docfolder['systemid'], idtype=docfolder['idtype'])
            SimpleLogger.do_log(f"Doc folder saved: {folderId}") 
        try:
            docfolder['filename'] = refName
            docfolder['ext'] = 'jpg'
            f = DocNodes.objects.using('docdb').filter(nodename=refId)
            dn = DocNodes.objects.using('docdb').get(nodename=refId)
            try:
                DocFiles.objects.using('docdb').create(docid=dn, filename=docfolder['filename'], ext=docfolder['ext']) #entry of file information into the database
            except:
                DocFiles.objects.using('docdb').filter(docid=dn).update(filename=docfolder['filename'], ext=docfolder['ext'])    
            SimpleLogger.do_log(f"Doc file saved: {f[0].docid}")
            #Preparing for saving signData bytes object as a jpg file
            filename = str(f[0].docid) + '.' + docfolder['ext']
            filePath = settings.MEDIA_ROOT+'/docs'
            SimpleLogger.do_log(f"filePath= {filePath+'/'+filename}")
            SimpleLogger.do_log(f"dirPath= {filePath}")
            fs = FileSystemStorage(location=filePath)
            try:
                file_content = base64.b64decode(signData)
                with open(filename, "wb") as f:
                    f.write(file_content)
            except Exception as e:
                print(str(e))
            read_file = open(filename, "rb") #opening file in read/binary mode
            fs.save(filename, read_file) #saving file to our project storage location
            read_file.close()
            os.remove(filename) #remove the temp file from the default location(which is the root of the project)
            SimpleLogger.do_log(f"File saved: {filePath+'/'+filename}")
            media_url = f'/media/docs/{filename}'
            return {'docid':folderId,'url':media_url}
        except Exception as e:
            DocNodes.objects.using('docdb').filter(docid=folderId).delete()
            DocFolders.objects.using('docdb').filter(docid=folderId).delete()
            SimpleLogger.do_log(f"{datetime.datetime.today()} - Error in saving signature data as file: {e}")
            return str(e)

    def SaveReceiptDocument(wo, receiptFile, folderId, fileId, refName, CurrentUserID):
        "to save signature data uploaded by user as a file"
        #checks if foldername exists in the database by checking NODENAME
        docfolder = {}
        refId = wo[0].workorderno
        f = DocNodes.objects.using('docdb').filter(nodename=refId)
        if not f.exists():
            docfolder['docid'] = folderId
            docfolder['createdon'] = datetime.datetime.today()
            docfolder['createdby'] = CurrentUserID
            try:
                pdocid = DocFolders.objects.using('docdb').get(foldername=refId).docid
            except:
                DocFolders.objects.using('docdb').create(docid=docfolder['docid'], foldername=refId)
                pdocid = DocFolders.objects.using('docdb').get(foldername=refId).docid 
            docfolder['pdocid'] = pdocid
            docfolder['nodetype'] = DocNodeType.FOLDER.value
            docfolder['nodename'] = refId
            docfolder['status'] = DocNodeStatus.OPEN.value
            docfolder['systemid'] = DocSystemID.NONE.value
            docfolder['idtype'] = DocIDType.NORMAL_DOC.value
            DocNodes.objects.using('docdb').create(docid=fileId, createdon=docfolder['createdon'], createdby=docfolder['createdby'], pdocid=docfolder['pdocid'], nodetype=docfolder['nodetype'], nodename=docfolder['nodename'], status=docfolder['status'], systemid=docfolder['systemid'], idtype=docfolder['idtype'])
            SimpleLogger.do_log(f"Doc folder saved: {folderId}") 
        
        try:
            docfolder['filename'] = refName
            docfolder['ext'] = 'pdf'
            f = DocNodes.objects.using('docdb').filter(nodename=refId)
            doc_id = f[0].docid
            try:
                DocFiles.objects.using('docdb').create(docid=doc_id, filename=docfolder['filename'], ext=docfolder['ext']) #entry of file information into the database
            except:
                DocFiles.objects.using('docdb').filter(docid=doc_id).update(filename=docfolder['filename'], ext=docfolder['ext'])    
            SimpleLogger.do_log(f"Doc file saved: {f[0].docid}")
            #Preparing for saving signData bytes object as a jpg file
            filePath = settings.MEDIA_ROOT+'/docs'
            pdf_filename = receiptFile['data']['fileName']
            pdf_ext = receiptFile['data']['fileExt']
            pdf_data = receiptFile['data']['fileData']
            filePath = settings.MEDIA_ROOT+'/reports'
            filename = pdf_filename + '.' + pdf_ext
            SimpleLogger.do_log(f"PDFfilePath= {filePath+'/'+filename}")
            SimpleLogger.do_log(f"PDFdirPath= {filePath}")
            fs = FileSystemStorage(location=filePath)
            try:
                file_content = base64.b64decode(pdf_data)
                with open(filename, "wb") as f: #writing data in binary mode
                    f.write(file_content)
            except Exception as e:
                print(str(e))
            read_file = open(filename, "rb") #opening file in read/binary mode
            fs.save(filename, read_file) #saving file to our project storage location
            read_file.close()
            os.remove(filename) #remove the temp file from the default location(which is the root of the project)
            SimpleLogger.do_log(f"Receipt File saved: {filePath+'/'+filename}")
            return {'docid':doc_id}
        except Exception as e:
            DocNodes.objects.using('docdb').filter(docid=folderId).delete()
            DocFolders.objects.using('docdb').filter(docid=folderId).delete()
            SimpleLogger.do_log(f"{datetime.datetime.today()} - Error in saving receipt data as file: {e}")
            return str(e)

    @staticmethod
    def SaveTicketPicture(request, ticket, filePath, iPictureID):
        "to save picture information regarding filepath etc"
        SimpleLogger.do_log("before get iPictureID") 
        #creating picture object
        fileName = os.path.basename(filePath)
        file_extension = fileName.split('.')[0]
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        picture_dict = {}
        picture_dict['PictureID'] = iPictureID
        picture_dict['TableName'] = 'OpTicket'
        picture_dict['FilterStr'] = None #no logic found in the C# code for this variable
        picture_dict['FieldName'] = None #no logic found in the C# code for this variable
        picture_dict['Ext'] = file_extension
        picture_dict['Keyword'] = None #no logic found in the C# code for this variable
        picture_dict['Description'] = None
        picture_dict['RefCD'] = ticket['ID']
        SimpleLogger.do_log(f"iPictureID  {picture_dict['PictureID']}")
        #saving the uploaded file
        SimpleLogger.do_log(f"fileName = {fileName}")
        picture_dict['FileSize'] = os.path.getsize(filePath)
        picture_dict['URL'] = request.get_host() + '/media/pictures/' + fileName
        SimpleLogger.do_log(f"filePath = {filePath}")
        SimpleLogger.do_log(f"Picture uploaded: {picture_dict['URL']}")
        try:
            Pictures.objects.using('docdb').create(pictureid=picture_dict['PictureID'], createdon=datetime.datetime.today(), createdby=CurrentUserID, tablename=picture_dict['TableName'], ext=picture_dict['Ext'],description=picture_dict['Description'], refcd=picture_dict['RefCD'])
        except:
            Pictures.objects.using('docdb').filter(pictureid=picture_dict['PictureID']).update(updatedon=datetime.datetime.today(), updatedby=CurrentUserID, tablename=picture_dict['TableName'], ext=picture_dict['Ext'],description=picture_dict['Description'], refcd=picture_dict['RefCD'])
        pic = Pictures.objects.using('docdb').get(pictureid=picture_dict['PictureID'])     
        picture_dict['CreatedOn'] = pic.createdon
        picture_dict['CreatedBy'] = pic.createdby
        picture_dict['UpdatedOn'] = pic.updatedon
        picture_dict['UpdatedBy'] = pic.updatedby 
        return picture_dict         


class TechEmailService:
    "define different mail functions here"
    def __init__(self) -> None:
        pass

    def SendEmail(message, to, ticketno, NoteID, fullname):
        "function to send email when new notes are saved by the user" 
        from_address = settings.NSP_INFO_EMAIL
        subject = f"[TECHNOTE] Created Tech Note for TK# {ticketno}"
        if settings.DEBUG is True:
            message_body = f"""
                            <font color='ORANGE'><b>TK# {ticketno}</font><br/><br/><font color='ORANGE'>
                            <b>Note# {NoteID}</font><br/><br/>{fullname}<br/><br/>{message}<br/><br/>
                            <a href='http://devoffice.kwinternational.com/nsp/ticketActivity/workOrderNote/workOrderNoteEdit.aspx?OpNote={NoteID}&NoteType=7&popup=1'>Click Here To View Tech Note</a><br/><br/>
                            <a href='http://devoffice.kwinternational.com/nsp/ticket/ticketView.aspx?TicketNo={ticketno}'>Click Here To View Tech</a><br/>
                            """ 
        else:
            message_body = f"""
                            <font color='ORANGE'><b>TK# {ticketno}</font><br/><br/><font color='ORANGE'>
                            <b>Note# {NoteID}</font><br/><br/>{fullname}<br/><br/>{message}<br/><br/>
                            <a href='http://office.kwinternational.com/nsp/ticketActivity/workOrderNote/workOrderNoteEdit.aspx?OpNote={NoteID}&NoteType=7&popup=1'>Click Here To View Tech Note</a><br/><br/>
                            <a href='http://office.kwinternational.com/nsp/ticket/ticketView.aspx?TicketNo={ticketno}'>Click Here To View Tech</a><br/>
                            """ 
        if '@' in to:
            emails_list = to.split(',')
            for e in emails_list:
                action = sendmailoversmtp(e, subject, message_body, from_address)
                if action is True:
                    SimpleLogger.do_log(f"Sent email to : {e}")
                else:
                    SimpleLogger.do_log(f"{datetime.datetime.now()} - ERROR: email cannot be sent to : {e}") 

    def EmailReceipt(token, WorkOrderID, Email):
        "to sends/post an xml doocument as EmailReceipt to a remote server"
        SimpleLogger.do_log("EmailReceipt()...")
        soapAction = "\"http://office.kwinternational.com/EmailReceipt\""
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <EmailReceipt xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iWorkOrderID>{WorkOrderID}</iWorkOrderID>
                        <sEmailTo>{Email}</sEmailTo>
                        </EmailReceipt>
                        </soap:Body>
                        </soap:Envelope>
                        """
        SimpleLogger.do_log(f"soapAction= {soapAction}")
        SimpleLogger.do_log(f"soapMessage= {soapMessage}")
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL

        encoded_request = soapMessage.encode('utf-8')

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)

        result = response.content
        SimpleLogger.do_log(f"result= {result}")
        return result 


class ReportGeneration:
    "use input data to generate reports depending on the requirements"
    def __init__():
        pass

    def CreateWorksheetReport(workorder_dict, SignData):
        "use jasper files and DB data to generate a report in pdf"
        #Getting address and other info
        wo = OpWorkOrder.objects.get(id=workorder_dict['ID'])
        contactid = wo.contactid
        contacts = NspCompanyContacts.objects.get(contactid=contactid)
        name = contacts.name
        adbk = NspAddresses.objects.get(addressid=contacts.addressid)
        address = adbk.address
        op = OpBase.objects.get(id=wo.id).pid
        t = OpTicket.objects.get(id=op)
        #Getting base64-encoded data from the TXT files
        jasperfile1 = open('service_order.txt', 'r', encoding='utf-8')
        templateFileData = jasperfile1.read()
        jasperfile2 = open('sq_service_order_item.txt', 'r', encoding='utf-8')
        subTemplateFileData = jasperfile2.read()
        mock_data = {}
        list_dict = {}
        reportData = {}
        itemsList = []
        reportData['customer_name_address'] = str(name) + ', ' + str(address)
        reportData['make_product'] = t.brand
        try:
            reportData['warranty_status'] = WarrantyStatus(int(wo.warrantystatus)).name
        except:
            reportData['warranty_status'] = WarrantyStatus(0).name    
        try:
            reportData['paid_by'] = PaymentTypeEnum(int(workorder_dict['PaymentType'])).name
        except:
            reportData['paid_by'] = PaymentTypeEnum(0).name 
        reportData['ticket_no'] = t.ticketno
        reportData['serial_no'] = t.serialno
        reportData['model_no'] = t.modelno
        reportData['cell_phone'] = contacts.mobile
        reportData['home_phone'] = contacts.tel
        try:
            reportData['tech_name'] = getuserinfo(t.techid)['UserName']
        except:
            reportData['tech_name'] = None    
        reportData['defect_code'] = t.defectcode
        reportData['defect_symptom'] = t.defectsymptom
        reportData['repair_code'] = wo.repaircode
        reportData['repair_action'] = wo.repairaction
        reportData['status'] = "Cleared"
        try:
            reportData['diag_by'] = getuserinfo(wo.diagnosedby)['UserName']
        except:
            reportData['diag_by'] = None    
        reportData['note'] = wo.note
        reportData['odometer'] = wo.odometer
        try:
            reportData['arriavl_time'] = t.firstcontactdtime.strftime("%m-%d-%Y %H:%M:%S")
        except:
            reportData['arriavl_time'] = ''
        try:        
            reportData['app_date_time'] = t.aptstartdtime.strftime("%m-%d-%Y %H:%M:%S")
        except:
             reportData['app_date_time'] = ''
        try:         
            reportData['date'] = t.issuedtime.strftime('%B %d, %Y') #prints date like January 22, 2022
        except:
            reportData['date'] = '' 
        try:       
            reportData['ticket_issue_date'] = t.issuedtime.strftime('%B %d, %Y')
        except:
            reportData['ticket_issue_date'] = ''    
        reportData['order_no'] = wo.workorderno
        #signaturefile3 = open('base64_signature.txt', 'r', encoding='utf-8')
        #sign_base64 = signaturefile3.read()
        reportData['sign_base64'] = SignData
        pd = NspPartDetails.objects.filter(opworkorderid=wo.id)
        grand_total = 0
        for p in pd:
            price = f"$ {str(p.unitprice)}"       
            itemsList.append({'item':p.partno,'description':p.partdesc,'price':price,'pick_form':p.fromlocation,'box':wo.sqbox})
            try:
                grand_total += p.unitprice
            except:
                pass    
        reportData['items'] = itemsList
        reportData['grand_total'] = f"$ {str(grand_total)}"
        mock_data['multifulFileName'] = "SQ"
        list_dict['templateFileData'] = templateFileData 
        list_dict['templateFileExt'] = ".jasper"
        list_dict['subTemplateFileData'] = subTemplateFileData
        list_dict['subTemplateFileExt'] = ".jasper"
        list_dict['outputType'] = "pdf"
        list_dict['reportParam'] = None
        list_dict['reportData'] = reportData
        list_dict['isBase64'] = True
        mock_data['listReportData'] = [list_dict]
        jasperfile1.close()
        jasperfile2.close()
        #signaturefile3.close()
        #Sending POST request to a remote api for pdf generation
        API_URL = 'http://kwis-prn.kwinternational.com:8080/api/jasper/multiful/rendering'
        encoded_request = json.dumps(mock_data).encode('utf-8')

        headers = {
                "Content-Type": "application/json; charset=UTF-8"
                }

        response = requests.post(url=API_URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)

        result = response.content
        return result                                        




        





        
