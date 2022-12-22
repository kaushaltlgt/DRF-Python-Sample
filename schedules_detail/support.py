#supporting functions
import datetime
from django.conf import settings
from functions.smtpgateway import sendmailoversmtp
from schedules_detail.models import NspPartSerials, NspPartSerialsAudit, NspCompanyContacts, NspAddresses
from schedules_detail.schedules2 import PictureTrans
from nsp_user.models import getuserinfo, getboolvalue, getfloatvalue
from schedules_list_map.models import OpWorkOrder, OpBase
from functions.querymethods import MultipleCursor, SingleCursor

class PartSupport:
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetPartSerial(psid):
        "to get data from the table NSPPARTSERIALS based on psid"
        try:
            ps = NspPartSerials.objects.get(psid=psid)
            result = {}
            result['PSID'] = psid
            result['PartNo'] = ps.partno
            result['AccountNo'] = ps.accountno
            result['WarehouseID'] = ps.warehouseid
            result['DONo'] = ps.dono
            result['InDate'] = ps.indate
            try:
                result['Value'] = float(ps.value)
            except:
                result['Value'] = ps.value
            try:                                  
                result['CoreValue'] = float(ps.corevalue)
            except:
                result['CoreValue'] = ps.corevalue    
            result['LocationCode'] = ps.locationcode
            result['ToLocationCode'] = ps.tolocationcode
            result['RANo'] = ps.rano
            result['CoreRANo'] = ps.corerano
            result['OutDate'] = ps.outdate
            result['OutType'] = ps.outtype
            result['OutTrackingNo'] = ps.outtrackingno
            result['PONo'] = ps.pono
            result['WorkOrderID'] = ps.workorderid
            result['ItemNo'] = ps.itemno
            result['RAReason'] = ps.rareason
            result['RANote'] = ps.ranote
            result['RADTime'] = ps.radtime
            result['TrackingNo'] = ps.trackingno
            result['ShipDate'] = ps.shipdate
            result['DeliveredDate'] = ps.delivereddate
            result['CreditDate'] = ps.creditdate
            result['RAStatus'] = ps.rastatus
            result['Status'] = ps.status
            result['RADONo'] = ps.radono
            result['RAAccountNo'] = ps.raaccountno
            result['SurveyDTime'] = ps.surveydtime
            result['SurveyBy'] = ps.surveyby
            result['IsOFS'] = ps.isofs
            result['SurveyLocationCode'] = ps.surveylocationcode
            result['JobDetailID'] = ps.jobdetailid
            result['ToWarehouseID'] = ps.towarehouseid
            result['BillDocNo'] = ps.billdocno
            result['CreatedOn'] = ps.createdon
            result['CreatedBy'] = ps.createdby
            result['UpdatedOn'] = ps.updatedon
            result['UpdatedBy'] = ps.updatedby
            if ps.updatedby is not None:
                result['LogBy'] = ps.updatedby
            else:
                result['LogBy'] = ps.createdby    
            result['LogByName'] = None
            for key, value in result.items():
                if value=="":
                    result[key] = None
            return result
        except:
            return None

    @staticmethod
    def GetPartSerialList(warehouseId, locationCode, partNo, pageNo, pageSize):
        "to get list of partserials by running a SQL query"
        SetFirstResult = (pageNo - 1) * pageSize
        SetMaxResults = pageSize
        query = f"select * from NspPartSerials a, NspLocations b where a.WarehouseID='{warehouseId}' and a.LocationCode=b.LocationCode and b.WarehouseID='{warehouseId}' "
        if locationCode:
            query = query + f"and a.LocationCode='{locationCode}' " 
        if partNo:
            query = query + f"and a.PartNo='{partNo}' and b.Restricted=0 "
        query = query + f"and a.OutDate is null order by a.LocationCode, a.PartNo, a.PSID OFFSET {SetFirstResult} ROWS FETCH NEXT {SetMaxResults} ROWS ONLY;"
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for ps in res:
                result = {}
                result['PSID'] = ps['PSID']
                result['PartNo'] = ps['PARTNO']
                result['AccountNo'] = ps['ACCOUNTNO']
                result['WarehouseID'] = ps['WAREHOUSEID']
                result['DONo'] = ps['DONO']
                result['InDate'] = ps['INDATE']
                try:
                    result['Value'] = float(ps['VALUE'])
                except:
                    result['Value'] = ps['VALUE']
                try:                                  
                    result['CoreValue'] = float(ps['COREVALUE'])
                except:
                    result['CoreValue'] = ps['COREVALUE']   
                result['LocationCode'] = ps['LOCATIONCODE']
                result['ToLocationCode'] = ps['TOLOCATIONCODE']
                result['RANo'] = ps['RANO']
                result['CoreRANo'] = ps['CORERANO']
                result['OutDate'] = ps['OUTDATE']
                result['OutType'] = ps['OUTTYPE']
                result['OutTrackingNo'] = ps['OUTTRACKINGNO']
                result['PONo'] = ps['PONO']
                result['WorkOrderID'] = ps['WORKORDERID']
                result['ItemNo'] = ps['ITEMNO']
                result['RAReason'] = ps['RAREASON']
                result['RANote'] = ps['RANOTE']
                result['RADTime'] = ps['RADTIME']
                result['TrackingNo'] = ps['TRACKINGNO']
                result['ShipDate'] = ps['SHIPDATE']
                result['DeliveredDate'] = ps['DELIVEREDDATE']
                result['CreditDate'] = ps['CREDITDATE']
                result['RAStatus'] = ps['RASTATUS']
                result['Status'] = ps['STATUS']
                result['RADONo'] = ps['RADONO']
                result['RAAccountNo'] = ps['RAACCOUNTNO']
                result['SurveyDTime'] = ps['SURVEYDTIME']
                result['SurveyBy'] = ps['SURVEYBY']
                result['IsOFS'] = ps['ISOFS']
                result['SurveyLocationCode'] = ps['SURVEYLOCATIONCODE']
                result['JobDetailID'] = ps['JOBDETAILID']
                result['ToWarehouseID'] = ps['TOWAREHOUSEID']
                result['BillDocNo'] = ps['BILLDOCNO']
                result['CreatedOn'] = ps['CREATEDON']
                result['CreatedBy'] = ps['CREATEDBY']
                result['UpdatedOn'] = ps['UPDATEDON']
                result['UpdatedBy'] = ps['UPDATEDBY']
                if ps['UPDATEDBY'] is not None:
                    result['LogBy'] = ps['UPDATEDBY']
                else:
                    result['LogBy'] = ps['CREATEDBY']    
                result['LogByName'] = None
                for key, value in result.items():
                    if value=="":
                        result[key] = None
                resList.append(result)
            return resList

    @staticmethod
    def SavePartSerialAudit(partSerial, CurrentUserID):
        "to create a record in the table NSPPARTSERIALSAUDIT by copying the record from the table NSPPARTSERIALS"
        try:
            ps = NspPartSerials.objects.get(psid=partSerial['PSID'])
            if ps.updatedon is None:
                type_value = 'C'
            else:
                type_value = 'U'    
            NspPartSerialsAudit.objects.create(auditid=partSerial['AuditID'],auditdtime=datetime.datetime.now(),auditee=CurrentUserID,method=partSerial['Method'],psid=ps.psid,createdon=ps.createdon,createdby=ps.createdby,updatedon=ps.updatedon,updatedby=ps.updatedby,partno=ps.partno,accountno=ps.accountno,warehouseid=ps.warehouseid,dono=ps.dono,indate=ps.indate,value=ps.value,corevalue=ps.corevalue,locationcode=ps.locationcode,tolocationcode=ps.tolocationcode,rano=ps.rano,corerano=ps.corerano,outdate=ps.outdate,outtype=ps.outtype,outtrackingno=ps.outtrackingno,pono=ps.pono,workorderid=ps.workorderid,itemno=ps.itemno,rareason=ps.rareason,ranote=ps.ranote,radtime=ps.radtime,trackingno=ps.trackingno,shipdate=ps.shipdate,delivereddate=ps.delivereddate,creditdate=ps.creditdate,rastatus=ps.rastatus,status=ps.status,radono=ps.radono,raaccountno=ps.raaccountno,surveydtime=ps.surveydtime,surveyby=ps.surveyby,isofs=ps.isofs,surveylocationcode=ps.surveylocationcode,jobdetailid=ps.jobdetailid,towarehouseid=ps.towarehouseid,billdocno=ps.billdocno,type=type_value)
        except Exception as e:
            print(e)
            email_title = f"[SQ_API]PartSerialAudit : AuditID {partSerial['AuditID']}, {partSerial['Method']}" 
            email_content = f"partSerial: {str(partSerial)} \n {e}"
            TO_ADDRESS = settings.NSC_ADMIN_EMAIL
            FROM_ADDRESS = settings.NSP_INFO_EMAIL
            sendmailoversmtp(TO_ADDRESS, email_title, email_content, FROM_ADDRESS)


    @staticmethod
    def SavePartSerialPicture(request, partSerial, imageFile):
        "to save picture for part Serials"
        sync = False
        savepicture = PictureTrans
        picture = savepicture.SavePictureNonTransaction(request, 'NSPPartSerials', partSerial['PSID'], imageFile, sync)
        return picture       


