import enum, requests, os, xmltodict
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from functions.smtpgateway import sendmailoversmtp
from functions.querymethods import MultipleCursor, SingleCursor, DBIDGENERATOR
from functions.kwlogging import SimpleLogger, AdvancedLogger
from functions.xmlfunctions import get_xml_node, get_xml_node_count, get_xml_childnodes, get_xml_selectnodes
from schedules_list_map.models import Pictures, NspDefectCode, NspSamsungDefectCodes, NspRepairCode, NspSamsungRepairCodes, OpBase, OpTicket, OpWorkOrder, OpWorkOrderAudit, OpTicketAudit
from schedules_detail.models import NspCompanyContacts, NspAddresses, NspPartDetails, DocFiles
from nsp_user.models import getuserinfo, getboolvalue

class UserTicketScheduleType(enum.Enum):
    "creating enumerations of different schedule types"
    NONE = 0
    TODAY = 1
    FUTURE = 2

class AttentionCode(enum.Enum):
    "creating enumerations of different attention codes"
    NO_ISSUE = 0
    PHYSICAL_DAMAGE = 1
    CX_ENVIRONMENT = 2
    NDF = 3
    UNIT_EXCHANGED = 4

class WorkOrderStatus(enum.Enum):
    "values of different workorder status names"
    OPEN = 1
    SCHEDULED = 5
    PROCESSING = 10
    CLOSED = 60
    VOID = 110

class TicketStatus(enum.Enum):
    "values of different ticket status names"
    OPEN = 1
    ACKNOWLEDGE = 10
    CUSTOMER_CONTACT = 20
    IN_REPAIR = 30
    CLOSED = 60
    CANCELLED = 120
    VOID = 121

class OpType(enum.Enum):
    "values of different optypes"
    TICKET = 10010000
    CONTACT_LOG = 10020000 # <-- ContactCustomer
    WORK_ORDER = 10030000
    NOTE = 10040000
    CLAIM = 10050000
    MAIL = 10060000 


class LogType(enum.Enum):
    "values of different log types"
    UNKNOWN = 0
    CUSTOMER_CALL = 1
    TICKET_LOG = 2
    HAPPY_CALL = 3
    MANAGER_LOG = 4
    GSPN_LOG = 5
    SMS_LOG= 6
    CALLFIRE_LOG= 7
    CALLAPI_LOG =10
    NSC_LOG = 11
    CUSTOMER_LOG = 12 

class ContactLogStatus(enum.Enum):
    "values of different contact log status" 
    OPEN = WorkOrderStatus.OPEN.value
    SCHEDULED = WorkOrderStatus.SCHEDULED.value
    PROCESSING = WorkOrderStatus.PROCESSING.value
    CLOSED = WorkOrderStatus.CLOSED.value
    VOID = WorkOrderStatus.VOID.value

class ContactResultCode(enum.Enum):
    "values of different contact result code"
    UNKNOWN = 0
    SUCCESS = 1
    FAIL = 2
    ERR = 3 

class UsageType(enum.Enum):
    "values of different usage types for partdetails data"
    UNKNOWN = -1
    NOT_USED = 0
    USED = 1
    WRONG_PART = 2
    DEFECTIVE_PART = 3

class PartType(enum.Enum):
    "values of different part types"
    UNKNOWN = 0
    PART = 1
    LABOR = 2
    JOB = 3

class LocationType(enum.Enum):
    "values of different location types"
    UNKNOWN = 0
    STORAGE = 1
    SYSTEM = 2
    SQBOX = 3
    VEHICLE = 4

class ReserveStatus(enum.Enum):
    "values of different reserve status"
    UNKNOWN = 0
    NOT_REQUIRED = 1
    RESERVED = 2
    PICKING = 3
    CONFIRMED = 4
    RESCHEDULED = 5

class SystemIDEnum(enum.Enum):
    "values of different System IDs"
    IT = 1
    GSPN = 2
    SQ = 3
    BODY_FRIENDS = 4
    SVC_BNCH = 5
    SVC_PWR = 6 

class RepairResultCodeEnum(enum.Enum):
    "values of different Repair Result Codes" 
    UNKNOWN = 0
    SUCCESS = 1
    FAIL = 2 

class RepairFailCodeEnum(enum.Enum):
    "values of different repair fail codes"
    NONE = 0
    UNIT_MOUNTED = 1
    WRONG_PARTS = 2
    DEFECTIVE_PARTS = 3
    MORE_PARTS_NEEDED = 4
    PHYSICAL_DAMAGE = 5
    UNREPAIRABLE = 6
    DIAGNOSIS_ONLY = 7
    CUSTOMER_NOT_HOME = 8
    RESCHEDULE = 9
    DIFF_PARTS_NEEDED = 10
    DIFF_ASC_COMPLETED = 11
    CX_REQUESTED_CANCEL = 12
    NOT_VISITED_CX_ISSUE = 13
    NOT_VISITED_LOCAL_ISSUE = 14
    NOT_VISITED_PART_ISSUE = 15 

class DocSystemID(enum.Enum):
    "values of different doc system IDs"
    NONE = 0
    ROOT = 1
    SYSTEM_ROOT = 2
    PACKAGE = 3
    DELIVERY_ORDER = 4
    SCANDOC = 5
    EFILING = 6
    SHARE_FOLDER = 7
    FAX = 8
    FAX_LOGIPIA = 9
    PURCHASE_ORDER = 10
    WAREHOUSE_SHIPMENT = 11
    ITSJOB = 12
    APPROVAL = 13
    RBJOB = 14
    NPCPANEL = 15
    NPCSHIPMENT = 16
    IMEXPORTINVOICE = 17
    NSP = 18
    SYSTEM_MAX = 999

class DocNodeType(enum.Enum):
    "values of different doc node types"
    UNKNOWN = 0
    FILE = 1
    FOLDER = 2
    LINK = 3

class DocNodeStatus(enum.Enum):
    "values of different doc node status"
    UNKNOWN = 0
    OPEN = 1
    ARCHIVED = 60
    DELETED = 110

class DocIDType(enum.Enum):
    "values of different doc ID types"
    NORMAL_DOC = 0
    FAX_DOC = 1

class PaymentTypeEnum(enum.Enum):
    "values of different payment types"
    UNKNOWN = 0
    NO_PAYMENT = 1
    CHECK = 2
    CREDIT_CARD = 3
    CASH = 4

class WarrantyStatus(enum.Enum):
    "values of different warranty status"
    UNKNOWN = 0
    IN_WARRANTY = 1
    OUT_OF_WARRANTY = 2
    OTWE_LP = 3
    OTWE_P = 4
    OTWE_L = 5
    THIRD = 6   

class NoteTypeEnum(enum.Enum):
    "values of different note types"
    UNKNOWN = 0
    TICKET_REVIEW = 1
    REDO_TICKET_REVIEW = 2
    QOS_REVIEW = 3
    ISSUE_NOTE = 4
    MY_NOTE = 6
    TECH_NOTE = 7

class DOStatus(enum.Enum):
    "values of different status for NSPDOs"
    OPEN = 1
    PROCESSING = 10
    CLOSED = 60
    CANCELLED = 120
    VOID = 121

class DODetailStatus(enum.Enum):
    "values of different DOs detail status"
    OPEN = 1
    PROCESSING = 10
    CLOSED = 60
    CANCELLED = 120
    VOID = 121    

class JobType(enum.Enum):
    "values of different job types"
    UNKNOWN = 0
    RECEIVING = 10
    PICKING = 20
    CHECK_OUT = 30
    CHECK_IN = 40
    RA_READY = 50
    RA_SUBMIT = 51
    RA_SHIP = 52
    CORE_READY = 60
    CORE_SUBMIT = 61
    CORE_SHIP = 62
    UNTANGLE = 70

class JobStatus(enum.Enum):
    "values of job status"
    UNKNOWN = 0
    OPEN = 1
    PROCESSING = 10
    COMPLETED = 60
    CANCELLED = 110

class JobDetailStatus(enum.Enum):
    "values of job detail status"
    UNKNOWN = 0
    OPEN = 1
    PROCESSING = 10
    COMPLETED = 60
    CANCELLED = 110

