#define soap requests related classes here
import datetime, requests, socket
from xml.etree.ElementTree import XML
from functions.kwlogging import SimpleLogger
from functions.querymethods import DBIDGENERATOR, MultipleCursor, SingleCursor
from django.conf import settings
from django.db.models import Q
from schedules_detail.models import NspLocations, NspWareHouses, NspPartDetails, NspPSMovingHistories, NspPartSerials, NspDoDetails, NspHotParts, NspDos, NspAccounts, NspPartMaster4Warehouses
from schedules_list_map.schedules import OUT_TYPE, STATUS_TYPE, USAGE_TYPE, LOCATION_TYPE, JOB_TYPE, GspnWebServiceClient, RESERVE_STATUS, SYSTEM_ID, NSP_STATUS, NSP_PERMIT_OBJECT, WAREHOUSE_TYPE
from schedules_list_map.models import OpWorkOrder, NspDataLogs, OpTicket, OpBase
from schedules_detail import schedules2
from nsp_user.models import Nspusers, getuserinfo
from repair_tasks.support import JobSupport
from repair_tasks.models import NspJobDetails, NspJobs
from functions.smtpgateway import sendmailoversmtp


class XMLActions:
    "to make a soap action for getting moving parts details"
    def __init__(self) -> None:
        pass

    @staticmethod 
    def move_part(CurrentUserID, psid, warehouseid, newlocationcode, movereason):
        "accept required values for soap request"
        SimpleLogger.do_log("MovePart()...")
        from schedules_detail.support import PartSupport
        from schedules_detail.support import LocationConstants
        xml = {} #returning xml as dict
        ps = PartSupport.GetPartSerial(psid)
        try:
            if ps is not None:
                if newlocationcode==LocationConstants.LOCATION_CODE_USED and ps['CoreValue']!=0:
                    raise Exception(f"PS {psid} has a core value. If this core part was used, Please Move to {LocationConstants.LOCATION_CODE_CORE}.")
                if newlocationcode==LocationConstants.LOCATION_CODE_CORE and ps["CoreValue"]==0:
                    raise Exception(f"PS {psid} has no core value. If this part was used, Please Move to {LocationConstants.LOCATION_CODE_USED}.")
            else:
                raise Exception(f"PS {psid} was not found")
            XMLActions.MovePartByPSID(CurrentUserID, psid, warehouseid, newlocationcode, movereason)
            xml['ErrorMsg'] = "" 
            loc = NspLocations.objects.filter(warehouseid=warehouseid,locationcode=newlocationcode) 
            if loc.exists() and loc[0].locationtype==LOCATION_TYPE.SQBOX.value:
                wo = OpWorkOrder.objects.filter(id=XMLActions.GetWorkOrderIDBySQBox(warehouseid, newlocationcode)['ID'])
                if wo.exists():
                    xml['WorkOrderID'] = wo[0].id
                    xml['ReserveComplete'] = wo[0].reservecomplete
        except Exception as e:
            xml['ErrorMsg'] = str(e)
        return xml    


    @staticmethod
    def MovePartByPSID(CurrentUserID, psid, warehouseid, sNewLocationCode, sMoveReason=""):
        "to move part by PSID" 
        from schedules_detail.support import PartSupport
        from schedules_detail.support import LocationConstants
        ps = PartSupport.GetPartSerial(psid)
        curLoc = NspLocations.objects.filter(warehouseid=ps['WarehouseID'], locationcode=ps['LocationCode'])
        loc = NspLocations.objects.filter(warehouseid=warehouseid, locationcode=sNewLocationCode) 
        jd = {}
        XMLActions.ValidationForMovePartLocation(CurrentUserID, psid, ps['WarehouseID'], ps['LocationCode'], warehouseid, sNewLocationCode)
        frWO = {}
        if ps['WorkOrderID'] > 0:
            sq = schedules2.SchedulesService
            frWO = sq.GetWorkOrder(ps['WorkOrderID'])
            if frWO['Status'] >= STATUS_TYPE.PROCESSING.value:
                frWO = None
        nsp_moving = NspPSMovingHistories.objects.all()[0] 
        moving = {}       
        wh = NspWareHouses.objects.get(warehouseid=warehouseid)
        moving['PSID'] = ps['PSID']
        moving['FromWarehouseID'] = ps['WarehouseID']
        moving['FromLocationCode'] = ps['LocationCode']
        if ps and curLoc.exists() and loc.exists():
            if curLoc[0].locationtype==LOCATION_TYPE.SQBOX.value and loc[0].locationcode==LocationConstants.LOCATION_CODE_PENDING.value:
                ps['LocationCode'] = LocationConstants.LOCATION_CODE_PENDING
                XMLActions.SetPendingStatus(CurrentUserID, ps['WorkOrderID'], True)
            else:
                if ps['ToLocationCode']=="" or ps['ToLocationCode']==sNewLocationCode:
                    if ps['OutDate'] and loc[0].locationtype in [LOCATION_TYPE.STORAGE.value, LOCATION_TYPE.SQBOX.value]:
                        ps['OutType'] = OUT_TYPE.NONE.value
                        ps['OutDate'] = "" 
                        ps["Status"] = STATUS_TYPE.NONE.value
                        if ps['RANo']!="" and ps['RAStatus']=="RR":
                            if ps['Remark']!="":
                                ps['Remark'] += "vbCrLf" 
                            ps['Remark'] += "RR:" + ps['RANo']
                            ps['RANo'] = ""

                            if ps['JobDetailID'] > 0:
                                jd = JobSupport.GetNSPJobDetail(ps['JobDetailID'])
                                if jd['Status'] < STATUS_TYPE.COMPLETED.value:
                                    XMLActions.CancelJobDetailOfPS(CurrentUserID, ps['JobDetailID']) 
                    if ps['RANo'] != "" and ps['RAStatus'] != "RR":
                        raise Exception(f"RA Number ({ps['RANo']}) already exists.  Please check.") 
                    if loc.exists():
                        if loc[0].locationtype==LOCATION_TYPE.SYSTEM.value:
                            if loc[0].locationcode==LocationConstants.LOCATION_CODE_LOST:
                                ps['OutType'] = OUT_TYPE.LOST.value
                                ps['OutDate'] = datetime.datetime.today()
                            if loc[0].locationcode==LocationConstants.LOCATION_CODE_RA or loc[0].locationcode==LocationConstants.LOCATION_CODE_DEFECT:
                                if loc[0].locationcode==LocationConstants.LOCATION_CODE_RA and wh.hotparts:
                                    if not XMLActions.CheckDefective(ps) and XMLActions.IsHotPart(psid, warehouseid):
                                        raise Exception("Frequently used part. Please do not create RA, place back to stock.") 
                                    ps['OutType'] = OUT_TYPE.RA.value
                                    ps['OutDate'] = datetime.datetime.today()
                                    ps['RAReason'] = sMoveReason
                                    ps['Status'] = STATUS_TYPE.RA_READY.value 
                                    if ps['JobDetailID']:
                                        jd = JobSupport.GetNSPJobDetail(ps['JobDetailID'])
                                        if jd['Status'] >= STATUS_TYPE.COMPLETED.value:
                                            jd = None
                            if loc[0].locationcode==LocationConstants.LOCATION_CODE_SCRAP:
                                ps['OutType'] = OUT_TYPE.SCRAP.value
                                ps['OutDate'] = datetime.datetime.today()
                            if loc[0].locationcode==LocationConstants.LOCATION_CODE_CORE or loc[0].locationcode==LocationConstants.LOCATION_CODE_USED:
                                if loc[0].locationcode==LocationConstants.LOCATION_CODE_CORE:
                                    ps['OutType'] = OUT_TYPE.CORE.value
                                    ps['Status'] = STATUS_TYPE.CORE_READY.value
                                    if ps['CoreValue'] != 0 and (not ps['CoreRANo'] or ps['CoreRANo']==""):
                                        ps['CoreRANo'] = XMLActions.GetCoreRANo(CurrentUserID, ps)
                                    elif loc[0].locationcode==LocationConstants.LOCATION_CODE_USED:
                                        ps['OutType'] = OUT_TYPE.USED.value
                                    else:
                                        pass
                                    ps['OutDate'] = datetime.datetime.today() 
                                if ps['WorkOrderID'] != 0:
                                    wo = OpWorkOrder.objects.get(id=ps['WorkOrderID'])
                                    dt = NspPartDetails.objects.filter(opworkorderid=wo.id) 
                                    if dt.exists and dt[0].psid==ps['PSID']:
                                        rows = NspPartDetails.objects.filter(Q(psid=0) | Q(psid=None), partno=ps['PartNo'], usage=USAGE_TYPE.USED.value)
                                        if rows.count() > 0:
                                            for r in rows:
                                                NspPartDetails.objects.filter(partdetailid=r.partdetailid).update(psid=ps['PSID'], updatedon=datetime.datetime.now(), updatedby=CurrentUserID)
                                        else:
                                            raise Exception(f"Part {ps['PartNo']} was not used in work order #{wo.workorderno}.")
                                    else:
                                        if dt.exists and dt[0].psid==ps['PSID'] and dt[0].usage!=USAGE_TYPE.USED.value:
                                            raise Exception(f"Part {ps['PartNo']} was not used in work order #{wo.workorderno}.") 
                elif loc[0].locationtype==LOCATION_TYPE.SQBOX.value:
                    sSQL = f"SELECT a.ID FROM OpWorkOrder a INNER JOIN OpBase b ON a.ID = b.ID WHERE b.Status < {STATUS_TYPE.CLOSED.value} AND a.PartWarehouseID = {warehouseid} AND a.SQBox = {sNewLocationCode} ORDER BY a.AptStartDTime"
                    res = SingleCursor.send_query(sSQL)
                    iWorkOrderID = 0
                    if type(res) is not str:
                        iWorkOrderID = res['ID']
                        try:
                            if iWorkOrderID!=0:
                                w = OpWorkOrder.objects.get(id=iWorkOrderID)
                                t = OpTicket.objects.get(id=OpBase.objects.get(id=w.id).pid)
                                toA = NspAccounts.objects.get(accountno=t.accountno) 
                                if t.warrantystatus!="3RD":
                                    if ps['AccountNo']!=toA.partaccountno:
                                        if not t.warrantystatus in ["NO", "3RD"] or not (t.warrantystatus in ["EXT", "POP"] and t.wtyexception=="OTWE2"):
                                            raise Exception("Part account does not match.") 
                                else:
                                    raise Exception("CANNOT move to closed SQBOX.") 
                            if ps['WorkOrderID']==iWorkOrderID or ps['WorkOrderID']==0:
                                sSQL = NspPartDetails.objects.filter(opworkorderid=iWorkOrderID, partno=ps['PartNo'], psid=ps['PSID'])
                                for x in sSQL:
                                    NspPartDetails.objects.filter(partdetailid=r.partdetailid).update(reservestatus=RESERVE_STATUS.RESERVED.value, updatedon=datetime.datetime.now(), updatedby=CurrentUserID)
                                    XMLActions.UpdateWorkOrderReserveStatus(CurrentUserID, iWorkOrderID, psid)
                                #look for rescheduled and confirm it
                                sSQL = f"SELECT * FROM NSPPartDetails WHERE OpWorkOrderID = {iWorkOrderID} AND PartNo = {ps['PartNo']} AND ReserveStatus = {RESERVE_STATUS.RESCHEDULED.value} AND PSID = {ps['PSID']}"
                                res = MultipleCursor.send_query(sSQL)
                                if type(res) is not str:
                                    for x in res:
                                        NspPartDetails.objects.filter(partdetailid=x.partdetailid).update(reservestatus=RESERVE_STATUS.CONFIRMED.value, updatedon=datetime.datetime.now(), updatedby=CurrentUserID)
                                        XMLActions.UpdateWorkOrderReserveStatus(CurrentUserID, iWorkOrderID, psid) 
                            #Received
                            if loc[0].locationtype==LocationConstants.LOCATION_CODE_RECEIVING:
                                sSQL = f"SELECT * FROM NSPPartDetails WHERE OpWorkOrderID = {iWorkOrderID} AND PartNo = {ps['PartNo']} AND ReserveStatus = {RESERVE_STATUS.PICKING.value} AND (DONo =  OR PONo = ) AND PSID = 0 ORDER BY DECODE(DONo, {ps['DONo']} , 1, 2) ASC"
                                res = MultipleCursor.send_query(sSQL)
                                if type(res) is not str:
                                    for x in res:
                                        NspPartDetails.objects.filter(partdetailid=x.partdetailid).update(reservestatus=RESERVE_STATUS.CONFIRMED.value, updatedon=datetime.datetime.now(), updatedby=CurrentUserID)
                                        XMLActions.UpdateWorkOrderReserveStatus(CurrentUserID, iWorkOrderID, psid)
                            #DO, PO, ReserveStatus, DO/PO : same - not ordered - different, ReserveStatus : Picking - Reserved - NotReserved / Ordered - NotRequired
                            sSQL = f"SELECT * FROM NSPPartDetails WHERE OpWorkOrderID = {iWorkOrderID} AND PartNo = {ps['PartNo']} AND PSID = 0 AND ReserveStatus IN ({RESERVE_STATUS.PICKING.value}, {RESERVE_STATUS.RESERVED.value}, {RESERVE_STATUS.UNKNOWN.value}, {RESERVE_STATUS.NOT_REQUIRED.value}) ORDER BY DECODE(DONo, {ps['DONo']} , 1, '', 2, 3) ASC, DECODE(PONo, {ps['PONo']} , 1, '', 2, 3) ASC, DECODE(ReserveStatus, {RESERVE_STATUS.PICKING.value} , 1, {RESERVE_STATUS.RESERVED.value} , 2, {RESERVE_STATUS.UNKNOWN.value} , 3, {RESERVE_STATUS.NOT_REQUIRED.value} , 4, 5) ASC"
                            res = MultipleCursor.send_query(sSQL)
                            if type(res) is not str:
                                for x in res:
                                    NspPartDetails.objects.filter(partdetailid=x.partdetailid).update(reservestatus=RESERVE_STATUS.CONFIRMED.value, updatedon=datetime.datetime.now(), updatedby=CurrentUserID)
                                    XMLActions.UpdateWorkOrderReserveStatus(CurrentUserID, iWorkOrderID, psid)
                        except:
                            raise Exception("This PSID CANNOT move to this SO.")
                        ps['WorkOrderID'] = iWorkOrderID
                        moving['WorkOrderID'] = iWorkOrderID                
                    elif loc[0].locationtype==LOCATION_TYPE.STORAGE.value:
                        if wh.hotparts:
                            if not XMLActions.IsHotPart(psid, warehouseid):
                                raise Exception("DO NOT place back to stock, MUST create RA.")

                        ps['WorkOrderID'] = 0
                    else:
                        ps['WorkOrderID'] = 0 #back to stock

                    ps['WarehouseID'] = warehouseid
                    ps['LocationCode'] = loc[0].locationcode
                    ps['ToLocationCode'] = "" 

                    if frWO and frWO.get('ID')!=ps['WorkOrderID']:
                        rows = NspPartDetails.objects.filter(opworkorderid=frWO.get('ID'), psid=psid)
                        if rows.count() > 0:
                            for x in rows:
                                pd = {}
                                pd['ReserveStatus'] = RESERVE_STATUS.UNKNOWN.value
                                pd['PSID'] = 0
                                pd['PONo'] = x.pono
                                pd['Remark'] = x.remark
                                if x.pono!="":
                                    if x.remark != "":
                                        pd['Remark'] += " "
                                    pd['Remark'] += x.pono
                                    pd['PONo'] = ""
                                NspPartDetails.objects.filter(partdetailid=x.partdetailid).update(reservestatus=pd['ReserveStatus'], psid=pd['PSID'], pono=pd['PONo'],remark=pd['Remark'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID) 
                                OpWorkOrder.objects.filter(id=frWO.get('ID')).update(reservecomplete=False)
                                nspdatalogid = DBIDGENERATOR.process_id("NSPDATALOGS_SEQ")
                                NspDataLogs.objects.create(nspdatalogid=nspdatalogid, tablename='NSPPartDetail', fieldname="ResetConfirmedPart", key1=x.partdetailid, key2=frWO.get('ID'), oldvalue=psid, newvalue="")
                                nspdatalogid = DBIDGENERATOR.process_id("NSPDATALOGS_SEQ") 
                                NspDataLogs.objects.create(nspdatalogid=nspdatalogid, tablename='NSPPartSerial', fieldname="MoveConfirmedPart", key1=psid, key2=ps['PartNo'], oldvalue=frWO.get('ID'), newvalue=ps['WorkOrderID'])          
                    if wh.exists():
                        raise Exception(f"Location {sNewLocationCode} doesn't exist.")
                    else:
                        raise Exception(f"Warehouse {warehouseid} doesn't exist.")    
                else:
                    raise Exception(f"Part PS {ps['PSID']} has to be moved to location {ps['ToLocationCode']}.")

            ps['LocationDate'] = datetime.datetime.today()
            NspPartSerials.objects.filter(psid=psid).update(locationdate=ps['LocationDate'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)

            moving['ToWarehouseID'] = ps['WarehouseID']
            moving['ToLocationCode'] = ps['LocationCode']
            NspPSMovingHistories.objects.filter(psid=ps['PSID']).update(fromwarehouseid=moving['FromWarehouseID'],fromlocationcode=moving['FromLocationCode'],workorderid=moving['WorkOrderID'],towarehouseid=moving['ToWarehouseID'],tolocationcode=moving['ToLocationCode'])

            XMLActions.UpdatePartLocations(CurrentUserID, ps['WarehouseID'], ps['PartNo'], ps['AccountNo'])

            if len(jd)!=0:
                if jd['JobType']==JOB_TYPE.RA_READY.value:
                    XMLActions.ExecuteJobDetail(CurrentUserID, JOB_TYPE.RA_READY.value, ps['JobDetailID'])
        else:
            raise Exception(f"PS {psid} was not found.")            




    @staticmethod
    def ValidationForMovePartLocation(CurrentUserID, iPSID, sFromWH, sFromLocation, sToWH, sToLocation):
        "to validate for move part location"
        from schedules_detail.support import PartSupport
        from schedules_detail.support import LocationConstants
        ps = PartSupport.GetPartSerial(iPSID)
        if sFromWH==sToWH and sFromLocation==sToLocation:
            if ps['OutType']!=OUT_TYPE.NONE.value:
                raise Exception(f"This part is already in {sFromLocation}")
        if sFromLocation==LocationConstants.LOCATION_CODE_LOST:
            raise Exception(f"CANNOT move parts to {LocationConstants.LOCATION_CODE_LOST} manually. Contact manager.")
        if sFromLocation in [LocationConstants.LOCATION_CODE_RA, LocationConstants.LOCATION_CODE_DEFECT] and ps['RAStatus']!="RR":
            raise Exception(f"CANNOT move parts to other location from {sFromLocation}")
        if ps['ToLocationCode']!=LocationConstants.LOCATION_CODE_RA and sToLocation==LocationConstants.LOCATION_CODE_RA:
            raise Exception(f"CANNOT move parts to {LocationConstants.LOCATION_CODE_RA} without any order.")
        u = Nspusers.objects.get(userid=CurrentUserID)
        uWH = NspWareHouses.objects.get(warehouseid=u.warehouseid) 
        toWH = NspWareHouses.objects.get(warehouseid=sToWH) 
        nspUser = u
        if XMLActions.CanI(CurrentUserID, nspUser, NSP_PERMIT_OBJECT.MOVE_PART_TO_OTHER_WAREHOUSE.value):
            if uWH.warehousetype==WAREHOUSE_TYPE.RDC_WAREHOUSE.value:
                if u.warehouseid!=uWH and toWH.rdcwarehouseid!=uWH.warehouseid:
                    raise Exception(f"You cannot move parts to {toWH.nickname}")
                if u.warehouseid!=sToWH:
                    raise Exception(f"You can only move parts to {toWH.nickname}")    

        if sFromWH==sToWH and sFromLocation==LocationConstants.LOCATION_CODE_RECEIVING and sToLocation==ps['ToLocationCode']:
            return True
        if ps['WorkOrderID'] > 0:
            sq = schedules2.SchedulesService
            wo = sq.GetWorkOrder(ps['WorkOrderID'])
            if wo['Status']==STATUS_TYPE.CLOSED.value and wo.get('IsRescheduled') > 0 and sFromLocation==wo.get('SQBox'):
                pd = NspPartDetails.objects.filter(psid=ps['PSID'], opworkorderid=ps['WorkOrderID']) 
                if pd.exists() and (pd[0].usage!=USAGE_TYPE.DEFECTIVE_PART.value or sToLocation==LocationConstants.LOCATION_CODE_DEFECT):
                    raise Exception("This part was rescheduled. CANNOT be moved to another location.")
        if sFromLocation==LocationConstants.LOCATION_CODE_USED.value:
            raise Exception("Used parts CANNOT be moved to another location.")
        if sFromLocation==LocationConstants.LOCATION_CODE_CORESENT.value:
            raise Exception("This is a CORESENT part. CANNOT be moved to another location.")
        if sFromLocation==LocationConstants.LOCATION_CODE_CORE and sToLocation!=LocationConstants.LOCATION_CODE_CORESENT:
            raise Exception("Used parts CANNOT be moved to another location.")
        if sFromLocation not in [LocationConstants.LOCATION_CODE_CORE, LocationConstants.LOCATION_CODE_CORESENT] and sToLocation==LocationConstants.LOCATION_CODE_CORESENT:
            raise Exception("Only the parts in SQ-CORE can be moved to SQ-CORESENT.")
        FL = NspLocations.objects.filter(warehouseid=sFromWH, locationcode=sFromLocation)
        TL = NspLocations.objects.filter(warehouseid=sToWH, locationcode=sToLocation)

        if FL.exists() and TL.exists():
            if FL[0].locationtype not in [LOCATION_TYPE.SQBOX.value, LOCATION_TYPE.NSC.value] and FL[0].locationcode!=LocationConstants.LOCATION_CODE_PENDING:
                if TL[0].locationcode in [LocationConstants.LOCATION_CODE_CORE, LocationConstants.LOCATION_CODE_USED]:
                    raise Exception("Only parts in SQBox can be moved to Used/Core location.")
                if sToLocation==LocationConstants.LOCATION_CODE_PENDING:
                    raise Exception("Only parts in SQBox can be moved to Pending location.")

            if FL[0].locationtype==LOCATION_TYPE.SQBOX.value and TL[0].locationtype==LOCATION_TYPE.SQBOX.value:
                raise Exception("Parts in SQBox CANNOT be moved to another SQBox.")

            if FL[0].locationtype==LOCATION_TYPE.SQBOX.value and (FL[0].warehouseid!=TL[0].warehouseid or FL[0].locationcode!=TL[0].locationcode):
                if XMLActions.CanMoveOutFromSQBox(iPSID):
                    raise Exception("This part CANNOT be moved out from the SQBOX.Contact manager.")
    @staticmethod
    def CanI(CurrentUserID, NspUser, iObject):
        return XMLActions.CanShe(CurrentUserID, NspUser, iObject)

    @staticmethod
    def CanShe(CurrentUserID, pUser, iObject):
        bRet = False 
        if pUser.nspstatus==NSP_STATUS.ENABLED.value:
            if iObject==NSP_PERMIT_OBJECT.READ_INFO.value:
                bRet = True
            elif iObject==NSP_PERMIT_OBJECT.UPLOAD_STORE_COVERAGE.value:
                bRet = pUser.ismanager 
                bRet = bRet or pUser.isfst
            elif iObject==NSP_PERMIT_OBJECT.CREATE_WAREHOUSESHIPMENT.value:
                bRet = pUser.ismanager
                bRet = bRet or pUser.iswarehouse
                bRet = bRet or pUser.isclaimagent
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_MASTER.value:
                bRet = pUser.ismanager 
            elif iObject==NSP_PERMIT_OBJECT.READ_REPORT.value:
                bRet = pUser.ismanager 
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_NSPPART.value:
                bRet = bRet or pUser.isclaimagent
            elif iObject==NSP_PERMIT_OBJECT.VIEW_COMMISSION.value:
                bRet = pUser.ismanager
            elif iObject==NSP_PERMIT_OBJECT.TRACK_STATUS.value:
                bRet = pUser.ismanager
                bRet = bRet or pUser.isclaimagent
                bRet = bRet or pUser.iscallagent
                bRet = bRet or pUser.iscalltech
                bRet = bRet or pUser.isfieldtech
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_CUSTOMER_INFO_FOR_INACTIVE_TICKET.value: 
                bRet = pUser.ismanager
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_NSP_USER.value:
                bRet = pUser.issupervisor
                bRet = bRet or pUser.isregionalmanager
                bRet = bRet or pUser.userid in [43901, 44313, 30072, 40329, 43737, 56283, 33514, 68510, 28001] #Corina Ponce, kenny, Jeffrey, tae.park, andy.yoon, karen.moran, vannida.yim, ami.hwang, sunnie 
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_ZONE_SLOT.value:
                bRet = pUser.isslotmanager
                bRet = bRet or pUser.issupervisor 
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_SETTING.value:
                bRet = pUser.ismanager 
            elif iObject==NSP_PERMIT_OBJECT.UPDATE_MAIL_TEMPLATE.value:
                bRet = bRet or pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_QOS.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_GEODATA.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.ASSIGN_TICKET_WAREHOUSE.value):
                bRet = pUser.ismanager
                bRet = bRet or pUser.isclaimagent
                bRet = bRet or pUser.iscallagent
                bRet = bRet or pUser.iscalltech
                bRet = bRet or pUser.isfieldtech
            elif (iObject == NSP_PERMIT_OBJECT.CHANGE_TICKET_WAREHOUSE.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.TRACK_STATUS_FOR_MANAGER.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.CLAIM.value):
                bRet = pUser.ismanager
                bRet = bRet or NSP_PERMIT_OBJECT.CLAIM_MANAGER.value
                bRet = bRet or pUser.isclaimagent
            elif (iObject == NSP_PERMIT_OBJECT.MANAGE_USER_ACCOUNT.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_INACTIVE_WORKORDER.value):
                bRet = pUser.ismanager or pUser.isfieldtech
                bRet = bRet or pUser.userid in [70532]       # christine
            elif (iObject == NSP_PERMIT_OBJECT.SCHEDULE_APPOINTMENT.value):
                bRet = pUser.iscallagent
                bRet = bRet or pUser.iscalltech
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.DISPATCH.value):
                bRet = pUser.isdis
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.CONFIG_WAREHOUSE.value):
                bRet = pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.REBUILD_ROUTING.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_REASONCODE.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_HOLIDAY.value):
                bRet = pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_BIZ_HOUR.value):
                bRet = pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_SQ_FEES.value):
                bRet = pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_MODEL_DOC_TYPE.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_MODEL_DOC.value):
                bRet = pUser.iscalltech
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.USE_SQL_MINING.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_SQL_MINING.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.REGISTER_PART.value):
                bRet = pUser.iscalltech
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.DEREGISTER_PART.value):
                pass
            elif (iObject == NSP_PERMIT_OBJECT.REGISTER_LOCATION.value):
                bRet = pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.DEREGISTER_LOCATION.value):
                pass
            elif (iObject == NSP_PERMIT_OBJECT.DO_RECEIVING.value):
                bRet = pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.DO_TRACKING.value):
                bRet = pUser.iscalltech
                bRet = bRet or pUser.iscallagent
                bRet = bRet or pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.MOVE_PART.value):
                bRet = pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.DIAGNOSIS.value):
                bRet = pUser.iscalltech
                bRet = bRet or pUser.iscallagent
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.DO_VIEW.value):
                bRet = pUser.iscalltech
                bRet = bRet or pUser.iscallagent
                bRet = bRet or pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_RA_REASON.value):
                bRet = pUser.iswarehouse
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.PART_ORDER.value):
                bRet = pUser.iscalltech
                bRet = bRet or pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.ASSIGN_COORDINATOR.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.ADD_ACCOUNT_NO.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.EDIT_ACCOUNT_NO.value):
                bRet = pUser.ismanager
            elif (iObject == NSP_PERMIT_OBJECT.LOCATION_MANAGER.value):
                bRet = pUser.islocationmanager
                #bRet = pUser.UserID = 24430 Or pUser.UserID = 21931 Or pUser.UserID = 27821 Or pUser.UserID = 28548 Or pUser.UserID = 30643 Or pUser.UserID = 44313 ' john, allen, josep, munsu, chanho, kenny    soonsub pUser.UserID = 26039
            elif (iObject == NSP_PERMIT_OBJECT.MANAGER_TECH.value):
                bRet = pUser.ismngrtech
            elif (iObject == NSP_PERMIT_OBJECT.IGNORE_COMPANY.value):
                bRet = ( not pUser.iscompany )  or pUser.companyid == 0 or  ( pUser.companyid == 297291 and pUser.isManager ) 
            elif (iObject == NSP_PERMIT_OBJECT.SET_SYSTEM_LOCATION.value):
                bRet = pUser.userid in [21931, 30643, 44313, 17905] #allen, chanho, kenny, Grace.Kim]'
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_CALLFIRE_TERM.value):
                bRet = pUser.userid in [17905, 27748, 51755, 52530, 57125, 50385, 58917]
                # Grace.Kim, monica.jaquez, seans.kim, karren.barlobinto, heidi.pak, jake.payes, onix.moreno
            elif (iObject == NSP_PERMIT_OBJECT.SEND_BBB_MAIL.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [52308, 54361, 54239, 46235, 27748, 57125, 68510, 33514, 31690]
            elif (iObject == NSP_PERMIT_OBJECT.CLAIM_MANAGER.value):
                bRet = pUser.userid in [21931, 30643, 28001, 17905, 44503, 24430, 70532, 63263, 36202] #' allen, chanho, sunnie, grace, rachel, john, christine, josephine, geraldine]'
            elif (iObject == NSP_PERMIT_OBJECT.SUPERVISOR.value):
                bRet = pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.CHANGE_TECH.value):
                bRet = not (pUser.isfieldtech and not pUser.issupervisor and not pUser.isleadtech and not pUser.ismngrtech and not pUser.ismanager)
            elif (iObject == NSP_PERMIT_OBJECT.CORRECT_PD_PS.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [44503, 44313, 46235] #rachel.kim, kenny, maria.cebreroz]'
            elif (iObject == NSP_PERMIT_OBJECT.REOPEN_TICKET.value):
                bRet = pUser.issupervisor
                bRet = bRet or  pUser.userid in  [38232, 43349] #michael.kim, brenda.aquino
            elif (iObject == NSP_PERMIT_OBJECT.COMPLETE_DATE_SWITCH.value):
                bRet = pUser.issupervisor
                bRet = bRet or  pUser.userid in [38232] #michael.kim]'
            elif (iObject == NSP_PERMIT_OBJECT.EDIT_RESCHEDULED_SO.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [38232, 70532] # michael.kim, christine]'
            elif (iObject == NSP_PERMIT_OBJECT.EDIT_COMPANY.value):
                bRet = pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.EDIT_JOB.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [44503, 44313] #rachel.kim, kenny
            elif (iObject == NSP_PERMIT_OBJECT.MOVE_PART_TO_OTHER_WAREHOUSE.value):
                bRet = pUser.userid in [28787, 44313, 17905, 30643, 44503] #hyunseok, kenny, grace, chanho, rachel
            elif (iObject == NSP_PERMIT_OBJECT.MODIFY_SO_APT.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.isslotmanager
                bRet = bRet or pUser.userid in [57125, 51755, 55335] #heidi.pak, seans.kim, jymar.caridad
            elif (iObject == NSP_PERMIT_OBJECT.EDIT_GSPN_TECH_ID.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.isRegionalmanager
                bRet = bRet or pUser.userid in [68510, 33514, 27094] #ami.hwang, vannida.yim, dennis.arnold
            elif (iObject == NSP_PERMIT_OBJECT.PART_SUPERVISOR.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [44313]
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_PRODUCT_TYPE.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [57125] #heidi.pak
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_PNN_EXCEPTION.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [44313] #kenny
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_TECH_INCENTIVE.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.isregionalmanager or pUser.userid in [40329, 44164, 57166] #tae.park, mike.roh, gs.park
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_INTERFACE_TO_SAP.value):
                bRet = pUser.issupervisor
            elif (iObject == NSP_PERMIT_OBJECT.VIEW_QUERY_RECORD.value):
                bRet = pUser.userid in [24430] #john
            elif (iObject == NSP_PERMIT_OBJECT.REQUIRED_PARTS.value):
                bRet = pUser.issupervisor
                bRet = bRet or pUser.userid in [30445] #jongyoup.kim
            elif (iObject == NSP_PERMIT_OBJECT.UPDATE_CLAIM_PARTS.value):
                bRet = pUser.userid in [36202] #geraldine.duong
            elif (iObject == NSP_PERMIT_OBJECT.SEND_MASS_APPOINTMENT_NOTICE.value):
                bRet = pUser.userid in [17905] #grace
            elif (iObject == NSP_PERMIT_OBJECT.REOPEN_CLAIMED_DO.value):
                bRet = pUser.issupervisor
                bRet = bRet or XMLActions.CanI(CurrentUserID, pUser, NSP_PERMIT_OBJECT.UPDATE_CLAIM_PARTS.value)
                bRet = bRet or pUser.userid in [44313] #kenny
            elif (iObject == NSP_PERMIT_OBJECT.AUTO_ROUTING.value):
                bRet = pUser.userid in [24430, 17905, 30643] #john, grace, chanho
            else:
                pass    
            if bRet == False:
                if pUser.userid==CurrentUserID:
                        bRet = True
            return bRet


    @staticmethod
    def CanMoveOutFromSQBox(iPSID):
        "check if part can be moved out from SQBox"
        from schedules_detail.support import PartSupport
        ps = PartSupport.GetPartSerial(iPSID)
        sq = schedules2.SchedulesService
        wo = sq.GetWorkOrder(ps['WorkOrderID'])
        if wo['Status'] >= STATUS_TYPE.PROCESSING.value and wo['Status'] < STATUS_TYPE.CLOSED.value:
            return False
        else:
            sSQL = NspPartDetails.objects.filter(psid=iPSID, opworkorderid=wo['ID'])
            iUsage = sSQL[0].usage if sSQL.exists else None
            if wo['Status']==STATUS_TYPE.CLOSED.value and iUsage==USAGE_TYPE.UNKNOWN.value:
                return False
            elif wo['Status']==STATUS_TYPE.VOID.value and iUsage==USAGE_TYPE.USED.value:
                return False
            else:
                pass
        return True


    @staticmethod
    def SetPendingStatus(CurrentUserID, WOID, bPending):
        "to set pending status of a workorder"
        wo = OpWorkOrder.objects.filter(id=WOID)
        if wo.exists():
            if bPending:
                wo.update(pendedon=datetime.datetime.now(), pendedby=CurrentUserID)
            else:
                wo.update(unpendedon=datetime.datetime.now(), unpendedby=CurrentUserID)
        else:
            SimpleLogger.do_log("WorkOrder doesn't exist.", "error")
            return False

    @staticmethod
    def CancelJobDetailOfPS(CurrentUserID, iPSID):
        "to cancel job detail of PS"
        from schedules_detail.support import PartSupport
        from schedules_detail.support import LocationConstants
        ps = PartSupport.GetPartSerial(iPSID)
        jd = JobSupport.GetNSPJobDetail(ps['JobDetailID'])
        iObject = jd['Job']['JobType']
        if (iObject==JOB_TYPE.RA_READY.value) or (iObject==JOB_TYPE.RA_SUBMIT.value) or (iObject==JOB_TYPE.RA_SHIP.value):
            NspJobDetails.objects.filter(jobdetailid=ps['JobDetailID']).update(status=STATUS_TYPE.CANCELLED.value)
            ps['JobDetailID'] = 0
            if ps['RANo'] != '':
                if ps['Remark'] != '':
                    ps['Remark'] += " "
                    ps['Remark'] += "RANo:" + ps['RANo']
                    XMLActions.ReOpenDONOByRA(CurrentUserID, iPSID)
            if ps['LocationCode']==LocationConstants.LOCATION_CODE_RA:
                ps['LocationCode'] = 'SQ-STOCK'
            ps['ToLocationCode'] = ''
            ps['OutType'] = OUT_TYPE.NONE.value
            ps['OutDate'] = ''
            ps['RANo'] = ''
            ps['RAReason'] = ''
            ps['RADTime'] = ''
            ps['ShipDate'] = ''
            ps['RAStatus'] = ''
            ps['Status'] = STATUS_TYPE.NONE.value
            ps['RANote'] = ''
            ps['RADONo'] = ''
            ps['RAAccountNo'] = ''
            NspPartSerials.objects.filter(psid=iPSID).update(jobdetailid=ps['JobDetailID'],remark=ps['Remark'],locationcode=ps['LocationCode'],tolocationcode=ps['ToLocationCode'],outtype=ps['OutType'],outdate=ps['OutDate'],rano=ps['RANo'],rareason=ps['RAReason'],radtime=ps['RADTime'],shipdate=ps['ShipDate'],rastatus=ps['RAStatus'],status=ps['Status'],ranote=ps['RANote'],radono=ps['RADONo'],raaccountno=ps['RAAccountNo'],updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
            XMLActions.CheckStatus(CurrentUserID, jd['JobID'])
        elif (iObject==JOB_TYPE.CORE_SHIP.value):
            if ps['WorkOrderID'] != 0:
                XMLActions.CancelJobDetail(jd['JobID'])
                ps['JobDetailID'] = 0
                w = OpWorkOrder.objects.get(id=ps['WorkOrderID'])
                ps['LocationCode'] = w.sqbox
                ps['OutType'] = OUT_TYPE.NONE.value
                ps['OutDate'] = ""
                ps['ShipDate'] = ""
                ps['Status'] = STATUS_TYPE.NONE.value
                ps['CoreRANo'] = ""
                NspPartSerials.objects.filter(psid=iPSID).update(jobdetailid=ps['JobDetailID'], locationcode=ps['LocationCode'], outtype=ps['OutType'], outdate=ps['OutDate'], shipdate=ps['ShipDate'], status=ps['Status'], corerano=ps['CoreRANo'], updatedon=datetime.datetime.now(),updatedby=CurrentUserID)
                XMLActions.CheckStatus(CurrentUserID, jd['JobID'])


    @staticmethod
    def ReOpenDONOByRA(CurrentUserID, iPSID):
        "to open DONO By RA"
        try:
            ps = NspPartSerials.objects.get(psid=iPSID)
            DoDetail = NspDoDetails.objects.filter(dodetailid=ps.dodetailid)[0]
            iOrgnQty =  DoDetail['raqty']
            if DoDetail['raqty'] > 0:
                DoDetail['raqty'] -= 1
                DoDetail['isavailable'] = DoDetail['qty'] <=  ( DoDetail['claimqty'] + DoDetail['raqty'] + DoDetail['thirdpartyqty'] )
                NspDoDetails.objects.filter(dodetailid=ps.dodetailid).update(qty=DoDetail['qty'], raqty=DoDetail['raqty'], isavailable=DoDetail['isavailable'],updatedon=datetime.datetime.today(), updatedby=CurrentUserID)
                nspdatalogid = DBIDGENERATOR.process_id("NSPDATALOGS_SEQ")
                NspDataLogs.objects.create(nspdatalogid=nspdatalogid, tablename='NSPDODETAILS', fieldname="DODetail ReOpened By RA", key1=DoDetail['dodetailid'], key2=ps.rano, oldvalue=iOrgnQty, newvalue=DoDetail['raqty'])
        except Exception as e:
            print(e)

    @staticmethod
    def CheckStatus(CurrentUserID, jobID):
        "to check status of NSPJOB by JobID"
        job = NspJobs.objects.get(jobid=jobID)
        if job.status < STATUS_TYPE.COMPLETED.value:
            iStatus = XMLActions.GetStatusFromDetails(jobID)
            if iStatus==STATUS_TYPE.COMPLETED.value or iStatus==STATUS_TYPE.CANCELLED.value:
                XMLActions.CompleteJob(CurrentUserID, jobID)
            if iStatus==STATUS_TYPE.COMPLETED.value:
                if job.jobtype==JOB_TYPE.RA_READY.value or job.jobtype==JOB_TYPE.RA_SUBMIT.value:
                    nextJob = XMLActions.GetJob(CurrentUserID, job.jobtype + 1, job.warehouseid, job.begindate, "", jobID, True)
                    if nextJob is not None:
                        XMLActions.TransferJobDetails(CurrentUserID, jobID, nextJob.jobid)
                        if nextJob.status==STATUS_TYPE.COMPLETED.value:
                            XMLActions.UnCompleteJob(nextJob.jobid)

    @staticmethod
    def GetStatusFromDetails(iJobID):
        "to get status from NSPJobDetails" 
        iRet = STATUS_TYPE.NONE.value
        NSPJob = NspJobs.objects.filter(jobid=iJobID)
        if not NSPJob.exists():
            return False
        else:
            sSQL = f"SELECT SUM(CASE WHEN Status < 60 THEN 1 ELSE 0 END) AS Open, SUM(CASE WHEN Status = 60 THEN 1 ELSE 0 END) AS Complete, SUM(CASE WHEN Status > 60 THEN 1 ELSE 0 END) AS Cancel FROM NSPJobDetails WHERE JobID = {iJobID}"
            res = MultipleCursor.send_query(sSQL)
            if type(res) is str or len(res)==0:
                iRet = STATUS_TYPE.NONE.value
            else:
                if res[0]['OPEN'] > 0:
                    iRet = STATUS_TYPE.PROCESSING.value
                else:
                    if res[0]['COMPLETE'] > 0:
                        iRet = STATUS_TYPE.COMPLETED.value
                    else:
                        iRet = STATUS_TYPE.CANCELLED.value
            return iRet                    


    @staticmethod
    def CompleteJob(CurrentUserID, jobID, iStatus=STATUS_TYPE.COMPLETED.value):
        IsCompleted = NspJobs.objects.filter(status=iStatus)
        if not IsCompleted.exists():
            IsStarted = NspJobs.objects.filter(status__gte = STATUS_TYPE.PROCESSING.value) 
            if not IsStarted.exists():
                StartJob = NspJobs.objects.filter(jobid=jobID).update(status=STATUS_TYPE.PROCESSING.value,startedby=CurrentUserID,startedon=datetime.datetime.now())
            NspJobs.objects.filter(jobid=jobID).update(status=iStatus, completedby=CurrentUserID, completedon=datetime.datetime.now())

    @staticmethod
    def UnCompleteJob(jobID):
        NspJobs.objects.filter(jobid=jobID).update(completedby=0, completedon=None, status=STATUS_TYPE.PROCESSING.value) 

    @staticmethod
    def CancelJobDetail(jobID):
        NspJobs.objects.filter(jobid=jobID).update(status=STATUS_TYPE.CANCELLED.value)            

    @staticmethod
    def GetJob(CurrentUserID, iJobType, sWarehouseID, dBeginDate, dDueDate, iRelayedFrom=0, bNew=False, bIncludeCancelled=False, bOnlyActive=True):
        if dBeginDate:
            if iJobType==JOB_TYPE.CHECK_IN.value:
                if datetime.datetime.today().weekday()==4:  #Friday
                    dBeginDate = datetime.datetime.today() + datetime.timedelta(days=3) 
                elif datetime.datetime.today().weekday()==5: #Saturday
                    dBeginDate = datetime.datetime.today() + datetime.timedelta(days=2)
                else: #Any Day
                    dBeginDate = datetime.datetime.today() + datetime.timedelta(days=1) 
            else:
                dBeginDate = datetime.datetime.today()
        if bNew:
            job_primary_key = DBIDGENERATOR.process_id("NSPJOBS_SEQ")
            NspJobs.objects.create(jobid=job_primary_key, createdon=datetime.datetime.now(), createdby=CurrentUserID, jobtype=iJobType, warehouseid=sWarehouseID, begindate=dBeginDate, status=STATUS_TYPE.OPEN.value, orderedby=CurrentUserID, startedby=CurrentUserID, startedon=datetime.datetime.now(), completedby=CurrentUserID, completedon=datetime.datetime.now())
            job = NspJobs.objects.filter(jobid=job_primary_key)
        else:
            job = NspJobs.objects.filter(jobtype=iJobType, warehouseid=sWarehouseID, begindate=dBeginDate) 
        if not job.exists() or bNew:
            if not dDueDate:
                dDueDate = datetime.datetime.today()
            DueDate = dDueDate + ' ' + datetime.time(23, 59, 59)
            if iRelayedFrom != 0:
                pJob = NspJobs.objects.filter(jobid=iRelayedFrom)
                if pJob.exists():
                    OrderedBy = pJob[0].orderedby
                    BeginDate = pJob[0].begindate
                else:
                    OrderedBy = CurrentUserID
                    BeginDate = dBeginDate
            else:
                OrderedBy = CurrentUserID
                BeginDate = dBeginDate
            update_nsp = NspJobs.objects.filter(jobid=iRelayedFrom).update(updatedon=datetime.datetime.now(), updatedby=CurrentUserID, jobtype=iJobType, warehouseid=sWarehouseID, begindate=BeginDate,duedate=DueDate, orderedby=OrderedBy)
            if update_nsp==0:
                job_primary_key = DBIDGENERATOR.process_id("NSPJOBS_SEQ")    
                NspJobs.objects.create(jobid=job_primary_key, createdon=datetime.datetime.now(), createdby=CurrentUserID, jobtype=iJobType, warehouseid=sWarehouseID, begindate=BeginDate,duedate=DueDate, orderedby=OrderedBy, startedby=CurrentUserID, startedon=datetime.datetime.now(), completedby=CurrentUserID, completedon=datetime.datetime.now())
                job = NspJobs.objects.filter(jobid=job_primary_key)
            else:
                job = NspJobs.objects.filter(jobid=iRelayedFrom)          
        try:
            return job[0]
        except:
            return None    

    @staticmethod
    def TransferJobDetails(CurrentUserID, pJobID, nJobID):
        "to tranfer job details form one table to another new table"
        lRet = 0
        dt = NspJobDetails.objects.filter(jobid=pJobID, status=STATUS_TYPE.COMPLETED.value).values('jobdetailid')
        if dt.count() > 0:
            for x in dt:
                try:
                    jd = NspJobDetails.objects.get(jobdetailid=x['jobdetailid'])
                    newJd = {}
                    newJd['JobID'] = nJobID
                    newJd['PSID'] = jd.psid
                    newJd['PartNo'] = jd.partno
                    newJd['DONo'] = jd.dono
                    newJd['Status'] = STATUS_TYPE.OPEN.value
                    NspJobDetails.objects.create(jobdetailid=DBIDGENERATOR.process_id("NSPJOBDETAILS_SEQ"), jobid=newJd['JobID'], psid=newJd['PSID'], partno=newJd['PartNo'], dono=newJd['DONo'], status=newJd['Status'], createdon=datetime.datetime.now(), createdby=CurrentUserID)
                    lRet += 1
                except Exception as e:
                    email_title = f"[NSPJob]Transfer Job details - {pJobID}" 
                    email_content = str(e) + "\n" + "Server: " + socket.gethostname() + "\n" + "DB Server: " + settings.DATABASES['default']['HOST'] + "\n" + "User: " + getuserinfo(CurrentUserID)['UserName']
                    to_address = settings.NSC_ADMIN_EMAIL
                    from_address = settings.NSP_INFO_EMAIL
                    sendmailoversmtp(to_address, email_title, email_content, from_address)
        return lRet

    @staticmethod
    def CheckDefective(PS):
        if PS['WorkOrderID']==0:
            return False
        sSQL = f"SELECT COUNT(*) FROM OpTicket T INNER JOIN OpBase B1 ON T.ID = B1.PID INNER JOIN OpWorkOrder W1 ON B1.ID = W1.ID INNER JOIN NSPPartDetails PD ON W1.ID = PD.OpWorkOrderID INNER JOIN OpBase B2 ON T.ID = B2.PID INNER JOIN OpWorkOrder W2 ON B2.ID = W2.ID AND B1.ID <> B2.ID WHERE PD.PartNo = {PS['PartNo']} AND PD.Usage = {USAGE_TYPE.USED.value} AND W2.ID = {PS['WorkOrderID']} AND PD.PSID <> {PS['PSID']}"
        res = SingleCursor.send_query(sSQL)['COUNT(*)']
        if res > 0:
            return True


    @staticmethod
    def IsHotPart(iPSID, sWarehouseID=""):
        from schedules_detail.support import PartSupport
        bRet = False
        ps = PartSupport.GetPartSerial(iPSID) 
        if sWarehouseID=="":
            sWarehouseID = ps['WarehouseID']
        hp = NspHotParts.objects.filter(warehouseid=sWarehouseID, partno=ps['PartNo'])
        if hp.exists():
            bRet = True
        return bRet

    @staticmethod
    def GetCoreRANo(CurrentUserID, pPS):
        MAX_PERIOD_DAYS = 90
        PRIOR_TO_DO_DATE = 30
        sCoreRANo = ""
        dFromDate = ""
        dToDate = ""
        if pPS['CoreValue'] != 0:
            d = NspDos.objects.get(dono=pPS['DONo'])
            if d.dodate:
                dFromDate = d.dodate + datetime.timedelta(days=PRIOR_TO_DO_DATE) 
            else:
                dFromDate = d.createdon + datetime.timedelta(days=PRIOR_TO_DO_DATE)
            dToDate = dFromDate + datetime.timedelta(days=MAX_PERIOD_DAYS) 

            sCoreRANo = GspnWebServiceClient.GetPartCoreRANo(CurrentUserID, pPS['AccountNo'], dFromDate, dToDate, pPS['DONo'], pPS['PartNo'])
        return sCoreRANo

    @staticmethod
    def UpdateWorkOrderReserveStatus(CurrentUserID, iWorkOrderID, iPSID=0):
        iNotCompletedLineCount = NspPartDetails.objects.filter(Q(reservestatus=RESERVE_STATUS.NOT_REQUIRED.value) | Q(reservestatus=RESERVE_STATUS.CONFIRMED.value), opworkorderid=iWorkOrderID)
        woSQ = OpWorkOrder.objects.get(id=iWorkOrderID)
        wo = {}
        if iNotCompletedLineCount==0:
            wo['ReserveComplete'] = True
            XMLActions.UpdateReadyToGo(OpBase.objects.get(id=woSQ.id).pid)
        else:
            wo['ReserveComplete'] = False
        OpWorkOrder.objects.filter(id=iWorkOrderID).update(reservecomplete=wo['ReserveComplete'])
        if iPSID!=0:
            XMLActions.UpdatePOReservedParts(iWorkOrderID, iPSID) 

    @staticmethod
    def UpdatePOReservedParts(iWorkOrderID, iPSID):
        sSQL = f"SELECT PD.PartNo , SUM(DECODE(PD.ReserveStatus, {RESERVE_STATUS.CONFIRMED.value} , 1, 0)) AS Confirmed , SUM(DECODE(PD.ReserveStatus, {RESERVE_STATUS.CONFIRMED.value} , 0, 1)) AS NotConfirmed FROM NSPPartDetails PD LEFT OUTER JOIN NSPPartMasters PM ON PD.PartNo = PM.PartNo WHERE PD.OpWorkOrderID = {iWorkOrderID} AND (PM.PartNo IS NULL OR (PM.ReserveException IS NOT NULL AND PM.ReserveException = 0 )) GROUP BY PD.PartNo ORDER BY PD.PartNo"
        res = MultipleCursor.send_query(sSQL)
        if type(res) is not str:
            for x in res:
                if x['CONFIRMED'] > 0 and x['NOTCONFIRMED']==0:
                    XMLActions.ReleasePOReservedParts(iWorkOrderID, x['PARTNO'], iPSID)


    @staticmethod
    def ReleasePOReservedParts(iWorkOrderID, sPartNo, iPSID):
        from schedules_detail.support import LocationConstants
        sSQL = f"SELECT PSID FROM NSPPartSerials WHERE LocationCode = {LocationConstants.LOCATION_CODE_RECEIVING} AND PartNo = {sPartNo} AND WorkOrderID = {iWorkOrderID} AND ToLocationCode IS NOT NULL AND PSID <> {iPSID}" 
        res = MultipleCursor.send_query(sSQL)
        if type(res) is not str:
            for x in res:
                NspPartSerials.objects.filter(psid=iPSID).update(tolocationcode="", workorderid=0)                         
            

    @staticmethod
    def UpdateReadyToGo(CurrentUserID, iTID):
        t = OpTicket.objects.get(id=iTID)
        if t.status < STATUS_TYPE.CLOSED.value:
            if t.gspnstatus <= STATUS_TYPE.REPAIR.value:
                OpTicket.objects.filter(id=iTID).update(gspnstatus=STATUS_TYPE.REPAIR.value, delayreason="HEZ03")
            if t.systemid==SYSTEM_ID.GSPN.value:
                try:
                    GspnWebServiceClient.SyncTicketInfoToGSPN(CurrentUserID, t)
                except Exception as e:
                    email_title = f"[NSP]UpdateReadyToGo - {t.ticketno}" 
                    email_content = str(e) + "\n" + "Server: " + socket.gethostname() + "\n" + "DB Server: " + settings.DATABASES['default']['HOST'] + "\n" + "User: " + getuserinfo(CurrentUserID)['UserName']
                    to_address = settings.NSC_ADMIN_EMAIL
                    from_address = settings.NSP_INFO_EMAIL
                    sendmailoversmtp(to_address, email_title, email_content, from_address)    
                 

    @staticmethod
    def UpdatePartLocations(CurrentUserID, sWarehouseID="", sPartNo="", sPartAccountNo=""):
        sSQL = f"SELECT a.WarehouseID,PartNo,a.AccountNo,a.LocationCode,b.LocationType,COUNT(0) AS Count FROM NSPPartSerials a INNER JOIN NSPLocations b ON a.LocationCode=b.LocationCode AND a.WarehouseID=b.WarehouseID WHERE OutDate IS NULL AND b.Restricted=0 AND b.LocationType > {LOCATION_TYPE.UNKNOWN.value}"
        if sWarehouseID!="":
            sSQL += f" AND a.WarehouseID={sWarehouseID}"
        if sPartNo!="":
            sSQL += f" AND a.PartNo={sPartNo}"
        if sPartAccountNo!="":
            sSQL += f" AND a.AccountNo={sPartAccountNo}"
        sSQL += " GROUP BY a.WarehouseID,a.PartNo,a.AccountNo,a.LocationCode,b.LocationType"
        dtData1 = MultipleCursor.send_query(sSQL)

        sSQL = f"SELECT DISTINCT a.WarehouseID,PartNo,a.AccountNo FROM NSPPartSerials a INNER JOIN NSPLocations b ON a.LocationCode=b.LocationCode AND a.WarehouseID=b.WarehouseID WHERE OutDate IS NULL AND b.Restricted=0 AND b.LocationType > {LOCATION_TYPE.UNKNOWN.value}"
        if sWarehouseID!="":
            sSQL += f" AND a.WarehouseID={sWarehouseID}"
        if sPartNo!="": 
            sSQL += f" AND a.PartNo={sPartNo}"
        if sPartAccountNo!="":
            sSQL += f" AND a.AccountNo={sPartAccountNo}"
        dtData2 = MultipleCursor.send_query(sSQL)

        for r in dtData2:
            pmv = NspPartMaster4Warehouses.objects.filter(partno=r['PARTNO'], warehouseid=r['WAREHOUSEID'], partaccountno=r['ACCOUNTNO']).values()[0]
            iPos = 0 
            for rr in dtData1:
                if rr['PARTNO']==pmv['partno'] and rr['WAREHOUSEID']==pmv['warehouseid'] and rr['ACCOUNTNO']==pmv['partaccountno']:
                    pmv['locationcode1'] = rr['LOCATIONCODE'] 
                    pmv['locationcode2'] = rr['LOCATIONCODE']
                    pmv['locationcode3'] = rr['LOCATIONCODE']
            NspPartMaster4Warehouses.objects.filter(partno=r['PARTNO'], warehouseid=r['WAREHOUSEID'], partaccountno=r['ACCOUNTNO']).update(locationcode1=pmv['locationcode1'], locationcode2=pmv['locationcode2'], locationcode3=pmv['locationcode3'], updatedon=datetime.datetime.now(), updatedby=CurrentUserID)                                            


    @staticmethod
    def ExecuteJobDetail(CurrentUserID, jt, iJobDetailID):
        jd = NspJobDetails.objects.filter(jobdetailid=iJobDetailID)
        if jd.exists() and jd[0].status==STATUS_TYPE.COMPLETED.value:
            try:
                if NspJobs.objects.get(jobid=jd[0].jobid).jobtype!=jt:
                    return "That JobDetail is not on that Job. Maybe the status of the job was changed."
                else: #Execute()
                    NspJobDetails.objects.filter(jobdetailid=iJobDetailID).update(status=STATUS_TYPE.COMPLETED.value, executedby=CurrentUserID, executedon=datetime.datetime.now())
                    job = NspJobs.objects.get(jobid=jd[0].jobid)
                    if job.status!=STATUS_TYPE.PROCESSING.value:
                        NspJobs.objects.filter(jobid=jd[0].jobid).update(status=STATUS_TYPE.PROCESSING.value, startedby=CurrentUserID, startedon=datetime.datetime.now()) 
                    XMLActions.CheckStatus(CurrentUserID, jd[0].jobid)
            except:
                pass
        else:
            raise Exception("That JobDetail doesn't exist or already executed.") 


    @staticmethod
    def GetWorkOrderIDBySQBox(sWarehouseID, sSQBoxCode):
        sSQL = f"SELECT a.ID FROM OpWorkOrder a INNER JOIN OpBase b ON a.ID = b.ID WHERE b.Status < {STATUS_TYPE.CLOSED.value} AND a.PartWarehouseID = {sWarehouseID} AND a.SQBox = {sSQBoxCode} ORDER BY a.AptStartDTime"
        res = SingleCursor.send_query(sSQL)
        return res                           
    
    
    @staticmethod
    def SyncTicketPictureToGSPN(token, iPictureID):
        "to make a xml request to a remoteserver" 
        SimpleLogger.do_log("SyncTicketPictureToGSPN()...")
        soapAction = "\"http://office.kwinternational.com/SyncTicketPictureToGSPN\""
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
        SimpleLogger.do_log(f"soapAction= {soapAction}")
        SimpleLogger.do_log(f"soapMessage= {soapMessage}")

        #posting xml request now
        if settings.DEBUG is True:
            URL = settings.DEV_ENDPOINT_URL
        else:
            URL = settings.PROD_ENDPOINT_URL 

        SimpleLogger.do_log(f"uri= {URL}")

        encoded_request = soapMessage.encode('utf-8')

        headers = {
                "Content-Type": "text/xml; charset=UTF-8",
                "SOAPAction": soapAction}

        result = requests.post(url=URL,
                                headers=headers,
                                data=encoded_request,
                                verify=False)

        SimpleLogger.do_log(f"result= {result}")
        return result


    
    

