import json
from django.http import HttpResponse, HttpResponseServerError, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from nsp_user.models import Nspusers
from django.views import View
from nsp_user.authentication import KWAuthentication
from datetime import date, datetime, timedelta
from functions.kwlogging import SimpleLogger, AdvancedLogger, BaseApiController
from functions.querymethods import SingleCursor, MultipleCursor
from tech_summary.support import TechSupport
from functions.xmlfunctions import get_xml_node
from nsp_user.support import DjangoOverRideJSONEncoder

def TechSummaryController(request):
    # GET /servicequick/api/TechSummary?TechId=$techId
    SimpleLogger.do_log(">>> Get()...")
    p1 = KWAuthentication
    authstat = p1.authenticate(request)
    if authstat is False:
        return JsonResponse({'message':'invalid headers'}, status=400)

    tech_id = request.GET.get('techID')
    pay_date_interval = 14

    CurrentUserID = KWAuthentication.getcurrentuser(request)
    jsonString = str(json.dumps({'tech_id':tech_id}))
    AppVersion = request.META.get('HTTP_APPVERSION')
    callerApp = BaseApiController.CallerApp(request) 
    sqAPILog = BaseApiController.StartLog(CurrentUserID, str(tech_id), "GET", "TechSummaryController", jsonString, callerApp, AppVersion)

    if authstat is not True:
        return JsonResponse(authstat, status=401)

    if tech_id is None:
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: techID')            
        return JsonResponse({'message':'Parameter not found: techID'}, safe=False, status=400)
    next_pay_date = get_next_pay_day()
    last_pay_date = get_next_pay_day() - timedelta(days=pay_date_interval)


    try:
        nsp_user = Nspusers.objects.get(userid=tech_id)
    except Exception as e:
        print(e)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Cannot find the technician: {tech_id}')            
        return JsonResponse({'message':f'Cannot find the technician: {tech_id}'}, safe=False, status=400)

    next_pay_date = next_pay_date.strftime("%Y-%m-%d")   
    last_pay_date = last_pay_date.strftime("%Y-%m-%d")
    print(next_pay_date)
    s_query = f"SELECT * FROM (SELECT SUM(DECODE(B.Status, 60, 1, 0)) AS Done, COUNT(*) AS TOTAL FROM OpWorkOrder W INNER JOIN OpBase B ON W.ID = B.ID 	WHERE NVL(W.StartDTime, W.AptStartDTime) >= TRUNC(CURRENT_DATE) AND NVL(W.StartDTime, W.AptStartDTime) < TRUNC(CURRENT_DATE) + 1 AND W.TechnicianID = {tech_id} AND B.Status <= 60 ) FULL OUTER JOIN (SELECT DECODE(LastTotal, 0, 0, ROUND(LastRedo / LastTotal, 4)) AS LastRRR, DECODE(CurrentTotal, 0, 0, ROUND(CurrentRedo / CurrentTotal, 4)) AS CurrentRRR , CurrentIncentive, LastIncentive    FROM (SELECT SUM(CASE WHEN Month = ADD_MONTHS(TRUNC(CURRENT_DATE, 'mm'), -1) AND IncentiveType = 1 AND Status = -1 THEN 1 ELSE 0 END) AS LastRedo, SUM(CASE WHEN Month = ADD_MONTHS(TRUNC(CURRENT_DATE, 'mm'), -1) AND IncentiveType = 1 AND Status IN(-1, 1) THEN 1 ELSE 0 END) AS LastTotal, SUM(CASE WHEN Month = TRUNC(CURRENT_DATE, 'mm') AND IncentiveType = 1 AND Status = -1 THEN 1 ELSE 0 END) AS CurrentRedo, SUM(CASE WHEN Month = TRUNC(CURRENT_DATE, 'mm') AND IncentiveType = 1 AND Status IN(-1, 1) THEN 1 ELSE 0 END) AS CurrentTotal, SUM(CASE WHEN PayDate = TO_DATE('{next_pay_date}', 'YYYY-MM-DD') THEN IncentiveAmount ELSE 0 END) AS CurrentIncentive, SUM(CASE WHEN PayDate = TO_DATE('{last_pay_date}', 'YYYY-MM-DD') THEN IncentiveAmount ELSE 0 END) AS LastIncentive FROM (SELECT TechID , IncentiveAmount, TRUNC(IncentiveDate, 'mm') AS Month  , IncenTiveWorkOrderID, IncentiveStatus, IncentiveType, PayDate, DECODE(IncentiveStatus, 10, 1, 11, 1, 20, -1, 21, -1, 40, -1, 41, -1, 0) AS Status, ROW_NUMBER() OVER (PARTITION BY PayDate, IncenTiveWorkOrderID, IncentiveType ORDER BY TechIncentiveID DESC) AS RN FROM NSPTechIncentives WHERE TechID = {tech_id})  WHERE RN = 1    ) ) ON 1 = 1 FULL OUTER JOIN ( 	SELECT ROUND(AVG(N.QoSRTSScore), 2) AS CurrentTS, ROUND(AVG(N.QoSRRSScore), 2) AS CurrentNPS, ROUND(AVG(N.QoSOCSScore), 2) AS CurrentCMI 	FROM OpTicket T INNER JOIN OpBase B ON T.ID = B.ID INNER JOIN OpBase NB ON T.ID = NB.PID AND NB.OpType = 10040000 INNER JOIN OpNote N ON NB.ID = N.ID AND N.NoteType = 3 WHERE T.LastWORepairResult = 1 AND B.Status >= 60 AND T.CompleteDTime IS NOT NULL AND T.CompleteDTime >= TRUNC(CURRENT_DATE, 'mm') AND T.TechID = {tech_id} ) ON 1 = 1 FULL OUTER JOIN ( SELECT ROUND(AVG(N.QoSRTSScore), 2) AS LastTS, ROUND(AVG(N.QoSRRSScore), 2) AS LastNPS, ROUND(AVG(N.QoSOCSScore), 2) AS LastCMI FROM OpTicket T INNER JOIN OpBase B ON T.ID = B.ID INNER JOIN OpBase NB ON T.ID = NB.PID AND NB.OpType = 10040000 INNER JOIN OpNote N ON NB.ID = N.ID AND N.NoteType = 3 	WHERE T.LastWORepairResult = 1 	AND B.Status >= 60 AND T.CompleteDTime IS NOT NULL AND T.CompleteDTime >= ADD_MONTHS(TRUNC(CURRENT_DATE, 'mm'), -1) AND T.CompleteDTime < TRUNC(CURRENT_DATE, 'mm') AND T.TechID = {tech_id} ) ON 1 = 1"
    
    try:
        #tech_s = TechSummary.objects.raw(s_query)
        #result = TechSummarySerializers(tech_s, many=False)
        result = SingleCursor.send_query(s_query)
        responseData = {}
        responseData['Date'] = datetime.today()
        try:
            responseData['Done'] = float(result['DONE'])
        except:
            responseData['Done'] = 0.0
        try:        
            responseData['Total'] = float(result['TOTAL'])
        except:
            responseData['Total'] = 0.0 
        try:       
            responseData['CurrentTS'] = float(result['CURRENTTS'])
        except:
            responseData['CurrentTS'] = None 
        try:       
            responseData['CurrentNPS'] = float(result['CURRENTNPS'])
        except:
            responseData['CurrentNPS'] = 0.0
        try:        
            responseData['CurrentCMI'] = float(result['CURRENTCMI'])
        except:
            responseData['CurrentCMI'] = 0.0
        try:        
            responseData['CurrentRRR'] = float(result['CURRENTRRR'])
        except: 
            responseData['CurrentRRR'] = 0.0 
        try:      
            responseData['LastTS'] = float(result['LASTTS'])
        except:
             responseData['LastTS'] = 0.0 
        try:        
            responseData['LastNPS'] = float(result['LASTNPS'])
        except:
            responseData['LastNPS'] = 0.0
        try:        
            responseData['LastCMI'] = float(result['LASTCMI'])
        except:
            responseData['LastCMI'] = 0.0
        try:        
            responseData['LastRRR'] = float(result['LASTRRR'])
        except:
            responseData['LastRRR'] = 0.0
        try:        
            responseData['CurrentIncentive'] = float(result['CURRENTINCENTIVE'])
        except:
            responseData['CurrentIncentive'] = 0.0
        try:        
            responseData['LastIncentive'] = float(result['LASTINCENTIVE'])
        except:
            responseData['LastIncentive'] = 0.0    
        #new_data = {key.title():value for key, value in result.items()} #converting keynames into title(first letter capitalized and others are small)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(responseData, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
    except Exception as e:
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Server Error: {e}')            
        return JsonResponse({'message':f'Server Error: {e}'}, safe=False, status=400)    