class PartSerialStatus(enum.Enum):
    "values of different part serial status"
    UNKNOWN = 0
    OPEN = 1
    RECEIVED = 5
    RA_READY = 40
    RA_SUBMITTED = 41
    RA_APPROVED = 42
    RA_SHIPPED = 43
    RA_DELIVERED = 44
    RA_HOLD = 45
    CLOSED = 60
    RA_REJECTED = 61
    RA_BACK_TO_CUSTOMER = 62
    CORE = 100
    CORE_READY = CORE + RA_READY,
    CORE_SUBMITTED = CORE + RA_SUBMITTED,
    CORE_APPROVED = CORE + RA_APPROVED,
    CORE_SHIPPED = CORE + RA_SHIPPED,
    CORE_DELIVERED = CORE + RA_DELIVERED,
    CORE_HOLD = CORE + RA_HOLD,
    CORE_CLOSE = CORE + CLOSED,
    CORE_REJECTED = CORE + RA_REJECTED,
    CORE_STC = CORE + RA_BACK_TO_CUSTOMER

class OutType(enum.Enum):
    "values of different outtypes"
    NONE = 0
    USED = 1
    RA = 2
    SCRAP = 3
    LOST = 4


class WarehouseType(enum.Enum):
    "values of different warehouse types"
    SQ_LOCAL_WAREHOUSE = 1
    RDC_WAREHOUSE = 2


class OUT_TYPE(enum.Enum):
    "values of different out types"
    UNKNOWN = -1
    NONE = 0
    USED = 1
    RA = 2
    SCRAP = 3
    LOST = 4
    CORE = 5


class STATUS_TYPE(enum.Enum):
    "values of different status types"
    NONE = 0
    OPEN = 1
    ACTIVE = 1
    SCHEDULED = 5
    PROCESSING = 10
    MAX_ACTIVE = 50
    CLOSED = 60
    COMPLETED = 60
    MAX_VALID = 100
    VOID = 110
    CANCELLED = 120
    FAIL = 130
    ALL = 255
    RA_READY = 40
    RA_SUBMITTED = 41
    RA_APPROVED = 42
    RA_SHIPPED = 43
    RA_DELIVERED = 44
    RA_HOLD = 45
    CLOSE = 60
    RA_REJECTED = 61
    RA_STC = 62
    CORE = 100
    CORE_READY = 140
    CORE_SUBMITTED = 141
    CORE_APPROVED = 142
    CORE_SHIPPED = 143
    CORE_DELIVERED = 144
    CORE_HOLD = 145
    CORE_CLOSE = 160
    CORE_REJECTED = 161
    CORE_STC = 162
    ACKNOWLEDGE = 10
    CUSTOMER_CONTACT = 20
    REPAIR = 30
    GOOD_DELIVERED = 70
    REJECTED = 110

class USAGE_TYPE(enum.Enum):
    "values of different usage types"
    UNKNOWN = -1
    NOT_USED = 0
    USED = 1
    WRONG_PART = 2
    DEFECTIVE_PART = 3

class LOCATION_TYPE(enum.Enum):
    "values of different location types" 
    UNKNOWN = 0
    STORAGE = 1
    SYSTEM = 2
    SQBOX = 3
    VEHICLE = 4
    NSC = 5

class JOB_TYPE(enum.Enum):
    UNKNOWN = 0
    RECEIVING = 10
    PICKING = 20
    CHECK_OUT = 30
    CHECK_IN = 40
    RA_READY = 50
    RA_SUBMIT = 51
    RA_SHIP = 52
    CORE_READY = 60
    CORE_SUBMIT = 61
    CORE_SHIP = 62

class RESERVE_STATUS(enum.Enum):
    UNKNOWN = 0
    NOT_REQUIRED = 1
    RESERVED = 2
    PICKING = 3
    CONFIRMED = 4
    RESCHEDULED = 5

class SYSTEM_ID(enum.Enum):
    NONE = 0
    IT = 1
    GSPN = 2
    SQ = 3
    BF = 4
    SVC_BNCH = 5
    SVC_PWR = 6
    SVC_LIVE = 7

class NSP_STATUS(enum.Enum):
    ENABLED = 1
    DISABLED = 60

class NSP_PERMIT_OBJECT(enum.Enum):
    READ_INFO = 0
    DISPATCH = 1
    UPDATE_ZONE_SLOT = 2
    UPLOAD_STORE_COVERAGE = 3
    CREATE_WAREHOUSESHIPMENT = 4
    UPDATE_MASTER = 5
    UPDATE_NSPPART = 6
    VIEW_COMMISSION = 7
    TRACK_STATUS = 8
    UPDATE_CUSTOMER_INFO_FOR_INACTIVE_TICKET = 9
    UPDATE_NSP_USER = 10
    UPDATE_SETTING = 11
    READ_REPORT = 12
    UPDATE_QOS = 13
    UPDATE_MAIL_TEMPLATE = 14
    UPDATE_GEODATA = 15
    ASSIGN_TICKET_WAREHOUSE = 16
    CHANGE_TICKET_WAREHOUSE = 17
    TRACK_STATUS_FOR_MANAGER = 18
    CLAIM = 19
    MANAGE_USER_ACCOUNT = 20
    UPDATE_INACTIVE_WORKORDER = 21
    SCHEDULE_APPOINTMENT = 22
    CONFIG_WAREHOUSE = 23
    REBUILD_ROUTING = 24
    UPDATE_REASONCODE = 25
    UPDATE_HOLIDAY = 26
    UPDATE_BIZ_HOUR = 27
    UPDATE_SQ_FEES = 28
    UPDATE_MODEL_DOC_TYPE = 29
    UPDATE_MODEL_DOC = 30
    UPDATE_SQL_MINING = 31
    USE_SQL_MINING = 32
    REGISTER_PART = 33
    DEREGISTER_PART = 34
    REGISTER_LOCATION = 35
    DEREGISTER_LOCATION = 36
    DO_RECEIVING = 37
    DO_TRACKING = 38
    DO_VIEW = 39
    MOVE_PART = 40
    DIAGNOSIS = 41
    UPDATE_RA_REASON = 42
    PART_ORDER = 43
    ASSIGN_COORDINATOR = 44
    EDIT_ACCOUNT_NO = 45
    ADD_ACCOUNT_NO = 46
    LOCATION_MANAGER = 47
    MANAGER_TECH = 48
    IGNORE_COMPANY = 49
    SET_SYSTEM_LOCATION = 50
    UPDATE_CALLFIRE_TERM = 51
    SEND_BBB_MAIL = 52
    CLAIM_MANAGER = 53
    SUPERVISOR = 54
    CHANGE_TECH = 55
    CORRECT_PD_PS = 56
    REOPEN_TICKET = 57
    COMPLETE_DATE_SWITCH = 58
    EDIT_RESCHEDULED_SO = 59
    EDIT_COMPANY = 60
    EDIT_JOB = 61
    MOVE_PART_TO_OTHER_WAREHOUSE = 62
    MODIFY_SO_APT = 63
    EDIT_GSPN_TECH_ID = 64
    PART_SUPERVISOR = 65
    UPDATE_PRODUCT_TYPE = 66
    UPDATE_PNN_EXCEPTION = 67
    UPDATE_TECH_INCENTIVE = 68
    UPDATE_INTERFACE_TO_SAP = 69
    VIEW_QUERY_RECORD = 70
    REQUIRED_PARTS = 71
    UPDATE_CLAIM_PARTS = 72
    SEND_MASS_APPOINTMENT_NOTICE = 73
    REOPEN_CLAIMED_DO = 74
    AUTO_ROUTING = 75

class WAREHOUSE_TYPE(enum.Enum):
    UNKNOWN = 0
    SQ_LOCAL_WAREHOUSE = 1
    RDC_WAREHOUSE = 2
    NSC_WAREHOUSE = 3                                                         


