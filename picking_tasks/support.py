#supporting functions
import datetime
from picking_tasks.models import NspPickingBatches
from functions.querymethods import MultipleCursor
from schedules_list_map.schedules import LocationType, OutType
from nsp_user.models import getboolvalue, getfloatvalue

class PickingSupport:

    @staticmethod
    def GetPickingBatch(batchid):
        "to get data for picking batch based on batch ID"
        try:
            x = NspPickingBatches.objects.get(batchid=batchid)
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
            return xd
        except:
            return None

    @staticmethod
    def GetPickingBatchTicketSummaryList(batchId):
        "to run a SQL query to get list of picking batch ticket summary"
        query = f"SELECT TicketNo AS TicketNo, WH.NickName AS WarehouseName, SQBox AS SQBox, COUNT(PartDetailID) AS PartCount FROM NSPPartDetails a INNER JOIN OpWorkOrder c ON a.OpWorkOrderID=c.ID INNER JOIN OpBase d ON c.ID=d.ID INNER JOIN OpTicket e ON d.PID=e.ID INNER JOIN NSPWarehouses WH ON c.PartWarehouseID = WH.WarehouseID WHERE PickingBatchID={batchId} GROUP BY TicketNo, WH.NickName, SQBox ORDER BY TicketNo;" 
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['TicketNo'] = x['TICKETNO']
                xd['SQBox'] = x['SQBOX']
                xd['WarehouseName'] = x['WAREHOUSENAME'] 
                xd['Parts'] = getfloatvalue(x.get('PARTCOUNT'))
                resList.append(xd)
            return resList


    @staticmethod
    def GetPickingLabelListByDOOrder(batchId):
        "to get picking label list by DO Order" 
        query = f"SELECT BatchID, PartNo, WorkOrderNo, AptStartDTime, SQBox, TicketNo, WarehouseID,WarehouseCode, WarehouseName, AccountNo, TicketDate, LocationCode1, LocationCode2, LocationCode3 FROM (SELECT CAST(PD.PickingBatchID AS NUMBER(9)) AS BatchID, PD.PartNo, W.WorkOrderNo, W.AptStartDTime, W.SQBox,T.TicketNo, WH.WarehouseID, WH.Code AS WarehouseCode, WH.NickName AS WarehouseName, A.PartAccountNo AS AccountNo,T.IssueDTime AS TicketDate, PD.PartDetailID,(SELECT TRUNC(MAX(PT.CompleteDTime)) FROM OpTicket PT INNER JOIN OpBase PB ON PT.ID = PB.PID INNER JOIN OpWorkOrder PW ON PB.ID = PW.ID INNER JOIN NSPPartDetails PPD ON PW.ID = PPD.OpWorkOrderID WHERE PPD.PartNo = PD.PartNo AND PT.SerialNo = T.SerialNo AND PT.CompleteDTime <= T.IssueDTime ) AS PrevTicketDate, PS.LocationCode , ROW_NUMBER() OVER (PARTITION BY PD.PartDetailID ORDER BY DECODE(PS.AccountNo, A.PartAccountNo, 0, 1) ASC , CASE WHEN D.DODATE >= TRUNC(CURRENT_DATE) - 45 THEN 0 ELSE 1 END ASC , D.DODate ASC) AS RN FROM NSPPartDetails PD INNER JOIN OpWorkOrder W ON PD.OpWorkOrderID = W.ID INNER JOIN OpBase B ON W.ID = B.ID INNER JOIN OpTicket T ON B.PID = T.ID INNER JOIN NSPWarehouses WH ON W.PartWarehouseID = WH.WarehouseID INNER JOIN NSPAccounts A ON T.AccountNo = A.AccountNo INNER JOIN NSPPickingBatches PBC ON PD.PickingBatchID = PBC.BatchID LEFT OUTER JOIN (NSPPartSerials PS INNER JOIN NSPLocations L ON PS.WarehouseID = L.WarehouseID AND PS.LocationCode = L.LocationCode AND L.Restricted = 0 AND L.LocationType = {LocationType.STORAGE.value} AND PS.OutType = {OutType.NONE.value} AND PS.ToLocationCode IS NULL INNER JOIN NSPDOs D ON PS.DONo = D.DONo ) ON PD.PartNo = PS.PartNo AND PBC.WarehouseID = PS.WarehouseID AND (A.PartAccountNo = PS.AccountNo OR T.WarrantyStatus = '3RD') WHERE PBC.BatchID = {batchId}) PIVOT (MAX(LocationCode) FOR RN IN (1 AS LocationCode1, 2 AS LocationCode2, 3 AS LocationCode3)) ORDER BY TRUNC(AptStartDTime) ASC , LocationCode1 ASC NULLS LAST, LocationCode2 ASC NULLS LAST, LocationCode3 ASC NULLS LAST , WarehouseID ASC, WorkOrderNo ASC;"                         
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['BatchID'] = x['BATCHID']
                xd['PartNo'] = x['PARTNO']
                xd['AccountNo'] = x['ACCOUNTNO']
                xd['WorkOrderNo'] = x['WORKORDERNO'] 
                xd['AptStartDTime'] = x['APTSTARTDTIME'] 
                xd['SQBox'] = x['SQBOX']
                xd['TicketNo'] = x['TICKETNO'] 
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['WarehouseCode'] = x['WAREHOUSECODE'] 
                xd['WarehouseName'] = x['WAREHOUSENAME']
                xd['LocationCode1'] = x['LOCATIONCODE1']
                xd['LocationCode2'] = x['LOCATIONCODE2']
                xd['LocationCode3'] = x['LOCATIONCODE3']
                resList.append(xd)
            return resList

    @staticmethod
    def GetReceivingLabelList(doNo, iItemNo=0):
        "to get list of receiving labels"
        query = f"SELECT CAST(PS.PSID AS NUMBER(9)) AS PSID, PS.PartNo AS PartNo, PS.AccountNo AS AccountNO, PS.WarehouseID AS WarehouseID, PS.DONo AS DONo, PS.InDate AS InDate, PS.CoreValue AS CoreValue, PS.ToLocationCode AS ToLocationCode, PM.PartDescription AS PartDescription, PMW.LocationCode1 AS LocationCode1, PMW.LocationCode2 AS LocationCode2, PMW.LocationCode3 AS LocationCode3, W.WorkOrderNo AS WorkOrderNo, W.AptStartDTime AS AptStartDTime, T.TicketNo AS TicketNo, WH.Code AS WarehouseCode, T.IssueDTime AS TicketDate, ( SELECT TRUNC(MAX(PT.CompleteDTime)) FROM ((OpTicket PT INNER JOIN OpBase PB ON PT.ID=PB.ID) INNER JOIN (OpWorkOrder PW INNER JOIN OpBase PWB ON PW.ID=PWB.ID) ON PB.ID=PWB.PID) INNER JOIN NSPPartDetails PD ON PWB.ID=PD.OpWorkOrderID WHERE PD.PartNo=PS.PartNo AND PT.SerialNo=T.SerialNo AND PT.CompleteDTime<=T.IssueDTime ) AS PrevTicketDate, PS.IsOFS FROM NSPPartSerials PS INNER JOIN NSPDOs D ON PS.DONo = D.DONo INNER JOIN NSPDODetails DD ON D.DOID = DD.DOID AND PS.ItemNo = DD.ItemNo LEFT OUTER JOIN NSPPartMasters PM ON PS.PartNo=PM.PartNo LEFT OUTER JOIN NSPPartMaster4Warehouses PMW ON PS.WarehouseID=PMW.WarehouseID and PS.PartNo=PMW.PartNo and PS.AccountNo = PMW.PartAccountNo LEFT OUTER JOIN OpWorkOrder W ON PS.WorkOrderID=W.ID LEFT OUTER JOIN OpBase B ON W.ID=B.ID LEFT OUTER JOIN OpTicket T ON B.PID=T.ID LEFT OUTER JOIN NSPWarehouses WH ON T.WarehouseID=WH.WarehouseID WHERE PS.DONo='{doNo}' "
        if iItemNo > 0:
            query += f"AND DD.ItemNo={iItemNo} "
        query += "ORDER BY PSID;"
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xd = {}
                xd['WorkOrderNo'] = x['WORKORDERNO']
                xd['AptStartDTime'] = x['APTSTARTDTIME']
                xd['TicketNo'] = x['TICKETNO']
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['WarehouseCode'] = x['WAREHOUSECODE']
                try:
                    if x['TICKETDATE'] and x['PREVTICKETDATE']:
                        xd['PrevDate'] = f"Prev. {datetime.datetime.strftime(x['PREVTICKETDATE'], '%m/%d/%Y')} ({(x['TICKETDATE'] - x['PREVTICKETDATE']).days}d)"
                    else:
                        xd['PrevDate'] = ""
                except Exception as e:
                    print(f"GetReceivingLabelList error: {e}")
                    xd['PrevDate'] = ""        
                xd['PSID'] = x['PSID'] 
                xd['PartNo'] = x['PARTNO']
                xd['PartDescription'] = x['PARTDESCRIPTION'] 
                xd['AccountNo'] = x['ACCOUNTNO']
                xd['WarehouseID'] = x['WAREHOUSEID']
                xd['DONo'] = x['DONO'] 
                xd['InDate'] = x['INDATE']
                xd['CoreValue'] = getfloatvalue(x['COREVALUE'])
                xd['ToLocationCode'] = x['TOLOCATIONCODE']
                xd['LocationCode1'] = x['LOCATIONCODE1']
                xd['LocationCode2'] = x['LOCATIONCODE2']
                xd['LocationCode3'] = x['LOCATIONCODE3']
                xd['IsOFS'] = getboolvalue(x['ISOFS'])        
                resList.append(xd)
            return resList                             