class TicketSupport:
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetSimpleWorkOrder(ID):
        "to get few details of a workorder based on ID"
        try:
            wo = OpWorkOrder.objects.get(id=ID)
            result = {}
            result['ID'] = wo.id
            try:
                result['Status'] = OpBase.objects.get(id=wo.id).status 
            except:
                result['Status'] = None
            result['WorkOrderNo'] = wo.workorderno
            result['AptStartDTime'] = wo.aptstartdtime
            result['AptEndDTime'] = wo.aptenddtime
            result['StartDTime'] = wo.startdtime
            result['FinishDTime'] = wo.finishdtime
            result['RepairResultCode'] = wo.repairresultcode
            result['RepairFailCode'] = wo.repairfailcode
            result['Triage'] = wo.triage
            result['ExtraMan'] = wo.extraman
            result['SealLevel'] = wo.seallevel
            result['Seq'] = wo.seq
            result['TechUserID'] = wo.technicianid
            result['TechUserName'] = getuserinfo(wo.technicianid).get('UserName')
            result['TechFullName'] = getuserinfo(wo.technicianid).get('FullName')
            return result
        except Exception as e:
            print(e)
            return None


    @staticmethod
    def GetTechnicianHistory(modelNo, serialNo):
        "to get history of a technician" 
        query = f"select c.UserID as UserID, c.Email as Email, c.FirstName as FirstName, c.LastName as LastName,cast(count(a.ID) as int) as Visit,cast(sum(case when a.RepairResultCode=1 then 1 else 0 end) as int) as Repair,max(a.StartDTime) as LastVisitDTime from OpWorkOrder a, OpTicket b, NSPUsers c, OpBase op where a.ID=op.ID and b.ID = op.PID and a.technicianid=c.UserID and op.Status=60 and b.ModelNo='{modelNo}' and b.SerialNo='{serialNo}' group by c.UserID, c.Email, c.FirstName, c.LastName order by max(a.StartDTime) asc;"
        res = MultipleCursor.send_query(query)
        try:
            resList = []
            for res in res:
                nsx = {}
                nsinfo = getuserinfo(res['USERID'])
                nsx['UserID'] = nsinfo.get('UserID')
                nsx['UserName'] = nsinfo.get('UserName')
                nsx['FullName'] = nsinfo.get('FullName')
                nsx['Visit'] = res['VISIT']
                nsx['Repair'] = res['REPAIR']
                def repair_rate():
                    if nsx['Repair']==0:
                        rr_value = 0
                    else:
                        rr_value = round((nsx['Repair'] * 1000) / nsx['Visit']) / 10
                    return rr_value      
                nsx['RapairRate'] = repair_rate()
                nsx['LastVisitDTime'] = res['LASTVISITDTIME']
                resList.append(nsx)
            return resList
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def GetDispatchNewOrRepairFailedTickets(warehouseId, apptDate):
        "to get a list of dispatched new or repair failed tickets"
        print('running GetDispatchNewOrRepairFailedTickets ...')
        nextDate = apptDate + datetime.timedelta(days=1)
        nextDate = f"TO_DATE('{nextDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        query = f"select b.ID as ID, op.Status as Status, b.TicketNo as TicketNo, b.SystemID as SystemID, b.IssueDTime as IssueDTime, b.AssignDTime as AssignDTime, b.AptStartDTime as AptStartDTime, b.AptEndDTime as AptEndDTime, b.CompleteDTime as CompleteDTime,b.ModelNo as ModelNo, b.SerialNo as SerialNo, b.Brand as Brand, b.Version as Version, b.WarehouseID as WarehouseID,b.ProductType as ProductType, b.TimeZone as TimeZone, b.DST as DST, b.WarrantyStatus as WarrantyStatus,b.LastWORepairResult as LastWORepairResult, b.Latitude as Latitude, b.Longitude as Longitude, b.ServiceType as ServiceType,b.ProductCategory as ProductCategory, b.SOCount as SOCount,c.ContactID as ContactID, c.Name as ContactName, c.Tel as ContactTel, c.Email as ContactEmail, c.Mobile as ContactMobile,d.AddressID as AddressID, d.Address as Addr, d.City as City, d.State as State, d.ZipCode as ZipCode, d.Country as Country,e.UserID as TechUserID, e.Email as TechEmail, e.FirstName as TechFirstName, e.LastName as TechLastName,(select z.Zone from NSPZones z where z.WarehouseID=b.WarehouseID and z.ProductCategory=b.ProductCategory and z.ZipCode=d.ZipCode) as SQZone,0 as LastWorkOrderID from nspcompanyContacts c, nspAddresses d, opTicket b, OpBase op,  nspusers e where b.ContactID = c.ContactID and c.AddressID = d.AddressID and b.ID = op.pid and op.Status < 60 and b.WarehouseID = '{warehouseId}' and b.IssueDTime < {nextDate} and ((select count(x.ID) from OpWorkOrder x where x.ID=op.ID) = 0 or (b.LastWORepairResult=2 and (select count(x.ID) from OpWorkOrder x where x.ID=op.ID and Op.Status < 60) = 0));" 
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {} 
                xd['ID'] = x['ID'] 
                xd['Status'] = x['STATUS']
                xd['TicketNo'] = x['TICKETNO'] 
                xd['SystemID'] = x['SYSTEMID'] 
                xd['IssueDTime'] = x['ISSUEDTIME']
                xd['AssignDTime'] = x['ASSIGNDTIME']
                xd['AptStartDTime'] = x['APTSTARTDTIME']
                xd['AptEndDTime'] = x['APTENDDTIME'] 
                xd['CompleteDTime'] = x['COMPLETEDTIME']
                xd['ModelNo'] = x['MODELNO']
                xd['SerialNo'] = x['SERIALNO'] 
                xd['Brand'] = x['BRAND']
                xd['Version'] = x['VERSION']
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['ProductType'] = x['PRODUCTTYPE']
                xd['TimeZone'] = x['TIMEZONE']
                xd['DST'] = getboolvalue(x['DST'])
                xd['WarrantyStatus'] = x['WARRANTYSTATUS']
                xd['LastWORepairResult'] = x['LASTWOREPAIRRESULT'] 
                xd['Latitude'] = getfloatvalue(x['LATITUDE'])
                xd['Longitude'] = getfloatvalue(x['LONGITUDE']) 
                xd['ServiceType'] = x['SERVICETYPE']
                xd['ProductCategory'] = x['PRODUCTCATEGORY']
                xd['SOCount'] = x['SOCOUNT']
                xd['SQZone'] = x['SQZONE']
                xd['ContactID'] = x['CONTACTID']
                xd['ContactName'] = x['CONTACTNAME']
                xd['ContactTel'] = x['CONTACTTEL']
                xd['ContactEmail'] = x['CONTACTEMAIL']
                xd['ContactMobile'] = x['CONTACTMOBILE']
                xd['AddressID'] = x['ADDRESSID']
                xd['Addr'] = x['ADDR']
                xd['City'] = x['CITY']
                xd['State'] = x['STATE']
                xd['ZipCode'] = x['ZIPCODE']
                xd['Country'] = x['COUNTRY']
                xd['TechUserID'] = x['TECHUSERID']
                xd['TechUserName'] = getuserinfo(x['TECHUSERID']).get('UserName')
                xd['TechFullName'] = getuserinfo(x['TECHUSERID']).get('FullName')
                resList.append(xd)
            return resList 

    @staticmethod
    def GetDispatchMultiRegionTickets(warehouseId, apptDate, techUserIds):
        "to get list of dispatched multi-region tickets"
        print('running GetDispatchMultiRegionTickets ...')
        nextDate = apptDate + datetime.timedelta(days=1)
        nextDate = f"TO_DATE('{nextDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        apptDate = f"TO_DATE('{apptDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        query = f"select b.ID as ID, op.Status as Status, b.TicketNo as TicketNo, b.SystemID as SystemID, b.IssueDTime as IssueDTime, b.AssignDTime as AssignDTime, b.AptStartDTime as AptStartDTime, b.AptEndDTime as AptEndDTime, b.CompleteDTime as CompleteDTime, b.ModelNo as ModelNo, b.SerialNo as SerialNo, b.Brand as Brand, b.Version as Version, b.WarehouseID as WarehouseID, b.ProductType as ProductType, b.TimeZone as TimeZone, b.DST as DST, b.WarrantyStatus as WarrantyStatus, b.LastWORepairResult as LastWORepairResult, b.Latitude as Latitude, b.Longitude as Longitude, b.ServiceType as ServiceType, b.ProductCategory as ProductCategory, b.SOCount as SOCount, c.ContactID as ContactID, c.Name as ContactName, c.Tel as ContactTel, c.Email as ContactEmail, c.Mobile as ContactMobile, d.AddressID as AddressID, d.Address as Address, d.City as City, d.State as State, d.ZipCode as ZipCode, d.Country as Country, e.UserID as TechUserID, e.Email as TechEmail, e.FirstName as TechFirstName, e.LastName as TechLastName, (select z.Zone from NSPZones z where z.WarehouseID=b.WarehouseID and z.ProductCategory=b.ProductCategory and z.ZipCode=d.ZipCode) as SQZone, a.ID as LastWorkOrderID from NSPCOMPANYContacts c, nspaddresses d, opworkorder a, opticket b, opbase op, nspusers e where e.userid = b.techid and b.contactid = c.contactid and c.addressid = d.addressid and a.ID = op.ID and b.ID = op.PID and op.status <= 60 and b.warehouseid != '{warehouseId}' and b.IssueDTime < {nextDate} and a.AptStartDTime >= {apptDate} and a.AptStartDTime < {nextDate}) and e.UserID in ({techUserIds});"
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {} 
                xd['ID'] = x['ID'] 
                xd['Status'] = x['STATUS']
                xd['TicketNo'] = x['TICKETNO'] 
                xd['SystemID'] = x['SYSTEMID'] 
                xd['IssueDTime'] = x['ISSUEDTIME']
                xd['AssignDTime'] = x['ASSIGNDTIME']
                xd['AptStartDTime'] = x['APTSTARTDTIME']
                xd['AptEndDTime'] = x['APTENDDTIME'] 
                xd['CompleteDTime'] = x['COMPLETEDTIME']
                xd['ModelNo'] = x['MODELNO']
                xd['SerialNo'] = x['SERIALNO'] 
                xd['Brand'] = x['BRAND']
                xd['Version'] = x['VERSION']
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['ProductType'] = x['PRODUCTTYPE']
                xd['TimeZone'] = x['TIMEZONE']
                xd['DST'] = getboolvalue(x['DST'])
                xd['WarrantyStatus'] = x['WARRANTYSTATUS']
                xd['LastWORepairResult'] = x['LASTWOREPAIRRESULT'] 
                xd['Latitude'] = getfloatvalue(x['LATITUDE'])
                xd['Longitude'] = getfloatvalue(x['LONGITUDE']) 
                xd['ServiceType'] = x['SERVICETYPE']
                xd['ProductCategory'] = x['PRODUCTCATEGORY']
                xd['SOCount'] = x['SOCOUNT']
                xd['SQZone'] = x['SQZONE']
                xd['ContactID'] = x['CONTACTID']
                xd['ContactName'] = x['CONTACTNAME']
                xd['ContactTel'] = x['CONTACTTEL']
                xd['ContactEmail'] = x['CONTACTEMAIL']
                xd['ContactMobile'] = x['CONTACTMOBILE']
                xd['AddressID'] = x['ADDRESSID']
                xd['Addr'] = x['ADDR']
                xd['City'] = x['CITY']
                xd['State'] = x['STATE']
                xd['ZipCode'] = x['ZIPCODE']
                xd['Country'] = x['COUNTRY']
                xd['TechUserID'] = x['TECHUSERID']
                xd['TechUserName'] = getuserinfo(x['TECHUSERID']).get('UserName')
                xd['TechFullName'] = getuserinfo(x['TECHUSERID']).get('FullName')
                xd['LastWorkOrder'] = TicketSupport.GetSimpleWorkOrder(x['LASTWORKORDERID']) 
                xd['TechnicianHistory'] = TicketSupport.GetTechnicianHistory(x['MODELNO'], x['SERIALNO'])
                resList.append(xd)
            return resList                      
        
                  

    @staticmethod
    def GetDispatchScheduledOrUnscheduledTickets(warehouseId, apptDate):
        "to get list of tickets"
        print('running GetDispatchScheduledOrUnscheduledTickets ...')
        nextDate = apptDate + datetime.timedelta(days=1)
        nextDate = f"TO_DATE('{nextDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        apptDate = f"TO_DATE('{apptDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        query = f"select b.ID as ID, op.Status as Status, b.TicketNo as TicketNo, b.SystemID as SystemID, b.IssueDTime as IssueDTime, b.AssignDTime as AssignDTime, b.AptStartDTime as AptStartDTime, b.AptEndDTime as AptEndDTime, b.CompleteDTime as CompleteDTime, b.ModelNo as ModelNo, b.SerialNo as SerialNo, b.Brand as Brand, b.Version as Version, b.WarehouseID as WarehouseID, b.ProductType as ProductType, b.TimeZone as TimeZone, b.DST as DST, b.WarrantyStatus as WarrantyStatus, b.LastWORepairResult as LastWORepairResult, b.Latitude as Latitude, b.Longitude as Longitude, b.ServiceType as ServiceType, b.ProductCategory as ProductCategory, b.SOCount as SOCount, c.ContactID as ContactID, c.Name as ContactName, c.Tel as ContactTel, c.Email as ContactEmail, c.Mobile as ContactMobile, d.AddressID as AddressID, d.Address as Address, d.City as City, d.State as State, d.ZipCode as ZipCode, d.Country as Country, e.UserID as TechUserID, e.Email as TechEmail, e.FirstName as TechFirstName, e.LastName as TechLastName, (select z.Zone from NSPZones z where z.WarehouseID=b.WarehouseID and z.ProductCategory=b.ProductCategory and z.ZipCode=d.ZipCode) as SQZone, a.ID as LastWorkOrderID from NSPCOMPANYContacts c, nspaddresses d, opworkorder a, opticket b, opbase op, nspusers e where e.userid = b.techid and b.contactid = c.contactid and c.addressid = d.addressid and a.ID = op.ID and b.ID = op.PID and op.status <= 60 and b.warehouseid = '{warehouseId}' and b.IssueDTime < {nextDate} and (( a.AptStartDTime >= {apptDate} and a.AptStartDTime < {nextDate}) or a.AptStartDTime is null);"
        res = MultipleCursor.send_query(query, 10)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['ID'] = x['ID']
                xd['Status'] = x['STATUS']
                xd['TicketNo'] = x['TICKETNO']
                xd['SystemID'] = x['SYSTEMID']
                xd['IssueDTime'] = x['ISSUEDTIME']
                xd['AssignDTime'] = x['ASSIGNDTIME']
                xd['AptStartDTime'] = x['APTSTARTDTIME']
                xd['AptEndDTime'] = x['APTENDDTIME']
                xd['CompleteDTime'] = x['COMPLETEDTIME']
                xd['ModelNo'] = x['MODELNO']
                xd['SerialNo'] = x['SERIALNO']
                xd['Brand'] = x['BRAND']
                xd['Version'] = x['VERSION']
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['ProductType'] = x['PRODUCTTYPE']
                xd['TimeZone'] = x['TIMEZONE']
                xd['DST'] = getboolvalue(x['DST'])
                xd['WarrantyStatus'] = x['WARRANTYSTATUS']
                xd['LastWORepairResult'] = x['LASTWOREPAIRRESULT']
                xd['Latitude'] = getfloatvalue(x['LATITUDE'])
                xd['Longitude'] = getfloatvalue(x['LONGITUDE'])
                xd['ServiceType'] = x['SERVICETYPE']
                xd['ProductCategory'] = x['PRODUCTCATEGORY']
                xd['SOCount'] = x['SOCOUNT']
                xd['SQZone'] = x['SQZONE']
                xd['ContactID'] = x['CONTACTID']
                xd['ContactName'] = x['CONTACTNAME']
                xd['ContactTel'] = x['CONTACTTEL']
                xd['ContactEmail'] = x['CONTACTEMAIL']
                xd['ContactMobile'] = x['CONTACTMOBILE']
                xd['AddressID'] = x['ADDRESSID']
                xd['Addr'] = x['ADDRESS']
                xd['City'] = x['CITY']
                xd['State'] = x['STATE']
                xd['ZipCode'] = x['ZIPCODE']
                xd['Country'] = x['COUNTRY']
                xd['TechUserID'] = x['TECHUSERID']
                xd['TechUserName'] = getuserinfo(x['TECHUSERID']).get('UserName')
                xd['TechFullName'] = getuserinfo(x['TECHUSERID']).get('FullName')
                xd['LastWorkOrderID'] = x['LASTWORKORDERID']
                resList.append(xd)
            return resList


    @staticmethod
    def GetDispatchTickets(warehouseId, apptDate, includeNoWorkOrder, includeMultiRegion):
        "to get a list of dispatched tickets"
        tickets = []
        techUserIds = []
        ticketList = TicketSupport.GetDispatchScheduledOrUnscheduledTickets(warehouseId, apptDate)
        for ticket in ticketList:
            if ticket['LastWorkOrderID'] > 0:
                ticket['LastWorkOrder'] = TicketSupport.GetSimpleWorkOrder(ticket['LastWorkOrderID']) 
                ticket['TechnicianHistory'] = TicketSupport.GetTechnicianHistory(ticket['ModelNo'], ticket['SerialNo'])
            if includeMultiRegion:
                workOrder = ticket['LastWorkOrder']
                if workOrder is not None and workOrder['AptStartDTime'] is not None and workOrder['TechUserID'] > 0 and workOrder['TechUserID'] not in techUserIds:
                    techUserIds.append(ticket['TechUserID'])
            tickets.append(ticket)

        if includeNoWorkOrder:
            ticketList = TicketSupport.GetDispatchNewOrRepairFailedTickets(warehouseId, apptDate)
            for ticket in ticketList:
                tickets.append(ticket)

        if includeMultiRegion and len(techUserIds) > 0:
            ticketList = TicketSupport.GetDispatchMultiRegionTickets(warehouseId, apptDate, techUserIds) 
            for ticket in ticketList:
                if ticket['LastWorkOrderID'] > 0:
                    ticket['LastWorkOrder'] = TicketSupport.GetSimpleWorkOrder(ticket['LastWorkOrderID']) 
                    ticket['TechnicianHistory'] = TicketSupport.GetTechnicianHistory(ticket['ModelNo'], ticket['SerialNo'])
                tickets.append(ticket)
        return tickets 

    @staticmethod
    def GetSimpleTicketByTicketNo(TicketNo):
        "to get simple ticket data based on ticketNo"
        query = f"select b.ID as ID, op.Status as Status, b.TicketNo as TicketNo, b.SystemID as SystemID, b.IssueDTime as IssueDTime, b.AssignDTime as AssignDTime,b.AptStartDTime as AptStartDTime, b.AptEndDTime as AptEndDTime, b.CompleteDTime as CompleteDTime,b.ModelNo as ModelNo, b.SerialNo as SerialNo, b.Brand as Brand, b.Version as Version, b.WarehouseID as WarehouseID,b.ProductType as ProductType, b.TimeZone as TimeZone, b.DST as DST, b.WarrantyStatus as WarrantyStatus,b.LastWORepairResult as LastWORepairResult, b.Latitude as Latitude, b.Longitude as Longitude, b.ServiceType as ServiceType,b.ProductCategory as ProductCategory, b.SOCount as SOCount,c.ContactID as ContactID, c.Name as ContactName, c.Tel as ContactTel, c.Email as ContactEmail, c.Mobile as ContactMobile,d.AddressID as AddressID, d.Address as Addr, d.City as City, d.State as State, d.ZipCode as ZipCode, d.Country as Country,e.UserID as TechUserID, e.Email as TechEmail, e.FirstName as TechFirstName, e.LastName as TechLastName,(select z.Zone from NSPZones z where z.WarehouseID=b.WarehouseID and z.ProductCategory=b.ProductCategory and z.ZipCode=d.ZipCode) as SQZone,(select max(v.ID) from opworkorder v, opbase ob where v.ID = ob.ID and ob.Status <= 60 and ob.PID = b.ID) as LastWorkOrderID from nspcompanyContacts c, nspAddresses d, opTicket b, opbase op, nspusers e where b.ID = op.PID and b.ContactID=c.ContactID and c.AddressID=d.AddressID and b.techid = e.userid and b.TicketNo='{TicketNo}';"
        res = SingleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return None
        else:
            x = res
            xd = {} 
            xd['ID'] = x['ID'] 
            xd['Status'] = x['STATUS']
            xd['TicketNo'] = x['TICKETNO'] 
            xd['SystemID'] = x['SYSTEMID'] 
            xd['IssueDTime'] = x['ISSUEDTIME']
            xd['AssignDTime'] = x['ASSIGNDTIME']
            xd['AptStartDTime'] = x['APTSTARTDTIME']
            xd['AptEndDTime'] = x['APTENDDTIME'] 
            xd['CompleteDTime'] = x['COMPLETEDTIME']
            xd['ModelNo'] = x['MODELNO']
            xd['SerialNo'] = x['SERIALNO'] 
            xd['Brand'] = x['BRAND']
            xd['Version'] = x['VERSION']
            xd['WarehouseID'] = x['WAREHOUSEID']
            xd['ProductType'] = x['PRODUCTTYPE']
            xd['TimeZone'] = x['TIMEZONE']
            xd['DST'] = getboolvalue(x['DST'])
            xd['WarrantyStatus'] = x['WARRANTYSTATUS']
            xd['LastWORepairResult'] = x['LASTWOREPAIRRESULT'] 
            xd['Latitude'] = getfloatvalue(x['LATITUDE'])
            xd['Longitude'] = getfloatvalue(x['LONGITUDE']) 
            xd['ServiceType'] = x['SERVICETYPE']
            xd['ProductCategory'] = x['PRODUCTCATEGORY']
            xd['SOCount'] = x['SOCOUNT']
            xd['SQZone'] = x['SQZONE']
            xd['ContactID'] = x['CONTACTID']
            xd['ContactName'] = x['CONTACTNAME']
            xd['ContactTel'] = x['CONTACTTEL']
            xd['ContactEmail'] = x['CONTACTEMAIL']
            xd['ContactMobile'] = x['CONTACTMOBILE']
            xd['AddressID'] = x['ADDRESSID']
            xd['Addr'] = x['ADDR']
            xd['City'] = x['CITY']
            xd['State'] = x['STATE']
            xd['ZipCode'] = x['ZIPCODE']
            xd['Country'] = x['COUNTRY']
            xd['TechUserID'] = x['TECHUSERID']
            xd['TechUserName'] = getuserinfo(x['TECHUSERID']).get('UserName')
            xd['TechFullName'] = getuserinfo(x['TECHUSERID']).get('FullName')
            xd['LastWorkOrder'] = TicketSupport.GetSimpleWorkOrder(x['LASTWORKORDERID']) 
            xd['TechnicianHistory'] = TicketSupport.GetTechnicianHistory(x['MODELNO'], x['SERIALNO'])
            return xd


    @staticmethod
    def GetCurrentTicketsByTechnician(technicianId):
        "to get current tickets based on technician ID"
        currentTime = f"TO_DATE('{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')"
        query = f"select * from opticket t where t.ID in (select t2.ID from opworkorder w, opbase b, opticket t2 where w.ID = b.ID and t2.ID = b.PID and w.technicianid={technicianId} and (b.status < 60 or w.FinishDTime >= {currentTime})) order by case when t.AptStartDTime is null then 1 else 0 end, t.AptStartDTime asc "
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['ID'] = x['ID']
                xd['TicketNo'] = x['TICKETNO'] 
                xd['IssueDTime'] = x['ISSUEDTIME']
                xd['AssignDTime'] = x['ASSIGNDTIME']
                xd['ContactScheduleDTime'] = x['CONTACTSCHEDULEDTIME']
                xd['AptStartDTime'] = x['APTSTARTDTIME']
                xd['AptEndDTime'] = x['APTENDDTIME']
                xd['CompleteDTime'] = x['COMPLETEDTIME']
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
                    contacts['Address'] = address
                    contacts['Name'] = c.name
                    contacts['Tel'] = c.tel
                    contacts['Fax'] = c.fax
                    contacts['Email'] = c.email
                    contacts['Mobile'] = c.mobile
                xd['Contact'] = contacts
                xd['Brand'] = x['BRAND']
                xd['ModelNo'] = x['MODELNO']
                xd['SerialNo'] = x['SERIALNO']
                xd['CancelReason'] = x['CANCELREASON']
                xd['PurchaseDate'] = x['PURCHASEDATE']
                xd['RedoTicketNo'] = x['REDOTICKETNO']
                xd['RedoReason'] = x['REDOREASON']
                xd['DelayReason'] = x['DELAYREASON']
                xd['AcknowledgeDTime'] = x['ACKNOWLEDGEDTIME']
                xd['GSPNStatus'] = x['GSPNSTATUS']
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['LastWORepairResult'] = x['LASTWOREPAIRRESULT'] 
                xd['Version'] = x['VERSION'] 
                xd['ProductType'] = x['PRODUCTTYPE']
                xd['AngerIndex'] = x['ANGERINDEX']
                xd['TimeZone'] = x['TIMEZONE']
                xd['DST'] = x['DST']
                xd['PartWTerm'] = x['PARTWTERM']
                xd['LaborWTerm'] = x['LABORWTERM']
                xd['NSPDelayReason'] = x['NSPDELAYREASON']
                xd['Latitude'] = x['LATITUDE']
                xd['Longitude'] = x['LONGITUDE'] 
                xd['Flag'] = x['FLAG']
                xd['ASCNumber'] = x['ASCNUMBER']
                xd['ManufactureMonth'] = x['MANUFACTUREMONTH']
                xd['QoSOCSScore'] = x['QOSOCSSCORE']
                xd['IssueOpenDTime'] = x['ISSUEOPENDTIME']
                xd['IssueCloseDTime'] = x['ISSUECLOSEDTIME'] 
                xd['IssueNoteID'] = x['ISSUENOTEID']
                xd['IssueLatestID'] = x['ISSUELATESTID']
                xd['IssueStatus'] = x['ISSUESTATUS']
                xd['NSPStatus'] = x['NSPSTATUS']
                xd['NSPStatusDTime'] = x['NSPSTATUSDTIME']
                xd['ProductCategory'] = x['PRODUCTCATEGORY']
                xd['SOCount'] = x['SOCOUNT']
                xd['RepeatCount'] = x['REPEATCOUNT']
                xd['Technician'] = getuserinfo(x['TECHID'])
                xd['HappyCallFollowUpDTime'] = x['HAPPYCALLFOLLOWUPDTIME']
                xd['RiskIndex'] = x['RISKINDEX']
                xd['Urgent'] = x['URGENT']
                xd['AccountNo'] = x['ACCOUNTNO']
                xd['DPlus1'] = x['DPLUS1']
                xd['RequestApptDTime'] = x['REQUESTAPPTDTIME']
                xd['CallfireDTime'] = x['CALLFIREDTIME'] 
                xd['FirstContactDTime'] = x['FIRSTCONTACTDTIME']
                xd['CallfireStatus'] = x['CALLFIRESTATUS']
                xd['DontCheckCall'] = x['DONTCHECKCALL']
                xd['FollowUpCheckCall'] = x['FOLLOWUPCHECKCALL']
                xd['ReplaceModelNo'] = x['REPLACEMODELNO']
                xd['ReplaceSerialNo'] = x['REPLACESERIALNO']
                xd['ReturnTrackingNo'] = x['RETURNTRACKINGNO']
                xd['DeliveryTrackingNo'] = x['DELIVERYTRACKINGNO']
                xd['NSCAccountNo'] = x['NSCACCOUNTNO']
                xd['SMSConsent'] = x['SMSCONSENT']
                xd['AlertMessage'] = x['ALERTMESSAGE']
                xd['GSPNTechnicianID'] = x['GSPNTECHNICIANID']
                resList.append(xd)
            return resList


class LocationConstants:
    "define constants related to NSP Locations" 
    LOCATION_CODE_RECEIVING = "RECEIVING"
    LOCATION_CODE_RA = "SQ-RA"
    LOCATION_CODE_RA_REJECT = "SQ-REJECT"
    LOCATION_CODE_DEFECT = "SQ-DEFECT"
    LOCATION_CODE_CORE = "SQ-CORE"
    LOCATION_CODE_CORESENT = "SQ-CORESENT"
    LOCATION_CODE_USED = "SQ-USED"
    LOCATION_CODE_B2S = "SQ-B2S"
    LOCATION_CODE_SCRAP = "SQ-SCRAP"
    LOCATION_CODE_LOST = "SQ-LOST"
    LOCATION_CODE_STO = "SQ-STO"
    LOCATION_CODE_PENDING = "SQ-PENDING"               

                                                                                          




