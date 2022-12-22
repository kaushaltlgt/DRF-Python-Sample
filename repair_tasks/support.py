#supporting functions
from repair_tasks.models import NspJobDetails, NspJobs
from schedules_detail.models import NspWareHouses
from functions.querymethods import MultipleCursor
from nsp_user.models import getfloatvalue

class JobSupport:
    "methods related to jobs and job details"

    @staticmethod
    def GetNSPJobDetail(JobDetailID):
        "to get data from the table NspJobDetails based on jobdetailid"
        try:
            j = NspJobDetails.objects.get(jobdetailid=JobDetailID)
            result = {}
            result['JobDetailID'] = j.jobdetailid
            try:
                nj = NspJobs.objects.get(jobid=j.jobid)
                xnj = {}
                xnj['JobID'] = nj.jobid
                xnj['JobType'] = nj.jobtype
                xnj['WarehouseID'] = nj.warehouseid
                xnj['BeginDate'] = nj.begindate
                xnj['DueDate'] = nj.duedate
                xnj['OrderedBy'] = nj.orderedby
                xnj['OrderedOn'] = nj.orderedon
                xnj['StartedBy'] = nj.startedby
                xnj['StartedOn'] = nj.startedon
                xnj['CompletedBy'] = nj.completedby
                xnj['CompletedOn'] = nj.completedon
                xnj['Status'] = nj.status
                xnj['CreatedOn'] = nj.createdon
                xnj['CreatedBy'] = nj.createdby
                xnj['UpdatedOn'] = nj.updatedon
                xnj['UpdatedBy'] = nj.updatedby
                if nj.updatedby is not None:
                    xnj['LogBy'] = nj.updatedby
                else:
                    xnj['LogBy'] = nj.createdby    
                xnj['LogByName'] = None
                for key, value in xnj.items():
                    if value=="":
                        xnj[key] = None
                result['NSPJob'] = xnj
            except:    
                result['NSPJob'] = None #need to get data from the table NspJobs
            result['PSID'] = j.psid
            result['PartNo'] = j.partno
            result['DONo'] = j.dono
            result['LocationCode'] = j.locationcode
            result['ExecutedOn'] = j.executedon
            result['ExecutedBy'] = j.executedby
            result['Status'] = j.status
            result['CreatedOn'] = j.createdon
            result['CreatedBy'] = j.createdby
            result['UpdatedOn'] = j.updatedon
            result['UpdatedBy'] = j.updatedby
            if j.updatedby is not None:
                result['LogBy'] = j.updatedby
            else:
                result['LogBy'] = j.createdby    
            result['LogByName'] = None
            for key, value in result.items():
                if value=="":
                    result[key] = None
            return result
        except:
            return None

class WareHouseSupport:
    "function related to warehouses defined here"

    @staticmethod
    def GetWarehouse(id):
        "to get warehouse data based on ID"
        try:
            x = NspWareHouses.objects.get(warehouseid=id)
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
            return xdict
        except:
            return None

    @staticmethod
    def GetRDCWarehouse(warehouseID):
        "to get RDC warehouse list based on ID"
        query = f"SELECT * FROM NSPWAREHOUSES WHERE IsActive = 1 AND (WarehouseID = '{warehouseID}' OR RDCWarehouseID = '{warehouseID}') ORDER BY DECODE(WarehouseID, '{warehouseID}', 0, 1) ASC;"                                
        res = MultipleCursor.send_query(query)
        if type(res) is str or len(res)==0:
            return []
        else:
            resList = []
            for x in res:
                xdict = {}
                xdict['WarehouseID'] = x['WAREHOUSEID']
                xdict['NickName'] = x['NICKNAME']
                xdict['Color'] = x['COLOR']
                xdict['Latitude'] = x['LATITUDE']
                xdict['Longitude'] = x['LONGITUDE']
                xdict['MarkerAdjX'] = getfloatvalue(x['MARKERADJX'])
                xdict['MarkerAdjY'] = getfloatvalue(x['MARKERADJY'])
                xdict['Code'] = x['CODE']
                xdict['CompanyID'] = x['COMPANYID']
                xdict['TimeZone'] = x['TIMEZONE']
                xdict['IsActive'] = x['ISACTIVE']
                xdict['RDCWarehouseID'] = x['RDCWAREHOUSEID']
                xdict['WarehouseType'] = x['WAREHOUSETYPE']
                xdict['PartTAT'] = x['PARTTAT']
                xdict['CreatedOn'] = x['CREATEDON']
                xdict['CreatedBy'] = x['CREATEDBY']
                xdict['UpdatedOn'] = x['UPDATEDON']
                xdict['UpdatedBy'] = x['UPDATEDBY']
                if xdict['UpdatedBy'] is not None:
                    xdict['LogBy'] = xdict['UpdatedBy']
                else:
                    xdict['LogBy'] = xdict['CreatedBy']    
                xdict['LogByName'] = None
                for key, value in xdict.items():
                    if value=="":
                        xdict[key] = None
                resList.append(xdict)        
            return resList


        