class GetTechnicianCurrentWorkOrders:
    "to get technician current work orders based on user_id and schedule type"
    def __init__(self) -> None:
        pass

    @staticmethod  
    def process_query(user_id, schedule_type_name, CurrentUserID, token):
        "getting data by running a SQL query"
        resList = []
        if schedule_type_name=='TODAY': 
            workorder_query = f"SELECT * FROM OPWorkOrder W, opbase B WHERE W.ID = B.ID AND W.TechnicianID = {user_id} AND (B.Status < 60 OR W.StartDTime IS NOT NULL) AND (B.Status < 60 OR W.FinishDTime >= TRUNC(CURRENT_DATE)) AND NVL(W.StartDTime, W.AptStartDTime) >= TRUNC(CURRENT_DATE) AND NVL(W.StartDTime, W.AptStartDTime) < TRUNC(CURRENT_DATE) + 1 ORDER BY NVL(W.StartDTime, W.AptStartDTime) ASC"
        elif schedule_type_name=='FUTURE':
            workorder_query = f"SELECT * FROM OPWorkOrder W, opbase B WHERE W.ID = B.ID AND W.TechnicianID = {user_id} AND (B.Status < 60 OR W.StartDTime IS NOT NULL) AND (B.Status < 60 OR W.FinishDTime >= TRUNC(CURRENT_DATE)) AND NVL(W.StartDTime, W.AptStartDTime) >= TRUNC(CURRENT_DATE) + 1 ORDER BY NVL(W.StartDTime, W.AptStartDTime) ASC"
        else:
            workorder_query = f"SELECT * FROM OPWorkOrder W, opbase B WHERE W.ID = B.ID AND W.TechnicianID = {user_id} AND (B.Status < 60 OR W.StartDTime IS NOT NULL) AND (B.Status < 60 OR W.FinishDTime >= TRUNC(CURRENT_DATE)) ORDER BY NVL(W.StartDTime, W.AptStartDTime) ASC" 
        workorders_list = MultipleCursor.send_query(workorder_query, 25)
        if type(workorders_list) is str or workorders_list is None: #if there is error
            return []
        for x in workorders_list:
            wores = {}
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
            wores['WarrantyStatus'] = x['WARRANTYSTATUS']
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
                PartDetails.append(partdict)
            wores['PartDetails'] = PartDetails
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
            try:
                b = OpBase.objects.get(id=x['ID'])
                wores['OpDTime'] = b.opdtime
                wores['Status'] = b.status
            except:
                wores['OpDTime'] = None
                wores['Status'] = None
            try:
                t = OpTicket.objects.get(id=b.pid)
                print('the ticket res = ', t)
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
                ticketres['WtyException'] = t.wtyexception
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
                ticketres['LastAttentionCode'] = WorkOrderAdditionalInfoVO.GetLastAttentionCode(t.serialno)
                ticketres['AlertMessage'] = t.alertmessage
                ticketres['ContactLogs'] = WorkOrderAdditionalInfoVO.GetTicketContactLogs(t.id)
                ticketres['Documents'] = WorkOrderAdditionalInfoVO.GetTicketDocuments(t.id, t.modelno)
                ticketres['Notes'] = WorkOrderAdditionalInfoVO.GetTicketNotes(t.id)
                ticketres['Pictures'] = WorkOrderAdditionalInfoVO.GetTicketPictures(t.id)
                ticketres['SamsungModelDocuments'] = GspnWebServiceClient.GetModelDocuments(t.modelno, CurrentUserID) #Samsung GSPN service not working currently, so just return empty list
                #ticketres['SamsungModelDocuments'] = [] 
            except Exception as e:
                print(e)
                ticketres = None
            wores['Ticket'] = ticketres    
            try:
                b = OpBase.objects.get(id=x['ID'])    
                wores['CreatedOn'] = b.createdon
                wores['CreatedBy'] = b.createdby
                wores['UpdatedOn'] = b.updatedon
                wores['UpdatedBy'] = b.updatedby
                if b.updatedby is not None:
                    wores['LogBy'] = b.updatedby
                else:
                    wores['LogBy'] = b.createdby 
            except:
                wores['CreatedOn'] = None
                wores['CreatedBy'] = None
                wores['UpdatedOn'] = None
                wores['UpdatedBy'] = None
                wores['LogBy'] = None
            wores['LogByName'] = None #this is always null as per C# code        
            resList.append(wores)
        return resList

