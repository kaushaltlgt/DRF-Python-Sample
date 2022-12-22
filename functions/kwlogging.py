import datetime, logging, socket, enum
from functions.querymethods import DBIDGENERATOR
from functions.aws_s3 import AWSS3
from schedules_list_map.models import GSPNWSLOGS, SQAPILogs
from django.http import HttpResponseServerError
from django.utils import timezone


class SimpleLogger:
    "to log API requests using custom parametres from the API views"
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def do_log(text_log, logtype=None):
        "method to write log to a file"
        rfh = logging.handlers.RotatingFileHandler(
            filename='logs/debug.log', 
            mode='a',
            maxBytes=5*1024*1024,
            backupCount=2,
            encoding=None,
            delay=0
        )
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)-25s %(levelname)-8s %(message)s",
            datefmt="%y-%m-%d %H:%M:%S",
            handlers=[
                rfh
            ]
        )
        logger = logging.getLogger('KW.ServiceQuick.Web.API')
        if logtype is None:
            logger.info(text_log)
        else:
            if logtype=='error':
                logger.error(text_log)
            elif logtype=='debug':
                logger.debug(text_log)
            elif logtype=='warn':
                logger.warning(text_log)
            else:
                logger.info(text_log)                
        

class AdvancedLogger:
    "log data to database and/or AWS S3"
    def __init__(self):
        pass

    def startlog(refNo, method, caller, reqXmlString, currentuserid):
        "get required arguments values to start logging"
        SimpleLogger.do_log("StartLog()...")
        try:
            row_id = DBIDGENERATOR.process_id('GSPNWSLOGS_SEQ')
            GSPNWSLOGS.objects.create(id=row_id, createdon=timezone.now(), createdby=currentuserid, refno=refNo,method=method,caller=caller)
        except Exception as e:
            print(e)
        # upload reqXmlString/json_string to AWS S3 bucket
        # AWS S3 code here
        try:
            subDirectoryInBucket = f'SQAPILogs/{datetime.date.today().strftime("%Y.%m")}'
            fileName = str(AdvancedLogger.getlogid(method, caller, currentuserid)) + '.rqst.json'
            aws = AWSS3()
            aws.WiteStringToS3(reqXmlString, subDirectoryInBucket, fileName)
        except Exception as e:
            SimpleLogger.do_log(f'Error: {e}')    
        return True 


    def stoplog(refNo, method, caller, reqXmlString, currentuserid, elapse):
        "to stop the logging by updating the current record"
        SimpleLogger.do_log("StopLog()...")
        GSPNWSLOGS.objects.filter(createdby=currentuserid,refno=refNo,method=method,caller=caller).update(callelapse=elapse, updatedby=currentuserid, updatedon=timezone.now())
        # AWS S3 code here
        try:
            subDirectoryInBucket = f'SQAPILogs/{datetime.date.today().strftime("%Y.%m")}'
            fileName = str(AdvancedLogger.getlogid(method, caller, currentuserid)) + '.rsps.json'
            aws = AWSS3()
            aws.WiteStringToS3(reqXmlString, subDirectoryInBucket, fileName)
        except Exception as e:
            SimpleLogger.do_log(f'Error: {e}')
        return True

    def getlogid(method, caller, currentuserid):
        "to get row ID for the lastest LOG based on given parameters"
        try:
            id = GSPNWSLOGS.objects.filter(createdby=currentuserid,method=method,caller=caller).order_by('-id')[0].id
        except:
            id = 0
        return id


class CallerAppEnum(enum.Enum):
    "values for different caller apps"
    UNKNOWN = 0
    SQ_AGENT = 1
    SQ_WAREHOUSE = 2
    SQ_DISPATCH = 3
    NSC = 4        


