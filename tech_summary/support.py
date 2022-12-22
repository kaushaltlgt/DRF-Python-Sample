#supporting functions
import requests
from tech_summary.models import NspRoutes, AndroidDevices
from nsp_user.models import Nspusers
from functions.kwlogging import SimpleLogger
from django.conf import settings

class TechSupport:
    def __init__(self) -> None:
        pass

    @staticmethod
    def GetTechnicianRoute(userId, date):
        "to get technician route by running a sql query"
        try:
            route = NspRoutes.objects.filter(technicianid=userId, routedate=date).order_by('-createdon')[0]
            res = {}
            res['RouteID'] = route.routeid
            res['TechnicianID'] = route.technicianid
            res['RouteDate'] = route.routedate
            res['Duration'] = route.duration
            res['Distance'] = route.distance
            res['SOCount'] = route.socount
            res['SOList'] = route.solist
            res['PolylinePoints'] = route.polylinepoints
            res['GoogleJson'] = route.googlejson
            res['CreatedOn'] = route.createdon
            res['CreatedBy'] = route.createdby
            res['UpdatedOn'] = route.updatedon
            res['UpdatedBy'] = route.updatedby
            if route.updatedby is not None:
                res['LogBy'] = route.updatedby
            else:
                res['LogBy'] = route.createdby    
            res['LogByName'] = None #this is always null as per C# code
            return res
        except:
            return None

    @staticmethod
    def RebuildTechnicianRouting(token, userId, date):
        "send an XML request to the remote server to rebuild routing"
        SimpleLogger.do_log("RebuildTechnicianRouting()...")
        soapAction = "\"http://office.kwinternational.com/RebuildTechnicianRouting\""
        xml_string = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
                        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
                        <soap:Body>
                        <RebuildTechnicianRouting xmlns=\"http://office.kwinternational.com/\">
                        <sToken>{token}</sToken>
                        <iTechID>{userId}</iTechID>
                        <sDate>{date}</sDate>
                        </RebuildTechnicianRouting>
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
        result = response
        SimpleLogger.do_log(f"result= {result}")
        return result

    @staticmethod
    def GetFieldTechnicians(warehouseId):
        "to get data from the table NSPUsers based on warehouseId"
        data = Nspusers.objects.filter(warehouseid=warehouseId,isfieldtech=True,nspstatus=1).order_by('email')
        resList = []
        for ns in data:
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
            for key, value in resultList.items():
                if value=="":
                    resultList[key] = None
            resList.append(resultList)
        return resList

    @staticmethod
    def GetDevicesByUserID(appId, userId):
        "to get list of devices based on AppID and UserID from the table AndroidDevices"
        data = AndroidDevices.objects.filter(appid=appId, remoteuser=userId).order_by('-updatedon')
        resList = []
        for x in data:
            ad = {}
            ad['AppID'] = x.appid
            ad['DeviceID'] = x.deviceid
            ad['DeviceName'] = x.devicename
            ad['DeviceVersion'] = x.deviceversion
            ad['DeviceModel'] = x.devicemodel
            ad['DeviceSerial'] = x.deviceserial
            ad['RemoteUser'] = x.remoteuser
            ad['RemoteAddr'] = x.remoteaddr
            ad['UserAgent'] = x.useragent
            ad['RegistrationID'] = x.registrationid
            ad['Latitude'] = x.latitude
            ad['Longitude'] = x.longitude
            ad['CreatedOn'] = x.createdon
            ad['UpdatedOn'] = x.updatedon
            resList.append(ad)
        return resList

    @staticmethod
    def GetLastUserDevice(userId):
        "to get list of devices whatever present in the last row"
        devices = TechSupport.GetDevicesByUserID(settings.SQ_AGENT_APP_ID, userId)
        if len(devices)==0:
            devices = TechSupport.GetDevicesByUserID(settings.NSP_AGENT_APP_ID, userId)
        if len(devices) > 0:
            return devices[0]
        else:
            return None                                          