def get_next_pay_day(p_date=None):
    initial_pay_date = date(2019, 3, 22)
    if p_date is None:
        p_date = date.today()
    else:
        p_date = datetime.date(p_date)
    if (p_date - initial_pay_date).days < 0:
        return None
    d = (18 - ((p_date - initial_pay_date).days - 10) % 14)
    return p_date + timedelta(days=d)
    

def TechKPIController(request):
    "get KPI(key performance indicator) of a technician using Tech ID"
    # GET /servicequick/api/techKPI?TechID=$techId
    SimpleLogger.do_log(">>> Get()...")
    p1 = KWAuthentication
    authstat = p1.authenticate(request)
    tech_id = request.GET.get('techID')

    CurrentUserID = KWAuthentication.getcurrentuser(request)
    jsonString = str(json.dumps({'tech_id':tech_id}))
    AppVersion = request.META.get('HTTP_APPVERSION')
    callerApp = BaseApiController.CallerApp(request) 
    sqAPILog = BaseApiController.StartLog(CurrentUserID, str(tech_id), "GET", "TechKPIController", jsonString, callerApp, AppVersion)

    if authstat is not True:
        return JsonResponse(authstat, status=401)

    if tech_id is None or tech_id=='':
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: techID')            
        return JsonResponse({'message':'Parameter not found: techID'}, safe=False, status=400)

    try:
        tech_id = int(tech_id)
    except:
        pass       

    try:
        nsp_user = Nspusers.objects.get(userid=tech_id)
    except Exception as e:
        print(e)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Cannot find the technician: {str(tech_id)}')            
        return JsonResponse({'message':f'Cannot find the technician: {str(tech_id)}'}, safe=False, status=400)
    
    resultList = {}
    resultList['TechID'] = tech_id
    resultList['UserName'] = str(nsp_user.firstname) + ' ' + str(nsp_user.lastname)  

    s_query = f"SELECT MONTHS.Month, KPI.TS, KPI.NPS, KPI.CMI, DECODE(RRR.RepairedCount, 0, 0, Round(RRR.RedoCount / RRR.RepairedCount, 4)) AS RRR, DECODE(RATIO.TotalSO, 0, 0, ROUND(RATIO.RepairedSO / RATIO.TotalSO, 4)) AS RepairRatio FROM (SELECT TRUNC(Days, 'mm') AS Month FROM(SELECT TRUNC(ADD_MONTHS(CURRENT_DATE, -5), 'mm') + LEVEL - 1 AS Days FROM DUAL CONNECT BY LEVEL <= (TRUNC(CURRENT_DATE) - TRUNC(ADD_MONTHS(CURRENT_DATE, -5), 'mm') + 1)) GROUP BY TRUNC(Days, 'mm') ) MONTHS LEFT OUTER JOIN (SELECT TRUNC(T.CompleteDTime, 'mm') AS Month, ROUND(AVG(N.QoSRTSScore), 2) AS TS, ROUND(AVG(N.QoSRRSScore), 2) AS NPS, ROUND(AVG(N.QoSOCSScore), 2) AS CMI FROM OpTicket T INNER JOIN OpBase B ON T.ID = B.ID INNER JOIN OpBase NB ON T.ID = NB.PID AND NB.OpType = 10040000 INNER JOIN OpNote N ON NB.ID = N.ID AND N.NoteType = 3 WHERE T.LastWORepairResult = 1 AND B.Status >= 60 AND T.CompleteDTime IS NOT NULL AND T.CompleteDTime >= TRUNC(ADD_MONTHS(CURRENT_DATE, -5), 'mm') AND T.TechID = {tech_id} GROUP BY TRUNC(T.CompleteDTime, 'mm') ) KPI ON MONTHS.Month = KPI.Month LEFT OUTER JOIN (SELECT TRUNC(IncentiveDate, 'mm') AS Month, SUM(DECODE(Status, -1, 1, 0)) AS ReDoCount, SUM(DECODE(Status, -1, 1, 1, 1, 0)) AS RepairedCount FROM (SELECT TechID, IncentiveAmount, IncentiveDate, IncenTiveWorkOrderID, IncentiveStatus, DECODE(IncentiveStatus, 10, 1, 11, 1, 20, -1, 21, -1, 40, -1, 41, -1, 0) AS Status, ROW_NUMBER() OVER (PARTITION BY PayDate, IncenTiveWorkOrderID ORDER BY TechIncentiveID DESC) AS RN FROM NSPTechIncentives WHERE IncentiveType = 1 AND TechID = {tech_id} AND IncentiveDate >= ADD_MONTHS(TRUNC(CURRENT_DATE, 'mm'), -5)) WHERE RN = 1 GROUP BY TRUNC(IncentiveDate, 'mm') ) RRR ON MONTHS.MONTH = RRR.MONTH LEFT OUTER JOIN (SELECT TRUNC(NVL(W.StartDTime, W.AptStartDTime), 'mm') AS Month, SUM(DECODE(W.RepairResultCode, 1, 1, 0)) AS RepairedSO, COUNT(*) AS TotalSO FROM OpWorkOrder W INNER JOIN OpBase B ON W.ID = B.ID WHERE B.Status = 60 AND NVL(W.StartDTime, W.AptStartDTime) >= ADD_MONTHS(TRUNC(CURRENT_DATE, 'mm'), -5) AND W.RepairFailCode NOT IN (1, 8, 9, 11, 12, 13, 14, 15) AND W.TechnicianID = {tech_id} GROUP BY TRUNC(NVL(W.StartDTime, W.AptStartDTime), 'mm') ) RATIO ON MONTHS.Month = RATIO.Month ORDER BY MONTHS.Month ASC"

    try:
        result = MultipleCursor.send_query(s_query)
        KPIList = []
        if type(result) is str or len(result)==0:
            queryres = {}
            queryres['Month'] = 0.0
            queryres['TS'] = 0.0
            queryres['NPS'] = 0.0
            queryres['CMI'] = 0.0
            queryres['RRR'] = 0.0
            queryres['RepairRatio'] = 0.0
            KPIList.append(queryres)
        else:
            for result in result:
                for key, value in result.items():
                    if value is None:
                        value = 0.0
                    result[key] = value    
                queryres = {}
                queryres['Month'] = result.get('MONTH')
                try:       
                    queryres['TS'] = float(result.get('TS'))
                except:
                    queryres['TS'] = 0.0
                try:        
                    queryres['NPS'] = float(result.get('NPS'))
                except:
                    queryres['NPS'] = 0.0 
                try:       
                    queryres['CMI'] = float(result.get('CMI'))
                except:
                    queryres['CMI'] = 0.0
                try:        
                    queryres['RRR'] = float(result.get('RRR'))
                except:
                    queryres['RRR'] = 0.0
                try:        
                    queryres['RepairRatio'] = float(result.get('REPAIRRATIO'))
                except:
                    queryres['RepairRatio'] = 0.0    
                KPIList.append(queryres)
        resultList['ListSize'] = len(result)                
        resultList['List'] = KPIList
        resultList['LogID'] = BaseApiController.getlogid("GET", "TechKPIController", CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)
    except Exception as e:    
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Server Error: {e}')            
        return JsonResponse({'message':f'Server Error: {e}'}, safe=False, status=400)


