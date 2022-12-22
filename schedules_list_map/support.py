#supporting functions
import datetime, requests
from django.conf import settings
from schedules_list_map.schedules import LogType, OpType, ContactLogStatus, ContactResultCode
from schedules_list_map.models import OpContactCustomer, OpTicket, OpBase
from functions.querymethods import MultipleCursor, DBIDGENERATOR, SingleCursor
from functions.kwlogging import SimpleLogger
from schedules_detail.models import NspPartDetails, NspCompanyContacts, NspAddresses
from schedules_list_map.schedules import WorkOrderAdditionalInfoVO
from nsp_user.models import getuserinfo, getboolvalue, getfloatvalue

class ContactSupport:
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetContactLogBySID(SID):
        "to get data from the table OpContactCustomer based on SID and LogType"
        contacts = OpContactCustomer.objects.filter(sid=SID, logtype=LogType.SMS_LOG.value)
        if contacts.count()==0:
            return None
        else:
            ct = contacts[0]
            xd = {}
            xd['ScheduleDTime'] = ct.scheduledtime
            xd['StartDTime'] = ct.startdtime
            xd['FinishDTime'] = ct.finishdtime
            xd['Content'] = ct.contactlog
            xd['LogType'] = ct.logtype
            xd['IsCxDissatisfied'] = ct.iscxdissatisfied
            xd['FollowUpReason'] = ct.followupreason
            xd['ContactResult'] = ct.contactresult
            xd['SatisfactionLevel'] = ct.satisfactionlevel
            xd['Triage'] = ct.triage
            xd['SID'] = ct.sid
            xd['ID'] = ct.id
            try:
                op = OpBase.objects.get(id=ct.id)
                xd['OpDTime'] = ct.opdtime
                xd['OpType'] = ct.optype
                xd['Status'] = ct.status
            except:
                pass
            return xd 


    @staticmethod
    def GetTicket(ID):
        "to get ticket based on ticket ID or contactlog ID"
        try:
            t = OpTicket.objects.filter(id=ID)[0]
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
            for key, value in ticketres.items():
                if value=='':
                    ticketres[key] = None     
        except Exception as e:
            print(e)
            ticketres = None
        return ticketres

    @staticmethod
    def GetWorkOrdersByTicketID(TicketID):
        "to get WorkOrder details by using Ticket ID"
        query = f"SELECT * FROM OpWorkOrder W, OpBase B, Opticket T WHERE T.ID={TicketID} AND W.ID = B.ID AND T.ID = B.PID ORDER BY CASE WHEN B.Status < 60 THEN 1 ELSE 0 END ASC, CASE WHEN W.FinishDTime IS NULL THEN 1 ELSE 0 END ASC, W.FinishDTime ASC, CASE WHEN W.AptStartDTime IS NULL THEN 1 ELSE 0 END ASC, W.AptStartDTime ASC;"
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            try:
                for x in res:
                    wores = {}
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
                    wores['PartCost'] = getfloatvalue(x['PARTCOST'])
                    wores['LaborCost'] = getfloatvalue(x['LABORCOST'])
                    wores['OtherCost'] = getfloatvalue(x['OTHERCOST'])
                    wores['SalesTax'] = getfloatvalue(x['SALESTAX'])
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
                    wores['CreatedOn'] = b.createdon
                    wores['CreatedBy'] = b.createdby
                    wores['UpdatedOn'] = b.updatedon
                    wores['UpdatedBy'] = b.updatedby
                    if b.updatedby is not None:
                        wores['LogBy'] = b.updatedby
                    else:
                        wores['LogBy'] = b.createdby    
                    wores['LogByName'] = None #this is always null as per C# code
                    resList.append(wores)
            except Exception as e:
                print(e)
            return resList

    @staticmethod
    def GetTicketWorkOrders(TicketID):
        "this function returns output from function GetWorkOrdersByTicketID"
        print('running GetTicketWorkOrders...')
        return ContactSupport.GetWorkOrdersByTicketID(TicketID)        
    

    @staticmethod
    def createManagerLog(Ticket, content, CurrentUserID):
        "to save contactlog by creating new record in the OpBase/OpContactCustomer tables"
        ContactLog = {}
        ContactLog['ID'] = DBIDGENERATOR.process_id('OpBase_SEQ')
        ContactLog['OpType'] = OpType.CONTACT_LOG.value
        ContactLog['LogType'] = LogType.MANAGER_LOG.value
        ContactLog['StartDTime'] = datetime.datetime.now()
        ContactLog['Status'] = ContactLogStatus.CLOSED.value
        ContactLog['Content'] = content
        ContactLog['ContactResult'] = ContactResultCode.UNKNOWN.value
        ContactLog['OpDTime'] = datetime.datetime.now()
        originalpid = Ticket['ID']
        OpBase.objects.create(id=ContactLog['ID'], createdon=datetime.datetime.today(), createdby=CurrentUserID, originalpid=originalpid, status=ContactLog['Status'], optype=ContactLog['OpType'], opdtime=ContactLog['OpDTime'], pid=originalpid)
        OpContactCustomer.objects.create(id=ContactLog['ID'], startdtime=ContactLog['StartDTime'], logtype=ContactLog['LogType'],contactlog=ContactLog['Content'], contactresult=ContactLog['ContactResult'])
        return True

    @staticmethod
    def GetTicketByMobile(mobileNo):
        "to get ticket records by mobileNo"
        query = f"select * from opticket T, opbase B, NSPCompanyContacts C where T.contactid = C.contactid AND B.PID = T.ID AND C.mobile LIKE '%{mobileNo}%' ORDER BY DECODE(B.Status, 120, 2, 121, 2, 60, 1, 0) ASC, T.IssueDTime DESC" 
        res = SingleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return None
        else:
            xt = {} #collecting required fields
            xt['ID'] = res['ID']
            xt['SystemID'] = res['SYSTEMID']
            xt['TicketNo'] = res['TICKETNO']
            xt['IssueDTime'] = res['ISSUEDTIME']
            xt['AssignDTime'] = res['ASSIGNDTIME'] 
            xt['ContactScheduleDTime'] = res['CONTACTSCHEDULEDTIME']
            xt['AptStartDTime'] = res['APTSTARTDTIME']
            xt['AptEndDTime'] = res['APTENDDTIME']
            xt['CompleteDTime'] = res['COMPLETEDTIME']
            return xt      