class GspnWebServiceClient:
    "to get codes and other data using samsung GSPN service"
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetDefectCodeListByModelNo(ModelNo, CurrentUserID):
        "to get a list of defect codes by using model no and sending request data to samsung soap API" 
        xml_document = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                        <rootdoc>
                        <Company>{settings.GSPN_COMPANY}</Company>
                        <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                        <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                        <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                        <ASCNo>{settings.GSPN_ASC_NO_KWINT}</ASCNo>
                        <CodeType>{settings.GSPN_CODE_TYPE_DEFECT}</CodeType>
                        <ModelCode>{ModelNo}</ModelCode>
                        </rootdoc>
                        """
        ###XML not working here, so request data is formatted in the form of dict and sent as JSON request.                
        reqXmlString = {'Company':settings.GSPN_COMPANY, 'ASCName':settings.GSPN_ASC_NAME, 'WSUserID':settings.GSPN_WS_USER_ID, 'WSPassword':settings.GSPN_WS_PASSWORD,'ASCNo':settings.GSPN_ASC_NO_KWINT,'CodeType':settings.GSPN_CODE_TYPE_DEFECT,'ModelCode':ModelNo}     
        SimpleLogger.do_log(f">>> reqXmlString = {reqXmlString}") 
        s = AdvancedLogger
        s.startlog(ModelNo, 'GET', 'GetCodeList', reqXmlString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()

        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}

        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN          

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqXmlString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time. There are 10 million ticks per second
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(ModelNo, 'GET', "GetCodeList", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            return '<ERROR></ERROR>'
        else:
            return resXmlString

    @staticmethod
    def GetRepairCodeListByModelNo(ModelNo, CurrentUserID):
        "to get a list of repair codes by using model no and sending request data to samsung soap API" 
        reqDataString = {'Company':settings.GSPN_COMPANY, 'ASCName':settings.GSPN_ASC_NAME, 'WSUserID':settings.GSPN_WS_USER_ID, 'WSPassword':settings.GSPN_WS_PASSWORD,'ASCNo':settings.GSPN_ASC_NO_KWINT,'CodeType':settings.GSPN_CODE_TYPE_REPAIR,'ModelCode':ModelNo}     
        SimpleLogger.do_log(f">>> reqXmlString = {reqDataString}") 
        s = AdvancedLogger
        s.startlog(ModelNo, 'GET', 'GetCodeList', reqDataString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}

        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqDataString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(ModelNo, 'GET', "GetCodeList", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            return '<ERROR></ERROR>'
        else:
            return resXmlString


    @staticmethod
    def GetModelDocuments(ModelNo, CurrentUserID):
        "to get model documents from Samsung GSPN"
        reqDataString = {'Company':settings.GSPN_COMPANY, 'ASCName':settings.GSPN_ASC_NAME, 'WSUserID':settings.GSPN_WS_USER_ID, 'WSPassword':settings.GSPN_WS_PASSWORD,'ModelCode':ModelNo}     
        SimpleLogger.do_log(f">>> reqXmlString = {reqDataString}") 
        s = AdvancedLogger
        s.startlog(ModelNo, 'GET', 'GetCodeList', reqDataString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetModelDocuments\""}


        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqDataString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(ModelNo, 'GET', "GetCodeList", resXmlString, CurrentUserID, elapsed_time)
        print('samsung GSPN response for ModelDocuments ', response)
        if response.status_code==400 or response.status_code==500:
            return []
        else:
            return resXmlString


    @staticmethod
    def SetPartReturnRequest(psId, accountNo, invoiceNo, returnCode, returnReason, subReasonCode, itemNo, returnQty, fileName, binary, CurrentUserID):
        "create request for gspnClient"
        xml_document = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                        <rootdoc>
                        <Company>{settings.GSPN_COMPANY}</Company>
                        <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                        <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                        <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                        <ASCNo>{accountNo}</ASCNo>
                        <InvoiceNo>{invoiceNo}</InvoiceNo>
                        <ReturnCode>{returnCode}</ReturnCode>
                        <ReturnReason>{returnReason}</ReturnReason>
                        <SubReasonCode>{subReasonCode}</SubReasonCode>
                        <FileName>{fileName}</FileName>
                        <Binary>{binary}</Binary>
                        <table>
                            <name>PartTB</name>
                            <column>
                                <name>ItemNo</name>
                                <type>String</type>
                            </column>
                            <column>
                                <name>ReturnQty</name>
                                <type>String</type>
                            </column>
                            <row>
                                <ItemNo>{itemNo}</ItemNo>
                            </row>
                            <row>
                                <ReturnQty>{returnQty}</ReturnQty>
                            </row>
                        </table>
                        </rootdoc>
                        """
        reqXmlString = xml_document                
        SimpleLogger.do_log(f">>> reqXmlString = {reqXmlString}")
        s = AdvancedLogger
        s.startlog(str(psId), 'GET', 'SetPartReturnRequest', reqXmlString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}

        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqXmlString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(str(psId), 'GET', "SetPartReturnRequest", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            return '<ERROR></ERROR>'
        else:
            return resXmlString

    @staticmethod
    def SetStockAdjust(ASCNo, Branch, AdjReason, PartNo, AdjQty, CurrentUserID):
        "create request for gspnClient"
        reqXmlString = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                        <rootdoc>
                        <Company>{settings.GSPN_COMPANY}</Company>
                        <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                        <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                        <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                        <ASCNo>{ASCNo}</ASCNo>
                        <Branch>{Branch}</Branch>
                        <AdjReason>{AdjReason}</AdjReason>
                        <PartNo>{PartNo}</PartNo>
                        <AdjQty>{str(AdjQty)}</AdjQty>
                        </rootdoc>
                        """ 
        SimpleLogger.do_log(f">>> reqXmlString = {reqXmlString}", "debug")
        s = AdvancedLogger
        s.startlog(Branch + "/" + PartNo, 'GET', 'SetStockAdjust', reqXmlString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}

        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqXmlString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(Branch + "/" + PartNo, 'GET', "SetStockAdjust", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            return '<ERROR></ERROR>'
        else:
            return resXmlString 


    @staticmethod
    def SetPartReturnFileUpload(psId, accountNo, rmaNo, fileName, fileSize, binary, CurrentUserID):
        "create request for gspnClient"
        reqXmlString = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                        <rootdoc>
                        <Company>{settings.GSPN_COMPANY}</Company>
                        <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                        <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                        <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                        <ASCNo>{accountNo}</ASCNo>
                        <RMANo>{rmaNo}</RMANo>
                        <FileName>{fileName}</FileName>
                        <FileSize>{fileSize}</FileSize>
                        <Binary>{str(binary)}</Binary>
                        </rootdoc>
                        """ 
        SimpleLogger.do_log(f">>> reqXmlString = {reqXmlString}", "debug")
        s = AdvancedLogger
        s.startlog(str(psId), 'POST', 'SetPartReturnFileUpload', reqXmlString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}

        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqXmlString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(str(psId), 'POST', "SetPartReturnFileUpload", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            return '<ERROR></ERROR>'
        else:
            return resXmlString

    @staticmethod
    def SyncTicketInfoToGSPN(CurrentUserID, pOpTicket, bComplete=False, dtWER='', data='', bRecursion=False):
        "create request for gspnClient"
        IS_BEFORE_ACKNOWLEDGED = "To change the policy, you must be acknowledged (ST015) the ticket first, then can do the Engineer Assign or Pending."
        reqXmlString = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                        <rootdoc>
                        <Company>{settings.GSPN_COMPANY}</Company>
                        <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                        <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                        <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                        <ASCNo>{pOpTicket.ascnumber}</ASCNo>
                        <bComplete>{bComplete}</bComplete>
                        <dtWER>{dtWER}</dtWER>
                        <data>{data}</data>
                        <bRecursion>{bRecursion}</bRecursion>
                        </rootdoc>
                        """ 
        SimpleLogger.do_log(f">>> reqXmlString = {reqXmlString}", "debug")
        s = AdvancedLogger
        s.startlog(str(pOpTicket.ascnumber), 'POST', 'SyncTicketInfoToGSPN', reqXmlString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}


        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqXmlString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(str(pOpTicket.ascnumber), 'POST', "SyncTicketInfoToGSPN", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            raise Exception(f"Error While Update GSPN for Ticket {pOpTicket.ascnumber}")
        else:
            return resXmlString         


    @staticmethod
    def GetPartCoreRANo(CurrentUserID, sASCNo, sInvoiceDateFrom, sInvoiceDateTo, sInvoiceNo, sPartNo, iStatus=0):
        "create request for gspnClient"
        if iStatus==0:
            reqXmlString = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                            <rootdoc>
                            <Company>{settings.GSPN_COMPANY}</Company>
                            <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                            <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                            <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                            <InvoiceDateFrom>{sInvoiceDateFrom}</InvoiceDateFrom>
                            <InvoiceDateTo>{sInvoiceDateTo}</InvoiceDateTo>
                            <ASCNo>{sASCNo}</ASCNo>
                            <InvoiceNo>{sInvoiceNo}</InvoiceNo>
                            <PartNo>{sPartNo}</PartNo>
                            <Status>AL</Status>
                            </rootdoc>
                            """
        elif iStatus==2:
            reqXmlString = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                            <rootdoc>
                            <Company>{settings.GSPN_COMPANY}</Company>
                            <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                            <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                            <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                            <InvoiceDateFrom>{sInvoiceDateFrom}</InvoiceDateFrom>
                            <InvoiceDateTo>{sInvoiceDateTo}</InvoiceDateTo>
                            <ASCNo>{sASCNo}</ASCNo>
                            <InvoiceNo>{sInvoiceNo}</InvoiceNo>
                            <PartNo>{sPartNo}</PartNo>
                            <Status>CL</Status>
                            </rootdoc>
                            """
        else:
            reqXmlString = f"""<?xml version=\"1.0\" encoding=\"utf-8\" ?>
                            <rootdoc>
                            <Company>{settings.GSPN_COMPANY}</Company>
                            <ASCName>{settings.GSPN_ASC_NAME}</ASCName>
                            <WSUserID>{settings.GSPN_WS_USER_ID}</WSUserID>
                            <WSPassword>{settings.GSPN_WS_PASSWORD}</WSPassword>
                            <InvoiceDateFrom>{sInvoiceDateFrom}</InvoiceDateFrom>
                            <InvoiceDateTo>{sInvoiceDateTo}</InvoiceDateTo>
                            <ASCNo>{sASCNo}</ASCNo>
                            <InvoiceNo>{sInvoiceNo}</InvoiceNo>
                            <PartNo>{sPartNo}</PartNo>
                            <Status>OP</Status>
                            </rootdoc>
                            """ 
        SimpleLogger.do_log(f">>> reqXmlString = {reqXmlString}", "debug")
        s = AdvancedLogger
        log_item = str(sInvoiceNo) + '-' + str(sPartNo)
        s.startlog(log_item, 'POST', 'SetPartReturnFileUpload', reqXmlString, CurrentUserID)
        #Sending XML Request
        StartTime = datetime.utcnow()
        headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "SOAPAction": "\"www.samsungasc.com/GetCodeList\""}

        if settings.DEBUG is True:
            URL = settings.DEV_GSPN
        else:
            URL = settings.PROD_GSPN        

        response = requests.post(url=URL,
                                headers=headers,
                                data=reqXmlString,
                                verify=False)

        resXmlString = response.text
        SimpleLogger.do_log(f">>> resXmlString = {resXmlString}")
        #Calculating Ticks at Start of Time
        t0 = datetime(1, 1, 1)
        seconds = (StartTime - t0).total_seconds()
        ticks = seconds * 10**7
        #Calculating the NOW ticks
        nowTime = datetime.utcnow()
        seconds = (nowTime - t0).total_seconds()
        ticks_now = seconds * 10**7
        
        elapsed_time = round((ticks_now - ticks) / 10000)

        s.stoplog(log_item, 'POST', "SetPartReturnFileUpload", resXmlString, CurrentUserID, elapsed_time)
        if response.status_code==400 or response.status_code==500:
            return '<ERROR></ERROR>'
        else:
            return resXmlString                                                             
                                                           
                                                            


class WorkOrderAdditionalInfoVO:
    "to process additional info for work orders"
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetGSPNTechIDWithRA(userid):
        "to get GSPN Technician ID with RA"
        s_query = f"SELECT * FROM ( SELECT DISTINCT DECODE(VDEOrigin, 1, VDETechnicianID, DECODE(REFOrigin, 1, REFTechnicianID, DECODE(HKEOrigin, 1, HKETechnicianID, DECODE(WSMOrigin, 1, WSMTechnicianID, '')))) AS GSPNTechID FROM NSPGSPNTechnicianIDs WHERE UserID = {userid} AND Status = 1 ) WHERE GSPNTechID IS NOT NULL;"
        res = MultipleCursor.send_query(s_query)
        if type(res) is str or len(res)==0: #if error, returns None
            return None
        else:
            return str(res[0]['GSPNTECHID']) #List of objects as string    

    @staticmethod
    def get_info(workorderID):
        "collect data from different sql queries" 
        ai = {}
        #TICKETCOUNT
        ticketcount_query = f"SELECT COUNT(*) FROM OpBase B INNER JOIN OpTicket T ON B.PID = T.ID INNER JOIN OpTicket T2 ON T.SerialNo = T2.SerialNo AND T.IssueDTime > T2.IssueDTime AND T.SerialNo <> 'M000' INNER JOIN OpBase B2 ON T2.ID = B2.ID WHERE B2.Status = 60 AND B.ID = {workorderID}"
        ticketcount = SingleCursor.send_query(ticketcount_query)['COUNT(*)']
        ai['TICKETCOUNT'] = ticketcount
        #VISITCOUNT
        visitcount_query = f"SELECT COUNT(*) FROM OpBase B INNER JOIN opbase b2 ON b.pid = b2.pid AND b2.optype = 10030000 AND b.ID > b2.ID INNER JOIN OpWorkOrder W ON B2.ID = W.ID WHERE W.RepairFailCode NOT IN (1, 8, 9, 12, 13, 14, 15) AND b.id = {workorderID}"
        visitcount = SingleCursor.send_query(visitcount_query)['COUNT(*)']
        ai['VISITCOUNT'] = visitcount
        #REDO
        redo_query = f"SELECT COUNT(*) FROM OpBase B INNER JOIN OpTicket T ON B.PID = T.ID INNER JOIN OpTicket T2 ON T.SerialNo = T2.SerialNo AND T.IssueDTime > T2.IssueDTime AND T.IssueDTime < T2.CompleteDTime + 90 INNER JOIN OpBase B2 ON T2.ID = B2.ID WHERE B2.Status = 60 AND T.SerialNo <> 'M000' AND B.ID = {workorderID}"
        redo = SingleCursor.send_query(redo_query)['COUNT(*)']
        ai['REDO'] = redo
        #LASTTECHNICIAN
        last_technician_query = f"SELECT /*+ ORDERED USE_NL(B T T2 B2 W2) USE_HASH(U) */ U.FirstName || ' ' || U.LastName AS LastTechnician FROM OpWorkOrder W INNER JOIN OpBase B ON W.ID = B.ID INNER JOIN OpTicket T ON B.PID = T.ID INNER JOIN OpTicket T2 ON T.SerialNo = T2.SerialNo AND (T2.SerialNo <> 'M000' OR T2.ID = T.ID) INNER JOIN OpBase B2 ON T2.ID = B2.PID INNER JOIN OpWorkOrder W2 ON B2.ID = W2.ID INNER JOIN NSPUsers U ON W2.TechnicianID = U.UserID WHERE W.ID = {workorderID} AND W2.ID <> W.ID AND B2.Status = 60 AND W2.RepairFailCode NOT IN (8, 9, 12, 13, 14, 15) AND W2.FinishDTime IS NOT NULL ORDER BY W2.FinishDTime DESC"
        last_technician = SingleCursor.send_query(last_technician_query)
        if type(last_technician) is str:
            ai['LASTTECHNICIAN'] = None
        else:    
            ai['LASTTECHNICIAN'] = last_technician['LASTTECHNICIAN']
        return ai


    @staticmethod
    def get_redo(workorderID):
        "collect data from different sql queries" 
        #REDO
        redo_query = f"SELECT COUNT(*) FROM OpBase B INNER JOIN OpTicket T ON B.PID = T.ID INNER JOIN OpTicket T2 ON T.SerialNo = T2.SerialNo AND T.IssueDTime > T2.IssueDTime AND T.IssueDTime < T2.CompleteDTime + 90 INNER JOIN OpBase B2 ON T2.ID = B2.ID WHERE B2.Status = 60 AND T.SerialNo <> 'M000' AND B.ID = {workorderID}"
        redo = SingleCursor.send_query(redo_query)['COUNT(*)']
        if type(redo) is str:
            return 0
        else:    
            return redo 


    @staticmethod
    def get_visitcount(workorderID):
        "collect data from different sql queries" 
        #VISITCOUNT
        visitcount_query = f"SELECT COUNT(*) FROM OpBase B INNER JOIN opbase b2 ON b.pid = b2.pid AND b2.optype = 10030000 AND b.ID > b2.ID INNER JOIN OpWorkOrder W ON B2.ID = W.ID WHERE W.RepairFailCode NOT IN (1, 8, 9, 12, 13, 14, 15) AND b.id = {workorderID}"
        visitcount = SingleCursor.send_query(visitcount_query)['COUNT(*)']
        if type(visitcount) is str:
            return 0
        else:    
            return visitcount     

    @staticmethod
    def GetTicket(WorkOrderID):
        "get ticketno from opticket table"
        try:
            b = OpBase.objects.get(id=WorkOrderID).pid
            ticketno = OpTicket.objects.get(id=b).ticketno
            return ticketno
        except:
            return None    

    @staticmethod
    def GetTicketContactLogs(TicketID):
        "get ticket contact logs from opcontactcustomer table"
        print('running GetTicketContactLogs...')
        query = f"select C.ID as ID, C.LOGTYPE AS LogType, C.CONTACTRESULT AS ContactResult, B.OPDTIME AS OpDTime, C.CONTACTLOG AS Content, B.STATUS AS Status from opcontactcustomer C, opbase B, opticket T where B.PID = {TicketID} AND T.ID = B.PID AND B.ID = C.ID order by B.OpDTime asc, B.CreatedOn ASC, B.ID ASC;"
        res = MultipleCursor.send_query(query)
        if type(res) is str:
            print(res)
            return []
        else:
            mres = []
            for c in res:
                xd = {}
                xd['ID'] = c['ID']
                xd['LogType'] = c['LOGTYPE'] 
                xd['ContactResult'] = c['CONTACTRESULT']
                xd['OpDTime'] = c['OPDTIME']
                xd['Content'] = c['CONTENT']
                xd['Status'] = c['STATUS']
                mres.append(xd)
            return mres

    
    @staticmethod
    def GetNotesByTicketID(TicketID):
        "get ticket notes from the table opnote" 
        query = f"select * from opnote n, opbase b where n.ID = b.ID and b.originalpid = {TicketID} order by case when n.ScheduleDTime is null then 1 else 0 end, n.ScheduleDTime asc;"
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['ID'] = x['ID']
                xd['NoteType'] = x['NOTETYPE']
                xd['Content'] = x['NOTE']
                xd['MailTo'] = x['MAILTO']
                xd['OpDTime'] = x['OPDTIME']
                resList.append(xd)
            return resList              

    @staticmethod
    def GetTicketNotes(TicketID):
        "get ticket notes from the function GetNotesByTicketID and modify the NoteList"
        print('running GetTicketNotes...') 
        noteList = WorkOrderAdditionalInfoVO.GetNotesByTicketID(TicketID)
        for note in noteList:
            try:
                user_id = OpBase.objects.get(id=note['ID']).updatedby
                if user_id is None:
                    user_id = OpBase.objects.get(id=note['ID']).createdby
            except Exception as e:
                print(e)
                user_id = 0
            note['FullName'] = getuserinfo(user_id)['FullName']
        return noteList    

    @staticmethod
    def GetTicketDocuments(TicketID, ModelNo):
        "get ticket documents from nspmodeldocs, nspmodeldoc4tickets"
        print('running GetTicketDocuments...')
        query = f"select a.ModelNo as ModelNo, a.DocID as DocID, a.DocType as DocType, a.Versions as Versions, a.Note as Note, cast(b.Status as number(3)) as Status from nspmodeldocs a left outer join nspmodeldoc4tickets b on a.ModelNo=b.ModelNo and a.DocID=b.DocID and b.TicketID={TicketID} where a.ModelNo='{ModelNo}' order by b.Status desc;"
        docResult = MultipleCursor.send_query(query) # GetTicketDocFiles
        resList = []
        docList = []
        docList2 = []
        for x in docResult:
            xd = {}
            xd['DocID'] = x['DOCID']
            xd['DocType'] = x['DOCTYPE']
            xd['ModelNo'] = x['MODELNO']
            xd['Versions'] = x['VERSIONS']
            xd['Note'] = x['NOTE']
            xd['Status'] = x['STATUS']
            docfile = WorkOrderAdditionalInfoVO.GetDocument(x['DOCID'])
            if bool(docfile) is False:
                xd['URL'] = None
                xd['FileSize'] = None 
            else:
                xd['FILENAME'] = docfile['FILENAME']
                xd['EXT'] = docfile['EXT']
                if xd.get('FILENAME') and xd.get('EXT'):
                    try:
                        xd['URL'] = '/' + str(xd.get('FILENAME')) + '.' + str(xd.get('EXT'))
                        uploaded_file_path = settings.MEDIA_ROOT+'/reports'+xd['URL']
                        xd['FileSize'] = os.path.getsize(uploaded_file_path) 
                    except Exception as e:
                        print(e)
                else:
                    xd['URL'] = None
                    xd['FileSize'] = None        
            docList.append(xd)    
        docFiles = WorkOrderAdditionalInfoVO.GetTicketDocs(TicketID) 
        if bool(docFiles) is False:
            pass
        else:
            for d in docFiles:
                doc = {}
                doc['DOCID'] = d['DOCID']
                doc['FILENAME'] = d['FILENAME']
                doc['EXT'] = d['EXT']
                doc['DOCTYPE'] = "REFERENCE"
                if d.get('FILENAME') and d.get('EXT'):
                    try:
                        doc['URL'] = '/' + str(d.get('FILENAME')) + '.' + str(d.get('EXT'))
                        uploaded_file_path = settings.MEDIA_ROOT+'/reports'+doc['URL']
                        doc['FileSize'] = os.path.getsize(uploaded_file_path) 
                    except Exception as e:
                        print(e)
                else:
                    doc['URL'] = None
                    doc['FileSize'] = None        
                docList2.append(doc)        
        resList = docList + docList2
        return resList      


    @staticmethod
    def GetDocument(DOCID):
        "fetch document filename and extension from table DocFiles"
        try:
            query = DocFiles.objects.using('docdb').get(docid=DOCID)
            res = {}
            res['DOCID'] = query.docid
            res['FILENAME'] = query.filename
            res['EXT'] = query.ext
            res['OCR'] = query.ocr
            return res
        except:    
            return {}

    @staticmethod
    def GetDocuments(docIds):
        "fetch document filename and extension from table DocFiles"
        docs = []
        for x in docIds:
            try:
                query = DocFiles.objects.using('docdb').get(docid=x['DOCID'])
                res = {}
                res['DOCID'] = query.docid
                res['FILENAME'] = query.filename
                res['EXT'] = query.ext
                res['OCR'] = query.ocr
                docs += [res] 
            except:
                pass
        return docs   

    @staticmethod
    def GetTicketDocs(TicketID):
        "to get ticket docs"
        query = f"select * from nspdocs where opticketid = {TicketID} and DocType='REFERENCE DOCUMENT' order by CreatedOn asc;"
        res = MultipleCursor.send_query(query)
        docIds = []
        for x in res:
            docIds += [x['DOCID']] 
        return WorkOrderAdditionalInfoVO.GetDocuments(docIds)

    @staticmethod
    def GetTicketPictures(TicketID):
        "get pictures based on ticketID from pictures table"
        print('running GetTicketPictures...')
        try:
            ticketno = OpTicket.objects.get(id=TicketID).ticketno
        except:
            ticketno = 0     
        pics = Pictures.objects.using('docdb').filter(Q(refcd=str(TicketID)) | Q(refcd=str(ticketno))).values('pictureid','createdon','createdby','updatedon','updatedby','tablename','filterstr','fieldname','ext','keyword','description','refcd').order_by('-pictureid')
        res = []
        for x in pics:
            pdict = {}
            pdict['PictureID'] = x['pictureid']
            pdict['CreatedOn'] = x['createdon']
            pdict['CreatedBy'] = x['createdby']
            pdict['UpdatedOn'] = x['updatedon']
            pdict['UpdatedBy'] = x['updatedby']
            pdict['TableName'] = x['tablename']
            pdict['FilterStr'] = x['filterstr']
            pdict['FieldName'] = x['fieldname']
            pdict['EXT'] = x['ext']
            pdict['KeyWord'] =x['keyword']
            pdict['Description'] = x['description']
            pdict['RefCD'] = x['refcd']
            pdict['URL'] = '/' + str(pdict['PictureID']) + '.' + str(pdict['EXT'])
            uploaded_file_path = settings.MEDIA_ROOT+'/pictures'+pdict['URL']
            pdict['FileSize'] = os.path.getsize(uploaded_file_path)
            res.append(pdict)
        return res
            

    @staticmethod
    def GetLastAttentionCode(SerialNo):
        "get last attention code from opticket table" 
        if SerialNo is not None or SerialNo!='' or SerialNo!='M000': 
            query = f"select ATTENTIONCODE from opticket where SERIALNO = '{SerialNo}' AND ATTENTIONCODE = {AttentionCode.NO_ISSUE.value} AND ATTENTIONCODE is not null order by ID desc;" 
            res = MultipleCursor.send_query(query)
            if type(res) is str:
                return AttentionCode.NO_ISSUE.value
            else:
                if len(res) > 0:
                    return res[0]['ATTENTIONCODE']
                else:    
                    return AttentionCode.NO_ISSUE.value     
        else:
            return AttentionCode.NO_ISSUE.value


    @staticmethod
    def GetSBDefectCode(ModelNo, token):
        "to get Samsung Defect codes by sending an XML request to the remote KW server" 
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL    

        xml_document = f"""<?xml version="1.0" encoding="utf-8"?>
                            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body><GetSBDefectCode xmlns="http://office.kwinternational.com/"><sToken>{token}</sToken><modelNo>{ModelNo}</modelNo></GetSBDefectCode></soap:Body>
                            </soap:Envelope>
                        """

        encoded_request = xml_document.encode('utf-8')

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": "\"http://office.kwinternational.com/GetSBDefectCode\""}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)

        result = response.content
        SimpleLogger.do_log(f"result = {result}")
        return result                               

    @staticmethod
    def GetSBRepairCode(ModelNo, token):
        "to get Samsung Repair codes by sending an XML request to the remote KW server"
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL    

        xml_document = f"""<?xml version="1.0" encoding="utf-8"?>
                            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body><GetSBRepairCode xmlns="http://office.kwinternational.com/"><sToken>{token}</sToken><modelNo>{ModelNo}</modelNo></GetSBRepairCode></soap:Body>
                            </soap:Envelope>
                        """

        encoded_request = xml_document.encode('utf-8')

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": "\"http://office.kwinternational.com/GetSBRepairCode\""}

        response = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)

        result = response.content
        SimpleLogger.do_log(f"result = {result}")
        return result       

               

    @staticmethod
    def GetDefectCodeList(ModelNo, SystemID, CurrentUserID, token):
        "fetch required list of DEFECT CODE data from the table nspdefectcode or from table NspSamsungDefectCodes or from Samsung GSPN based on different conditions"
        SimpleLogger.do_log(">>> Get()...")
        print("running GetDefectCodeList....")
        if ModelNo is None or not ModelNo:
            print("ModelNo not available")
            query = NspDefectCode.objects.all() #Get all Defect Codes
            dataList = []
            for dc in query:
                xd = {}
                xd['Code'] = dc.code
                xd['Description'] = dc.description
                xd['CodeGroup'] = ''
                xd['CodeGroupName'] = ''
                dataList.append(xd)
            dataList = [i for n, i in enumerate(dataList) if i not in dataList[n + 1:]] #removing duplicate dicts       
            return dataList

        else:
            dataList = []

            try:
                samsungdefectcode = NspSamsungDefectCodes.objects.filter(modelno=ModelNo)[0]
            except:
                samsungdefectcode = None    

            if samsungdefectcode is not None:
                print("samsungdefectcode not none")
                if samsungdefectcode.updatedon is None or samsungdefectcode.updatedon=='':
                    delta = datetime.now().date() - samsungdefectcode.createdon
                    total_days = delta.days
                else:
                    delta = datetime.now().date() - samsungdefectcode.updatedon
                    total_days = delta.days
            
            if SystemID==SystemIDEnum.SVC_BNCH.value or SystemID==SystemIDEnum.SVC_PWR.value:
                print("getting xmlData from office.kwinternational.com")
                xmlData = WorkOrderAdditionalInfoVO.GetSBDefectCode(ModelNo, token)
                SimpleLogger.do_log(f"xml.InnerText = {xmlData}")

            else:   

                if samsungdefectcode is None:
                    print("samsungdefectcode is none")
                    xmlData = GspnWebServiceClient.GetDefectCodeListByModelNo(ModelNo, CurrentUserID)
                    SimpleLogger.do_log(f"xmlData.Length = {len(xmlData)}")
                    #analysing the XML document returned from the service GspnWebServiceClient 
                    retcode = get_xml_node(xmlData, 'RetCode')
                    SimpleLogger.do_log(f"retCode = {retcode}") 

                    if retcode is not None and retcode!='':
                        if int(retcode)==0:
                            if get_xml_node_count(xmlData, '//ROW') < 1000:
                                NspSamsungDefectCodes.objects.create(createdon=datetime.today(), createdby=CurrentUserID, modelno=ModelNo, codedata=xmlData)
                                SimpleLogger.do_log(f"Samsung defect code saved: {ModelNo}")
                     
                elif total_days >= 14:
                    print("it is above or equal to 14")
                    xmlData = GspnWebServiceClient.GetDefectCodeListByModelNo(ModelNo, CurrentUserID)
                    SimpleLogger.do_log(f"xmlData.Length = {len(xmlData)}")
                    #analysing the XML document returned from the service GspnWebServiceClient 
                    retcode = get_xml_node(xmlData, 'RetCode')
                    SimpleLogger.do_log(f"retCode = {retcode}") 

                    if retcode is not None and retcode!='':
                        if int(retcode)==0:
                            if get_xml_node_count(xmlData, '//ROW') < 1000:
                                NspSamsungDefectCodes.objects.filter(modelno=ModelNo).update(updatedon=datetime.today(), updatedby=CurrentUserID, codedata=xmlData)
                                SimpleLogger.do_log(f"Samsung defect code saved: {ModelNo}")

                else:
                    print("else get xmlData from the table")
                    xmlData = samsungdefectcode.codedata                

            #defining some list objects containing strings
            DO_NOT_USE = ["APPR", "OTHR", "HXX", "U0H", "U1B", "U1V"]
            DO_NOT_USE_GROUP = ["OTHER" ]
            NEED_IN_OTHER = ["HF6", "HFC", "HFD", "HFE"]
            #creating list of dict of defect codes from xml nodes
            xml_dict = xmltodict.parse(xmlData, dict_constructor=dict)
            try:
                xml_list = xml_dict['rootdoc']['Table']['ROW']
            except:
                xml_list = []    

            for node in xml_list:
                for node in xml_list:
                    DefectCode = {}
                    DefectCode['Code'] = node.get('Code')
                    DefectCode['Description'] = node.get('CodeName')
                    DefectCode['CodeGroup'] = node.get('CodeGroup')
                    DefectCode['CodeGroupName'] = node.get('CodeGroupName')
                    if DefectCode['CodeGroupName']:
                        if DefectCode['CodeGroupName'].upper() in DO_NOT_USE_GROUP:
                            is_code_groupname = True
                        else:
                            is_code_groupname = False
                    else:
                        is_code_groupname = False            
                    if SystemID==SystemIDEnum.SVC_BNCH.value or SystemID==SystemIDEnum.SVC_PWR.value or is_code_groupname is False or DefectCode['Code'] in NEED_IN_OTHER:
                        if DefectCode['Code'] not in DO_NOT_USE:
                            dataList.append(DefectCode)

            dataList = [i for n, i in enumerate(dataList) if i not in dataList[n + 1:]]        
            return dataList                
            

    @staticmethod
    def GetRepairCodeList(ModelNo, SystemID, CurrentUserID, token):
        "to fetch repair codes"
        SimpleLogger.do_log(">>> Get()...") 
        if ModelNo is None or not ModelNo:
            query = NspRepairCode.objects.all().values() #Get all Defect Codes
            dataList = []
            for dc in query:
                xd = {}
                xd['Code'] = dc.code
                xd['Description'] = dc.description
                xd['CodeGroup'] = ''
                xd['CodeGroupName'] = ''
                dataList.append(xd)    
            dataList = [i for n, i in enumerate(dataList) if i not in dataList[n + 1:]]        
            return dataList 
        else:
            dataList = []

            try:
                samsungRepairCode = NspSamsungRepairCodes.objects.filter(modelno=ModelNo)[0]
            except:
                samsungRepairCode = None

            if samsungRepairCode is not None:
                if samsungRepairCode.updatedon is None or samsungRepairCode.updatedon=='':
                    delta = datetime.now().date() - samsungRepairCode.createdon
                    total_days = delta.days
                else:
                    delta = datetime.now().date() - samsungRepairCode.updatedon
                    total_days = delta.days    

            if SystemID==SystemIDEnum.SVC_BNCH.value or SystemID==SystemIDEnum.SVC_PWR.value:
                xmlData = WorkOrderAdditionalInfoVO.GetSBRepairCode(ModelNo, token)
                SimpleLogger.do_log(f"xml.InnerText = {xmlData}")

            else:

                if samsungRepairCode is None:
                    xmlData = GspnWebServiceClient.GetRepairCodeListByModelNo(ModelNo, CurrentUserID)
                    SimpleLogger.do_log(f"xmlData.Length = {len(xmlData)}")
                    #analysing the XML document returned from the service GspnWebServiceClient 
                    retcode = get_xml_node(xmlData, 'RetCode')
                    SimpleLogger.do_log(f"retCode = {retcode}") 

                    if retcode is not None and retcode!='':
                        if int(retcode)==0:
                            if get_xml_node_count(xmlData, '//ROW') < 1000:
                                NspSamsungRepairCodes.objects.create(createdon=datetime.today(), createdby=CurrentUserID, modelno=ModelNo, codedata=xmlData)
                                SimpleLogger.do_log(f"Samsung repair code saved: {ModelNo}") 

                elif total_days >= 14:
                    print('runing total_days option')
                    xmlData = GspnWebServiceClient.GetRepairCodeListByModelNo(ModelNo, CurrentUserID)
                    SimpleLogger.do_log(f"xmlData.Length = {len(xmlData)}")
                    #analysing the XML document returned from the service GspnWebServiceClient 
                    retcode = get_xml_node(xmlData, 'RetCode')
                    SimpleLogger.do_log(f"retCode = {retcode}") 

                    if retcode is not None and retcode!='':
                        if int(retcode)==0:
                            if get_xml_node_count(xmlData, '//ROW') < 1000:
                                NspSamsungRepairCodes.objects.filter(modelno=ModelNo).update(updatedon=datetime.today(), updatedby=CurrentUserID, codedata=xmlData)
                                SimpleLogger.do_log(f"Samsung repair code saved: {ModelNo}")

                else:

                    xmlData = samsungRepairCode.codedata 

            #defining some list objects containing strings
            DO_NOT_USE = ["98", "OTHR", "CT05", "MISC"]
            DO_NOT_USE_GROUP = ["OTHER" ]
            #creating list of dict of defect codes from xml nodes
            xml_dict = xmltodict.parse(xmlData, dict_constructor=dict)
            try:
                xml_list = xml_dict['rootdoc']['Table']['ROW']
            except:
                xml_list = []
            for node in xml_list:
                for node in xml_list:
                    repairCode = {}
                    repairCode['Code'] = node.get('Code')
                    repairCode['Description'] = node.get('CodeName')
                    repairCode['CodeGroup'] = node.get('CodeGroup')
                    repairCode['CodeGroupName'] = node.get('CodeGroupName')
                    if repairCode['CodeGroupName']:
                        if repairCode['CodeGroupName'].upper() in DO_NOT_USE_GROUP:
                            is_code_groupname = True
                        else:
                            is_code_groupname = False
                    else:
                        is_code_groupname = False            
                    if SystemID==SystemIDEnum.SVC_BNCH.value or SystemID==SystemIDEnum.SVC_PWR.value or is_code_groupname is False:
                        if repairCode['Code'] not in DO_NOT_USE:
                            dataList.append(repairCode)
            dataList = [i for n, i in enumerate(dataList) if i not in dataList[n + 1:]]        
            return dataList

    @staticmethod
    def GetDefectCodeDescription(DefectCodeList, DefectCode):
        "to get defect code description based on DefectCodeList and DefectCode"
        for x in DefectCodeList:
            if x.get('Code')==DefectCode:
                return x.get('Description')
        return ""

    @staticmethod
    def GetRepairCodeDescription(RepairCodeList, RepairCode):
        "to get defect code description based on DefectCodeList and DefectCode"
        for x in RepairCodeList:
            if x.get('Code')==RepairCode:
                return x.get('Description')
        return ""

    @staticmethod
    def DefectCodeDescription(DefectCode):
        "to get defect code description based on DefectCode only"
        d = NspDefectCode.objects.filter(code=DefectCode)
        if d.exists():
            return d[0].description
        return ""

    @staticmethod
    def RepairCodeDescription(RepairCode):
        "to get defect code description based on RepairCode only"
        d = NspRepairCode.objects.filter(code=RepairCode)
        if d.exists():
            return d[0].description
        return ""

    @staticmethod
    def UpdateWorkOrderSchedule(workOrder, aptStartDTime, aptEndDTime, technician, CurrentUserID):
        "to update work order schedule"
        if workOrder['status'] > WorkOrderStatus.SCHEDULED.value:
            SimpleLogger.do_log(f"Work order cannot be updated: status = {workOrder['status']}", "error")
            return 'updation failed'
        try:    
            ticket = OpTicket.objects.get(id=workOrder['pid'])
            ticketStatus = OpBase.objects.get(pid=ticket.id).status
            if ticketStatus>=TicketStatus.CLOSED.value:
                SimpleLogger.do_log(f"Ticket has already been closed: {ticket.id}", "error")
                return 'updation failed' 
        except:
            pass
        # Saving WorkOrder
        if not technician:
            workOrder['technicianid'] = technician
        if (workOrder['aptstartdtime'] is None and aptStartDTime is not None) or (workOrder['aptstartdtime'].date()!=aptStartDTime.date()):
            workOrder['aptmadedtime'] = datetime.now()
            if CurrentUserID!=0:
                workOrder['aptmadeby'] = CurrentUserID
        if workOrder['status'] < WorkOrderStatus.SCHEDULED.value:
            workOrder['status'] = WorkOrderStatus.SCHEDULED.value
        workOrder['aptstartdtime'] = aptStartDTime
        workOrder['aptenddtime'] = aptEndDTime 
        OpWorkOrder.objects.filter(id=workOrder['id']).update(technicianid=workOrder['technicianid'], aptmadedtime=workOrder['aptmadedtime'], aptmadeby=workOrder['aptmadeby'], aptstartdtime=workOrder['aptstartdtime'], aptenddtime=workOrder['aptenddtime'])
        check_query = OpBase.objects.filter(id=workOrder['id'])
        original_pid_value = None 
        wo_status = workOrder['status']
        if check_query.exists():
            try:
                original_pid_value = OpTicket.objects.get(id=check_query[0].pid).id
            except:
                original_pid_value = None
            if check_query[0].createdon is None:
                check_query.update(createdon=datetime.now(), createdby=CurrentUserID, status=wo_status, originalpid=original_pid_value)
            else:
                check_query.update(updatedon=datetime.now(), updatedby=CurrentUserID, status=wo_status)
        # Saving WorkOrderAudit
        audit_id = DBIDGENERATOR.process_id('OpWorkOrderAudit_SEQ')
        try:
            w = OpWorkOrder.objects.get(id=workOrder['id']) #getting the updated workorder record
            OpWorkOrderAudit.objects.create(auditid=audit_id, method='POST', type="U", id=w.id, auditdtime=datetime.now(), auditee=CurrentUserID, workorderno=w.workorderno, aptstartdtime=w.aptstartdtime, aptenddtime=w.aptenddtime, startdtime=w.startdtime, finishdtime=w.finishdtime, contactid=w.contactid, technicianid=w.technicianid, techniciannote=w.techniciannote, triagenote=w.triagenote, triage=w.triage, defectcode=w.defectcode,repaircode=w.repaircode, odometer=w.odometer, note=w.note, repairaction=w.repairaction, defectsymptom=w.defectsymptom, partcost=w.partcost, laborcost=w.laborcost,othercost=w.othercost, salestax=w.salestax, checklist1=w.checklist1, checklist2=w.checklist2, checklist3=w.checklist3, checklist4=w.checklist4, ispartinfoclear=w.ispartinfoclear, warrantystatus=w.warrantystatus, signaturedocid=w.signaturedocid, smallsignaturedocid=w.smallsignaturedocid, signedname=w.signedname, finalworkorderdocid=w.finalworkorderdocid, repairresultcode=w.repairresultcode, repairfailcode=w.repairfailcode, paymenttype=w.paymenttype, diagnosedby=w.diagnosedby, diagnosedtime=w.diagnosedtime, partorderby=w.partorderby, partorderdtime=w.partorderdtime, aptmadeby=w.aptmadeby, aptmadedtime=w.aptmadedtime, quoteby=w.quoteby, quotedtime=w.quotedtime, extraman=w.extraman, seallevel=w.seallevel, seq=w.seq, partwarehouseid=w.partwarehouseid, sqbox=w.sqbox, reservecomplete=w.reservecomplete, ispartordered=w.ispartordered, paymenttransactionid=w.paymenttransactionid, status=wo_status, pid=original_pid_value) 
        except Exception as e:
            #send an email if updation/save failed 
            print(e)   
            email_title = f"[SQ_API]WorkOrderAudit : AuditID {audit_id}, POST" 
            email_content = f"WorkOrder: {str(workOrder['id'])} \n {e}"
            TO_ADDRESS = settings.NSC_ADMIN_EMAIL
            FROM_ADDRESS = settings.NSP_INFO_EMAIL
            sendmailoversmtp(TO_ADDRESS, email_title, email_content, FROM_ADDRESS)
        if WorkOrderStatus(int(wo_status)).name=='CLOSED':
            OpTicket.objects.filter(id=workOrder['id']).update(lastworepairresult=workOrder['repairresultcode'])
        SimpleLogger.do_log(f"Work order saved: {workOrder['id']}")
        # Saving Ticket
        try:
            OpTicket.objects.filter(id=workOrder['pid']).update(aptstartdtime=workOrder['aptstartdtime'],aptenddtime=workOrder['aptenddtime'],techid=technician)
            OpBase.objects.filter(id=workOrder['id']).update(status=TicketStatus.IN_REPAIR.value)
            SimpleLogger.do_log(f"Ticket Saved : {str(workOrder['pid'])}")
        except Exception as e:
            print(f'Error in updating Opticket : {str(e)}')
            SimpleLogger.do_log(f"Ticket Save Error : {str(e)}")
        #creating new record in OPTicketAudit table
        ticket_audit_id = DBIDGENERATOR.process_id('OpTicketAudit_SEQ') 
        try:
            op = OpBase.objects.get(id=workOrder['id'])
            t = OpTicket.objects.get(id=op.pid)
            OpTicketAudit.objects.create(auditid=ticket_audit_id, type='U', method='POST', id=t.id, status=op.status,systemid=t.systemid,modelno=t.modelno,serialno=t.serialno,attentioncode=t.attentioncode,alertmessage=t.alertmessage,gspntechnicianid=t.gspntechnicianid,ticketno=t.ticketno,issuedtime=t.issuedtime,assigndtime=t.assigndtime,contactscheduledtime=t.contactscheduledtime,aptstartdtime=t.aptstartdtime,aptenddtime=t.aptenddtime,completedtime=t.completedtime,contactid=t.contactid,contactid2=t.contactid2,brand=t.brand,cancelreason=t.cancelreason,purchasedate=t.purchasedate,purchasedate2=t.purchasedate2,redoticketno=t.redoticketno,redoreason=t.redoreason,delayreason=t.delayreason,acknowledgedtime=t.acknowledgedtime,gspnstatus=t.gspnstatus,warehouseid=t.warehouseid,lastworepairresult=t.lastworepairresult,version=t.version,producttype=t.producttype,angerindex=t.angerindex,timezone=t.timezone,dst=t.dst,warrantystatus=t.warrantystatus,partwterm=t.partwterm,laborwterm=t.laborwterm,nspdelayreason=t.nspdelayreason,latitude=t.latitude,longitude=t.longitude,flag=t.flag,ascnumber=t.ascnumber,manufacturemonth=t.manufacturemonth,qosocsscore=t.qosocsscore,wtyexception=t.wtyexception,issueopendtime=t.issueopendtime,issueclosedtime=t.issueclosedtime,issuenoteid=t.issuenoteid,issuelatestid=t.issuelatestid,issuestatus=t.issuestatus,servicetype=t.servicetype,nspstatus=t.nspstatus,nspstatusdtime=t.nspstatusdtime,productcategory=t.productcategory,socount=t.socount,repeatcount=t.repeatcount,techid=t.techid,happycallfollowupdtime=t.happycallfollowupdtime,riskindex=t.riskindex,urgent=t.urgent,accountno=t.accountno,dplus1=t.dplus1,requestapptdtime=t.requestapptdtime,callfiredtime=t.callfiredtime,firstcontactdtime=t.firstcontactdtime,callfirestatus=t.callfirestatus,dontcheckcall=t.dontcheckcall,followupcheckcall=t.followupcheckcall,replacemodelno=t.replacemodelno,replaceserialno=t.replaceserialno,returntrackingno=t.returntrackingno,deliverytrackingno=t.deliverytrackingno,nscaccountno=t.nscaccountno,smsconsent=t.smsconsent)
            OpBase.objects.filter(id=workOrder['id']).update(updatedon=datetime.now(), updatedby=CurrentUserID)
        except Exception as e:
            print(e)
            #send an email
            email_title = f"[SQ_API]TicketAudit : AuditID {ticket_audit_id}, POST" 
            email_content = f"TicketDetails: {t} \n {e}"
            to_address = settings.NSC_ADMIN_EMAIL
            from_address = settings.NSP_INFO_EMAIL
            sendmailoversmtp(to_address, email_title, email_content, from_address)                    
                                                                                                            
                             
            


                            

               

 
           

                                                     

 