class TechIncentiveController(View):
    "method to get incentives for a technician"
    def get(self, request):
        # GET  /servicequick/api/TechIncentive?TechID=$techId
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)

        tech_id = request.GET.get('techID')

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'tech_id':tech_id}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(tech_id), "GET", "TechIncentiveController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        if tech_id is None or tech_id=='':
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Parameter not found: techID')            
            return JsonResponse({'message':'Parameter not found: techID'}, safe=False, status=400)

        try:
            tech_id = int(tech_id)
        except:
            pass       

        try:
            ns = Nspusers.objects.get(userid=tech_id)
        except Exception as e:
            print(e)
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg=f'Cannot find the technician: {str(tech_id)}')            
            return JsonResponse({'message':f'Cannot find the technician: {str(tech_id)}'}, safe=False, status=400)
        

        resultList = {}
        resultList['TechID'] = tech_id
        if ns.email:
            try:
                resultList['UserName'] = str(ns.email).split('@')[0]
            except:
                resultList['UserName'] = ns.email
        else:
            resultList['UserName'] = None     
        
        PAY_DATE_INTERVAL = 14
        #GetTechIncentiveTickets
        payDate = get_next_pay_day()
        payDate = f"TO_DATE('{payDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        s_query = f"SELECT DECODE(I.IncentiveType, 2, 'Mileage', T.TicketNo) AS TicketNo , NVL(W.FinishDTime, NVL(W.StartDTime, W.AptStartDTime)) AS SODTime, I.IncentiveAmount AS Incentive , DECODE(I.IncentiveType, 2, '' ,DECODE(W.SealLevel , 0, 'Not Major' , 1, 'Possible Seal' , 2, 'Seal' , 3, 'TV Over 65' , 4, 'Tub' , 5, 'Wall Oven' , '') ) AS JobType FROM (SELECT IncentiveAmount , IncenTiveWorkOrderID , IncentiveStatus , IncentiveDate , IncentiveType , PayDate , ROW_NUMBER() OVER(PARTITION BY PayDate, IncenTiveWorkOrderID, IncentiveType ORDER BY TechIncentiveID DESC) AS RN FROM NSPTechIncentives WHERE TechID = {tech_id} AND PayDate = {payDate} ) I INNER JOIN OpWorkOrder W ON I.IncentiveWorkOrderID = W.ID INNER JOIN OpBase B ON W.ID = B.ID INNER JOIN OpTicket T ON B.PID = T.ID WHERE I.RN = 1 ORDER BY TRUNC(NVL(W.FinishDTime, NVL(W.StartDTime, W.AptStartDTime))) ASC , I.IncentiveType ASC , NVL(W.FinishDTime, NVL(W.StartDTime, W.AptStartDTime)) ASC"
        try:
            IncentiveTickets = []
            GetTechIncentiveTickets = MultipleCursor.send_query(s_query)
            if type(GetTechIncentiveTickets) is str:
                GetTechIncentiveTickets = []
            else:
                for i in GetTechIncentiveTickets:
                    techtickets = {}
                    techtickets['TicketNo'] = i['TICKETNO']
                    techtickets['SODTime'] = i['SODTIME']
                    try:
                        techtickets['Incentive'] = float(i['INCENTIVE']) 
                    except:
                        techtickets['Incentive'] = i['INCENTIVE']    
                    techtickets['JobType'] = i['JOBTYPE']
                    IncentiveTickets.append(techtickets)
            resultList['IncentiveTickets'] = IncentiveTickets             
        except Exception as e:    
            return HttpResponseBadRequest(f'Server Error: {e}')
        #GetTechIncentive    
        payDate = get_next_pay_day() - timedelta(days = PAY_DATE_INTERVAL * 5)
        payDate = f"TO_DATE('{payDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        s_query = f"SELECT PAYDATES.PayDate, ICTV.Incentive FROM (SELECT DISTINCT PayDate FROM NSPTechIncentives WHERE PayDate >= {payDate} ) PAYDATES LEFT OUTER JOIN (SELECT PayDate, SUM(IncentiveAmount)AS Incentive FROM (SELECT TechID, IncentiveAmount, IncenTiveWorkOrderID, IncentiveStatus, IncentiveType, PayDate, ROW_NUMBER() OVER(PARTITION BY PayDate, IncenTiveWorkOrderID, IncentiveType ORDER BY TechIncentiveID DESC) AS RN FROM NSPTechIncentives WHERE TechID = {tech_id} AND PayDate >= {payDate}) WHERE RN = 1 GROUP BY PayDate ) ICTV ON PAYDATES.PayDate = ICTV.PayDate ORDER BY PAYDATES.PayDate"
        try:
            techList = []
            GetTechIncentive = MultipleCursor.send_query(s_query)
            if type(GetTechIncentive) is str:
                GetTechIncentive = []
            else:
                for i in GetTechIncentive:
                    techincentive = {}
                    techincentive['PayDate'] = i['PAYDATE']
                    try:
                        techincentive['Incentive'] = float(i['INCENTIVE'])
                    except:
                        techincentive['Incentive'] = i['INCENTIVE']   
                    techList.append(techincentive)
            resultList['ListSize'] = len(techList)        
            resultList['List'] = techList             
        except Exception as e:    
            return HttpResponseBadRequest(f'Server Error: {e}')    
        #GetTechLastIncentive
        payDate = get_next_pay_day() - timedelta(days = PAY_DATE_INTERVAL)
        payDate = f"TO_DATE('{payDate.strftime('%Y-%m-%d')}', 'YYYY-MM-DD')"
        s_query = f"SELECT PayDate , COUNT(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 11 THEN 1 END) AS PaidCount , SUM(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 11 THEN IncentiveAmount END) AS PaidAmount , COUNT(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 21 THEN 1 END) AS DeductedCount , SUM(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 21 THEN IncentiveAmount END) AS DeductedAmount , COUNT(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 30 THEN 1 END) AS NotPayableCount , COUNT(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 41 THEN 1 END) AS OmittedCount , SUM(CASE WHEN IncentiveType = 1 AND IncentiveStatus = 41 THEN IncentiveAmount END) AS OmittedAmount , COUNT(CASE WHEN IncentiveType = 2 AND IncentiveStatus = 11 THEN 1 END) AS MileageCount , SUM(CASE WHEN IncentiveType = 2 AND IncentiveStatus = 11 THEN IncentiveAmount END) AS MileageAmount FROM(SELECT TechID , IncentiveAmount , IncenTiveWorkOrderID , IncentiveStatus , IncentiveType , PayDate , ROW_NUMBER() OVER(PARTITION BY PayDate, IncenTiveWorkOrderID, IncentiveType ORDER BY TechIncentiveID DESC) AS RN FROM NSPTechIncentives WHERE TechID = {tech_id} AND PayDate = {payDate}) WHERE RN = 1 AND IncentiveStatus IN(11, 21, 30, 41) GROUP BY PayDate"
        try:
            GetTechLastIncentive = SingleCursor.send_query(s_query)
            if type(GetTechLastIncentive) is str or len(GetTechLastIncentive)==0:
                techins = {}
                techins['PayDate'] = None
                techins['PaidCount'] = None
                techins['PaidAmount'] = None 
                techins['DeductedCount'] = None
                techins['DeductedAmount'] = None
                techins['NotPayableCount'] = None
                techins['OmittedCount'] = None
                techins['OmittedAmount'] = None
                techins['MileageCount'] = None
                techins['MileageAmount'] = None
            else:
                i = GetTechLastIncentive
                techins = {}
                techins['PayDate'] = i['PAYDATE']
                try:
                    techins['PaidCount'] = float(i['PAIDCOUNT'])
                except:
                     techins['PaidCount'] = i['PAIDCOUNT']
                try:         
                    techins['PaidAmount'] = float(i['PAIDAMOUNT'])
                except:
                    techins['PaidAmount'] = i['PAIDAMOUNT'] 
                try:        
                    techins['DeductedCount'] = float(i['DEDUCTEDCOUNT'])
                except:
                    techins['DeductedCount'] = i['DEDUCTEDCOUNT']
                try:        
                    techins['DeductedAmount'] = float(i['DEDUCTEDAMOUNT'])
                except:
                    techins['DeductedAmount'] = i['DEDUCTEDAMOUNT']
                try:        
                    techins['NotPayableCount'] = float(i['NOTPAYABLECOUNT'])
                except:
                     techins['NotPayableCount'] = i['NOTPAYABLECOUNT'] 
                try:        
                    techins['OmittedCount'] = float(i['OMITTEDCOUNT'])
                except:
                    techins['OmittedCount'] = i['OMITTEDCOUNT']
                try:        
                    techins['OmittedAmount'] = float(i['OMITTEDAMOUNT'])
                except:
                    techins['OmittedAmount'] = i['OMITTEDAMOUNT'] 
                try:       
                    techins['MileageCount'] = float(i['MILEAGECOUNT'])
                except:
                    techins['MileageCount'] = i['MILEAGECOUNT'] 
                try:       
                    techins['MileageAmount'] = float(i['MILEAGEAMOUNT'])
                except:
                    techins['MileageAmount'] = i['MILEAGEAMOUNT']   
            resultList['LastIncentive'] = techins             
        except Exception as e:    
            return HttpResponseBadRequest(f'Server Error: {e}')
        resultList['LogID'] = BaseApiController.getlogid("GET", "TechIncentiveController", CurrentUserID) 
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)   
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200) 

