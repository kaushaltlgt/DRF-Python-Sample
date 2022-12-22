#contains supporting functions
import datetime
from django.core.serializers.json import DjangoJSONEncoder
import decimal
from django.utils.timezone import is_aware
from functions.querymethods import MultipleCursor
from nsp_user.models import Nspusers
from schedules_detail.support import TicketSupport
from schedules_list_map.support import ContactSupport
from schedules_list_map.schedules import WorkOrderAdditionalInfoVO

class NSPSupport:
    def __init__(self) -> None:
        pass

    @staticmethod
    def IsWorkOrderUpdatedByOtherUser(CurrentUserID, TechID, LastSyncDTime, WorkOrders):
        "to check if work order is updated"
        updatedBy = CurrentUserID
        LastSyncDTime = f"TO_DATE('{LastSyncDTime.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')"
        query = f"SELECT W.ID FROM OpWorkOrder W INNER JOIN OpBase B ON W.ID = B.ID WHERE NVL(B.UpdatedOn, B.CreatedOn) >= {LastSyncDTime} AND NVL(W.StartDTime, W.AptStartDTime) >= TRUNC(CURRENT_DATE) AND NVL(W.StartDTime, W.AptStartDTime) < TRUNC(CURRENT_DATE) + 1 AND (W.TechnicianID = {TechID} OR W.ID IN ({WorkOrders})) AND (B.UpdatedBy <> {updatedBy} OR W.ID NOT IN ({WorkOrders})) UNION ALL ( SELECT T.ID FROM OpTicket T INNER JOIN OpBase B ON T.ID = B.ID INNER JOIN OpBase WB ON B.ID = WB.PID AND B.OpType = 10030000 WHERE NVL(B.UpdatedOn, B.CreatedOn) >= {LastSyncDTime} AND B.UpdatedBy <> {updatedBy} AND WB.ID IN ({WorkOrders})) UNION ALL (SELECT PartDetailID FROM NSPPartDetails WHERE OpWorkOrderID IN ({WorkOrders}) AND NVL(UpdatedBy, CreatedBy) <> {updatedBy} AND NVL(UpdatedOn, CreatedOn) > {LastSyncDTime} );"
        res = MultipleCursor.send_query(query)
        if type(res) is str: #if any error
            return False
        elif len(res) > 0:
            return True
        else:
            return False

    @staticmethod
    def UpdateNSPUserLocation(userId, latitude, longitude, CurrentUserID):
        "to update user location by using the model Nspusers"
        try:
            Nspusers.objects.filter(userid=userId).update(latitude=latitude, longitude=longitude, updatedby=CurrentUserID, updatedon=datetime.datetime.now())
            return True
        except Exception as e:
            return str(e)


    @staticmethod
    def GetNSPUserByUserID(userid):
        "to get details of a nsp user by userid"
        try:
            ns = Nspusers.objects.get(userid=userid)
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
            return resultList
        except:
            return None

    @staticmethod
    def GetNSPUserByUserName(userName):
        "to get details of a nsp user by username"
        try:
            ns = Nspusers.objects.filter(email__startswith=userName+'@')[0]
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
            return resultList
        except:
            return None


    @staticmethod
    def GetTechnicianCurrentTickets(technicianId):
        "to get details based on current tickets and userID"
        ticketList = TicketSupport.GetCurrentTicketsByTechnician(technicianId) 
        for ticket in ticketList:
            ticket['WorkOrders'] = ContactSupport.GetTicketWorkOrders(ticket['ID'])
            ticket['ContactLogs'] = WorkOrderAdditionalInfoVO.GetTicketContactLogs(ticket['ID']) 
            ticket['Notes'] = WorkOrderAdditionalInfoVO.GetTicketNotes(ticket['ID'])
            ticket['Documents'] = WorkOrderAdditionalInfoVO.GetTicketDocuments(ticket['ID'], ticket['ModelNo'])
            ticket['Pictures'] = WorkOrderAdditionalInfoVO.GetTicketPictures(ticket['ID'])                                               
        return ticketList


class DjangoOverRideJSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
            #   r = r[:-6] + 'Z'
                r = r[:-6]
            return r.replace('T', ' ')
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoOverRideJSONEncoder, self).default(o)        