class NSPWSClient:
    "functions for different XML actions"

    @staticmethod
    def RunPostWorkBizLogic(token, ticketNo):
        "to send ticket updation XML report to the remote server"
        SimpleLogger.do_log(f"RunPostWorkBizLogic()...{ticketNo}")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <RunPostWorkBizLogic xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <TicketNo>{ticketNo}</TicketNo>
                        </RunPostWorkBizLogic>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/RunPostWorkBizLogic\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")
        
        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return True

    @staticmethod
    def ExecuteJobDetail(token, JobTypeEnum, jobDetailID):
        "to send job detail report to the remote server"
        SimpleLogger.do_log("ExecuteJobDetail()...")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <ExecuteJobDetail xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iJobType>{JobTypeEnum}</iJobType>
                        <iJobDetailID>{jobDetailID}</iJobDetailID>
                        </ExecuteJobDetail>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/ExecuteJobDetail\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return True

    @staticmethod
    def CreatePartSerial4DODetail(token, doId, itemNo):
        "to send an XML request to the remote server about creating PartSerial for DODetail"
        SimpleLogger.do_log("CreatePartSerial4DODetail()...")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <CreatePartSerial4DODetail xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iDOID>{doId}</iDOID>
                        <iItemNo>{itemNo}</iItemNo>
                        </CreatePartSerial4DODetail>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/CreatePartSerial4DODetail\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return response

    @staticmethod
    def CreatePartSerial4DeliveryOrder(token, doId):
        "to send an XML request to the remote server about creating PartSerial for Delivery Order"
        SimpleLogger.do_log("CreatePartSerial4DeliveryOrder()...")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <CreatePartSerial4DeliveryOrder xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iDOID>{doId}</iDOID>
                        </CreatePartSerial4DeliveryOrder>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/CreatePartSerial4DeliveryOrder\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return response

    @staticmethod
    def CompleteDOReceiving(token, doId):
        "to send an XML request to the remote server about report regarding complete DO receiving"
        SimpleLogger.do_log("CompleteDOReceiving()...")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <CompleteDOReceiving xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iDOID>{doId}</iDOID>
                        </CompleteDOReceiving>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/CompleteDOReceiving\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return response

    @staticmethod
    def SyncTicketPictureToGSPN(token, iPictureID):
        "to send an XML request to the remote KW Office server regarding Ticket Picture" 
        SimpleLogger.do_log("SyncTicketPictureToGSPN()...")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <SyncTicketPictureToGSPN xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iPictureID>{iPictureID}</iPictureID>
                        </SyncTicketPictureToGSPN>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/SyncTicketPictureToGSPN\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return response

    @staticmethod
    def ReceivedCallfireText(token, sFromNo, sMessage, sResult):
        "to send an XML request to the remote KW Office server Call Fire Text" 
        SimpleLogger.do_log("ReceivedCallfireText()...")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <ReceivedCallfireText xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <sFromNo>{sFromNo}</sFromNo>
                        <sMessage>{sMessage}</sMessage>
                        <sResult>{sResult}</sResult>
                        </ReceivedCallfireText>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/ReceivedCallfireText\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return response 

    @staticmethod
    def CreatePickingBatch(token, warehouseId):
        "to send an XML request to the remote KW Office server Call Fire Text" 
        SimpleLogger.do_log("CreatePickingBatch()...", "info")
        soapMessage = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <CreatePickingBatch xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <sWarehouseID>{warehouseId}</sWarehouseID>
                        </CreatePickingBatch>
                        </soap:Body>
                        </soap:Envelope>
                        """ 
        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 
            
        encoded_request = soapMessage.encode('utf-8')
        soapAction = "\"http://office.kwinternational.com/CreatePickingBatch\""

        SimpleLogger.do_log(f"soapAction={soapAction}", "debug")
        SimpleLogger.do_log(f"soapMessage={soapMessage}", "debug")
        SimpleLogger.do_log(f"uri={URL}", "debug")

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)
        SimpleLogger.do_log(f"result= {response}", "debug")
        return response                      


class InventorySupport:
    "functions related to inventory defined here"

    @staticmethod
    def GetInventoryList(warehouseId, locationCode, partNo):
        "to get list of inventory based on values for warehouseId, locationCode and partNo"
        query = f"SELECT a.WarehouseID AS WarehouseID, a.LocationCode AS LocationCode, a.PartNo AS PartNo, COUNT(PSID) AS Qty, COUNT(ToLocationCode) AS OutQty, (SELECT COUNT(x.PSID) FROM NSPPartSerials x WHERE x.WarehouseID = a.WarehouseID AND x.ToLocationCode = a.LocationCode AND x.PartNo = a.PartNo) AS InQty FROM NSPPartSerials a LEFT OUTER JOIN NSPPartMasters b ON b.PartNo = a.PartNo INNER JOIN NSPLocations c ON a.WarehouseID=c.WarehouseID and a.LocationCode=c.LocationCode WHERE a.WarehouseID='{warehouseId}' "
        if locationCode:
            query += f"AND a.LocationCode='{locationCode}' "
        if partNo:
            query += f"AND a.PartNo='{partNo}' AND c.Restricted=0 "
        query += "AND a.OutDate is null GROUP BY a.WarehouseID, a.LocationCode, a.PartNo ORDER BY a.LocationCode, a.PartNo;"
        #print(query)
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['LocationCode'] = x['LOCATIONCODE']
                xd['PartNo'] = x['PARTNO']
                xd['PartDescription'] = x.get('PARTDESCRIPTION')
                xd['Qty'] = x['QTY']
                xd['InQty'] = x['INQTY']
                xd['OutQty'] = x['OUTQTY']
                try:
                    xd['Balance'] = (xd['Qty'] + xd['InQty']) - xd['OutQty']
                except:
                    xd['Balance'] = None    
                resList.append(xd)
            return resList



class FileActions:
    "functions related to file/folder manipulations and others"

    @staticmethod
    def DownloadFromURL(url, file_name):
        get_response = requests.get(url,stream=True)
        with open(file_name, 'wb') as f:
            for chunk in get_response.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)