@method_decorator(csrf_exempt, name='dispatch')
class TechnicianRouteController(View):
    "to update route for a technician"
    def get(self, request):
        "accept params in GET to process"
        # GET api/technicianroute?technicianId=12345&date=2022-02-22
        SimpleLogger.do_log(">>> Get()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        userId = request.GET.get('userId')
        date = request.GET.get('date')
        reqData = f"userId : {userId}, date : {date}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(userId), "GET", "TechnicianRouteController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        try:
            userId = int(userId)
        except:
            pass
        #Logging the parameters
        SimpleLogger.do_log(f"userId={userId}")
        SimpleLogger.do_log(f"date={date}")
        token = request.META.get('HTTP_KW_TOKEN')
        #Validation
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except:
            BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString, errCode='400', errMsg='Invalid date format. Must be in YYYY-MM-DD')            
            return JsonResponse({'message':'Invalid date format. Must be in YYYY-MM-DD'}, safe=False, status=400)
        #Checking the route
        route = TechSupport.GetTechnicianRoute(userId, date)
        if route is None:
            wsResult = TechSupport.RebuildTechnicianRouting(token, userId, date)
            SimpleLogger.do_log(f"xml.InnerText={wsResult.content}")
            from xml.etree.ElementTree import fromstring
            print('wsResult = ', wsResult.status_code)
            if wsResult.status_code==400 or wsResult.status_code==500:
                wsResult = '<ERROR>Server Error in processing soap request</ERROR>'
            else:
                try:    
                    wsResult = fromstring(wsResult.text) #converting soap response to XML document 
                except:
                    wsResult = '<ERROR>Server Error in processing soap request</ERROR>'    
            xml_error = get_xml_node(wsResult, 'ERROR') 
            if xml_error is not None or xml_error=='':
                return HttpResponseServerError(xml_error)
            else:
                SimpleLogger.do_log("The route has been updated successfully.")
                route = TechSupport.GetTechnicianRoute(userId, date)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)        
        return HttpResponse(route)
        
    def post(self, request):
        "to update technician route explicitly"
        # POST api/technicianroute?technicianId=12345&date=2022-02-22  explicit route update
        SimpleLogger.do_log(">>> Post()...")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        content = request.body.decode("utf-8")    
        try:
            received_json_data = json.loads(content)
        except:
            return HttpResponseBadRequest("invalid json request")     
        userId = received_json_data.get('userId')
        date = received_json_data.get('date')
        reqData = f"userId : {userId}, date : {date}"

        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, str(userId), "POST", "TechnicianRouteController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)
        try:
            userId = int(userId)
        except:
            pass
        #Logging the parameters
        SimpleLogger.do_log(f"userId={userId}")
        SimpleLogger.do_log(f"date={date}")
        token = request.META.get('HTTP_KW_TOKEN')
        #Validation
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except:
            return HttpResponseBadRequest('Invalid date format. Must be in YYYY-MM-DD')
        #Updating the route and getting the route details
        wsResult = TechSupport.RebuildTechnicianRouting(token, userId, date)
        SimpleLogger.do_log(f"xml.InnerText={wsResult.content}")
        from xml.etree.ElementTree import fromstring
        if wsResult.status_code==400 or wsResult.status_code==500:
            wsResult = '<ERROR>Server Error in processing soap request</ERROR>'
        else:
            try:    
                wsResult = fromstring(wsResult.text) #converting soap response to XML document 
            except:
                wsResult = '<ERROR>Server Error in processing soap request</ERROR>'    
        xml_error = get_xml_node(wsResult, 'ERROR')
        if xml_error is not None or xml_error=='':
            return HttpResponseServerError(xml_error)
        else:
            SimpleLogger.do_log("The route has been updated successfully.")
            route = TechSupport.GetTechnicianRoute(userId, date)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)    
        return HttpResponse(route)