class BaseApiController:
    "functions related to saving of SQAPILogs" 
    ERROR_MSG_LENGTH = 255
    METHODS_ONLY_SQAGENT_USING = [
                                    "UserTicketsController",
                                    "UserWorkOrdersController",
                                    "RepairStartController",
                                    "PartsUsageController",
                                    "RepairDetailsController",
                                    "DefectCodesController",
                                    "RepairCodesController",
                                    "SchedulableDateController",
                                    "CloseWorkOrderController",
                                    "IsUserSOUpdatedController",
                                    "TechSummaryController",
                                    "WorkOrderHistoryController",
                                    "TechNoteController",
                                    "TechIncentiveController",
                                    "TechKPIController",
                                    "EmailReceiptController"
                                ] 

    MESSAGE_TO_UPDATE = "Please Update The App to New Version." 

    @staticmethod
    def CallerApp(request):
        "to know which app version is sending the request"
        app = request.META.get('HTTP_APP')
        SimpleLogger.do_log(f"app={app}", "debug")
        app = app.replace("-", "_")
        if app in CallerAppEnum.__members__:
            return CallerAppEnum[app]
        else:
            return CallerAppEnum.UNKNOWN.value

    @staticmethod
    def AppVersion(request):
        "return version of APP requesting for the service"
        return request.META.get('HTTP_APPVERSION') 

    @staticmethod
    def StartLog(CurrentUserID, refNo, method, caller, jsonString, callerApp=CallerAppEnum.UNKNOWN.value, appVersion=""):
        "to save logs in the table SQAPILOGS"
        SimpleLogger.do_log("StartLog()...", "debug")
        try:
            sqAPILog = {}
            sqAPILog['ID'] = DBIDGENERATOR.process_id("SQAPILOGS_SEQ")
            sqAPILog['CreatedOn'] = timezone.now()
            sqAPILog['CreatedBy'] = CurrentUserID
            sqAPILog['RefNo'] = refNo
            sqAPILog['Method'] = method
            sqAPILog['Caller'] = caller
            sqAPILog['startTime'] = timezone.now()
            sqAPILog['Server'] = socket.gethostname()
            sqAPILog['CallerApp'] = callerApp
            sqAPILog['AppVersion'] = appVersion
            SQAPILogs.objects.create(
                id = sqAPILog['ID'],
                createdon = sqAPILog['CreatedOn'],
                createdby = CurrentUserID,
                refno = refNo,
                method = method,
                caller = caller,
                server = sqAPILog['Server'],
                callerapp = callerApp,
                appversion = appVersion
            )
            # upload reqXmlString/json_string to AWS S3 bucket
            # AWS S3 code here 
            try:
                subDirectoryInBucket = f'SQAPILogs/{datetime.date.today().strftime("%Y.%m")}'
                fileName = f"{str(BaseApiController.getlogid(method, caller, CurrentUserID))}.rqst.json"
                aws = AWSS3()
                aws.WiteStringToS3(jsonString, subDirectoryInBucket, fileName)
            except Exception as e:
                SimpleLogger.do_log(f'Error: {e}', 'error')
            if method in BaseApiController.METHODS_ONLY_SQAGENT_USING:
                if callerApp==CallerAppEnum.UNKNOWN.value and not appVersion:
                    return HttpResponseServerError(BaseApiController.MESSAGE_TO_UPDATE)
            return sqAPILog
        except Exception as e:
            SimpleLogger.do_log(f"Error in StartLog(): {str(e)}", "debug")
            return None 


    @staticmethod
    def StopLog(CurrentUserID, sqAPILog, jsonString, errCode="", errMsg=""):
        "to update logs in the table SQAPILOGS based on ID"
        SimpleLogger.do_log("StopLog()...", "debug")
        try:
            sqAPILog['ErrorCode'] = errCode
            sqAPILog['ErrorMsg'] = errMsg[0:BaseApiController.ERROR_MSG_LENGTH] if len(errMsg) > BaseApiController.ERROR_MSG_LENGTH else errMsg
            sqAPILog['CallElapse'] = (timezone.now() - sqAPILog['startTime']).seconds * 100 #ticks
            SQAPILogs.objects.filter(id = sqAPILog['ID']).update(
                            updatedon = timezone.now(),
                            updatedby = CurrentUserID,
                            errorcode = sqAPILog['ErrorCode'],
                            errormsg = sqAPILog['ErrorMsg'],
                            callelapse = sqAPILog['CallElapse']
                        )
            # upload reqXmlString/json_string to AWS S3 bucket
            # AWS S3 code here
            try:
                subDirectoryInBucket = f'SQAPILogs/{datetime.date.today().strftime("%Y.%m")}'
                fileName = f"{str(sqAPILog['ID'])}.rsps.json"
                aws = AWSS3()
                aws.WiteStringToS3(jsonString, subDirectoryInBucket, fileName)
            except Exception as e:
                SimpleLogger.do_log(f'Error: {e}', 'error')            
            return sqAPILog
        except Exception as e:
            SimpleLogger.do_log(f"Error in StopLog(): {str(e)}", "debug")
            return None

    @staticmethod 
    def getlogid(method, caller, currentuserid):
        "to get row ID for the lastest LOG based on given parameters"
        try:
            id = SQAPILogs.objects.filter(createdby=currentuserid,method=method,caller=caller).order_by('-id')[0].id
        except:
            id = 0
        return id                                                                      