class TechniciansController(View):
    "to get the list of technicians"
    def get(self, request):
        "accept request in GET to process"
        # API : GET /servicequick/api/technicians
        SimpleLogger.do_log(">>> Get()...", "debug")
        p1 = KWAuthentication
        authstat = p1.authenticate(request)
        warehouseId = request.GET.get('warehouseId') 
        strRoute = request.GET.get('route')
        routeDate = request.GET.get('routeDate')
        SimpleLogger.do_log(f"warehouseId={warehouseId}", "debug")
        SimpleLogger.do_log(f"includeRoute={strRoute}", "debug")  
        SimpleLogger.do_log(f"routeDate={routeDate}", "debug") 
        reqData = f"warehouseId : {warehouseId}, route : {strRoute}, routeDate : {routeDate}"
        CurrentUserID = KWAuthentication.getcurrentuser(request)
        jsonString = str(json.dumps({'reqData':reqData}))
        AppVersion = request.META.get('HTTP_APPVERSION')
        callerApp = BaseApiController.CallerApp(request) 
        sqAPILog = BaseApiController.StartLog(CurrentUserID, warehouseId, "GET", "TechniciansController", jsonString, callerApp, AppVersion)

        if authstat is not True:
            return JsonResponse(authstat, status=401)

        token = request.META.get('HTTP_KW_TOKEN')
        
        if (strRoute and strRoute=='1') or (strRoute and strRoute.lower()=='true'):
            includeRoute = True
        else:
            includeRoute = False
        if includeRoute and not routeDate:
            routeDate = datetime.today().strftime("%Y-%m-%d")
        #Getting list of nspUsers    
        nspUsers = TechSupport.GetFieldTechnicians(warehouseId)
        #Creating a list of technicians
        technicians = []
        for nspUser in nspUsers:
            techx = {}
            techx['WarehouseID'] = nspUser['WarehouseID']
            techx['UserID'] = nspUser['UserID']
            techx['UserName'] = nspUser['UserName']
            techx['FirstName'] = nspUser['FirstName']
            techx['LastName'] = nspUser['LastName']
            techx['Initial'] = nspUser['Initial']
            techx['FullName'] = nspUser['FullName']
            techx['Email'] = nspUser['Email']
            device = TechSupport.GetLastUserDevice(nspUser['UserID'])
            if device is not None:
                techx['DeviceID'] = device['DeviceID']
                techx['DeviceName'] = device['DeviceName']
                techx['DeviceModel'] = device['DeviceModel']
                techx['DeviceVersion'] = device['DeviceVersion']
                techx['Latitude'] = device['Latitude']
                techx['Longitude'] = device['Longitude']
                techx['Timestamp'] = device['UpdatedOn']
            if includeRoute:
                route = TechSupport.GetTechnicianRoute(nspUser['UserID'], routeDate)
                if route is None:
                    wsResult = TechSupport.RebuildTechnicianRouting(token, nspUser['UserID'], routeDate)
                    SimpleLogger.do_log(f"xml.InnerText={wsResult.content}")
                    from xml.etree.ElementTree import fromstring
                    print('wsResult = ', wsResult.status_code)
                    if wsResult.status_code==400 or wsResult.status_code==500:
                        wsResult = '<ERROR>Server Error in processing soap request</ERROR>'
                    else:
                        try:    
                            wsResult = fromstring(wsResult.text) #converting soap response to XML document 
                        except:
                            wsResult = '<ERROR>Server Error in processing soap request</ERROR>'    
                    xml_error = get_xml_node(wsResult, 'ERROR') 
                    if xml_error is not None or xml_error=='':
                        pass
                        #return HttpResponseServerError(xml_error)
                    else:
                        SimpleLogger.do_log("The route has been updated successfully.")
                        route = TechSupport.GetTechnicianRoute(nspUser['UserID'], routeDate)
                techx['Route'] = route
            #now append to the list    
            technicians.append(techx)
        #Preparing for the response data
        resultList = {}
        resultList['WarehouseID'] = warehouseId
        resultList['Route'] = includeRoute
        resultList['RouteDate'] = routeDate
        resultList['ListSize'] = len(technicians) 
        resultList['List'] = technicians
        resultList['LogID'] = BaseApiController.getlogid("GET", "TechniciansController", CurrentUserID)
        BaseApiController.StopLog(CurrentUserID, sqAPILog, jsonString)
        return JsonResponse(resultList, encoder=DjangoOverRideJSONEncoder, safe=False, status=200)                    




        
         
        





