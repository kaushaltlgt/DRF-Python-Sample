import uuid, datetime, msal, requests
from Crypto.Cipher import DES3
from .models import OauthAccessTokens
from nsp_user.models import Nspusers
from django.conf import settings
from nsp_user.auth_helper import load_cache, save_cache
from functions.querymethods import DBIDGENERATOR
from django.utils import timezone

class TokenGeneration: #currently this class is not being used, please refer to the class AzureAuthentication
    "generate a new token for the user if it is expired or not present else return existing token"
    def __init__(self) -> None:
        pass
    def generate(request, uid):
        local_ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
        machine_name = request.META.get("REMOTE_HOST", "unknown") 

        #print(request.META)
        # checking if token already created and is not expired
        today = timezone.now()
        checktoken = OauthAccessTokens.objects.filter(user_id=uid)
        if checktoken.exists():
            token = OauthAccessTokens.objects.filter(user_id=uid, expires_at__gte=today)[0].scopes
            return token
        else:
            token_string = "MOolwHo2XSbuQVVDfb72Y7JTMXgeHez0bq8{_ENCLOSE_}1{_SPLIT_}" + local_ip + "{_SPLIT_}" + machine_name + "{_ENCLOSE_}jEn5eHNLAAlQWeqhLTrXNsHaZhyID"
            #print(token_string)
            #Encrypting the token using DES3
            masterkey = 'geedsgWe381#8&^%123jkQbZ'
            iv_list = [63, -115, -43, -41, -66, -82, -45, -94]
            iv_string = ''
            for x in iv_list:
                iv_string += str(x)
            cipher = DES3.new(masterkey, DES3.MODE_EAX, bytes(iv_string, 'utf-8'))
            enctext = cipher.encrypt(bytes(token_string, 'utf-8'))    
            token = enctext.hex().strip().upper()
            #saving the token in the database table
            id_string = str(uuid.uuid4())
            today = timezone.now()
            next_date = datetime.timedelta(days=7)
            expires_at = today + next_date #expires after 7 days
            OauthAccessTokens.objects.create(id=id_string,user_id=uid,scopes=token, expires_at=expires_at, client_id=uid, revoked=0, name="user_token")
            return token
     

class KWAuthentication:
    "method to be used on each api endpoint to verify if user is authenticated and own a valid token"
    def __init__(self) -> None:
        pass
    def authenticate(request):
        #print(request.META)
        content_type = request.META.get('CONTENT_TYPE')
        kw_token = request.META.get('HTTP_KW_TOKEN')
        app = request.META.get('HTTP_APP')
        app_version = request.META.get('HTTP_APPVERSION')
        today = timezone.now()
        checktoken = OauthAccessTokens.objects.filter(scopes=kw_token, expires_at__gte=today)
        if not checktoken.exists():
            return {'message':'token invalid or expired'}
        else:
            return True    

    @staticmethod
    def getcurrentuser(request):
        "search user_id based on the token supplied by the device"
        try:
            token = request.META.get('HTTP_KW_TOKEN')
            user_id = OauthAccessTokens.objects.filter(scopes=token)[0].user_id
            return user_id
        except:
            return '' 

    @staticmethod
    def getcurrentusername(request):
        "search user_id based on the token supplied by the device"
        try:
            token = request.META.get('HTTP_KW_TOKEN')
            user_id = OauthAccessTokens.objects.filter(scopes=token)[0].user_id
            username = Nspusers.objects.filter(user_id=user_id)[0].email
            return username
        except:
            return ''


class AzureAuthentication:
    "to authenticate an user against the Azure Active Directory and get the access token with other credentials"
    @staticmethod
    def get_token(request, username, password):
        "use the provided credentials to signin and get the access token"
        authority = 'https://login.microsoftonline.com/' + settings.TENANT_ID
        app_secret = settings.APP_SECRET
        app_id = settings.CLIENT_ID
        cache = load_cache(request)
        auth_app = msal.ConfidentialClientApplication(
        app_id,
        authority=authority,
        client_credential=app_secret,
        token_cache=cache
        )
        result = auth_app.acquire_token_by_username_password(username=username, password=password, scopes=["User.Read"])
        if "access_token" in result:
            save_cache(request, cache)
        return result

    @staticmethod
    def save_token(username, access_token):
        "save the access token obtained after successful Azure AD Authentication if not already saved"
        check_user = Nspusers.objects.filter(email=username) #checking username
        if check_user.exists():
            uid = check_user[0].userid
        else:
            userid = DBIDGENERATOR.process_id("NSPUSERS_SEQ")
            get_name = AzureAuthentication.get_user_name(access_token)
            if get_name['displayName'] is not None:
                names = get_name['displayName'].split()
                try:
                    firstname = names[0]
                    lastname = names[1]
                except:
                    firstname = names[0]
                    lastname = None
            elif get_name['givenName'] is not None:
                firstname = get_name['givenName']
                lastname = None
            else:
                firstname = None
                lastname = None                
            Nspusers.objects.create(userid=userid, email=username, firstname=firstname, lastname=lastname, createdon=timezone.now(), createdby=userid) #save username(email) with other details
            uid = userid    
        #saving/updating the token in the database table
        id_string = str(uuid.uuid4())
        today = timezone.now()
        token = access_token
        next_date = datetime.timedelta(days=15)
        expires_at = today + next_date #expires after 15 days
        checktoken = OauthAccessTokens.objects.filter(user_id=uid)
        if checktoken.exists():
            OauthAccessTokens.objects.filter(user_id=uid, expires_at__lte=today).update(scopes=token, expires_at=expires_at, updated_at=timezone.now())
        else:
            OauthAccessTokens.objects.create(id=id_string,user_id=uid,scopes=token, expires_at=expires_at, client_id=uid, revoked=0, name=username)
        return True    

    @staticmethod
    def get_user_name(access_token):
        "query Microsoft Graph API to get displayname or fullname for the user for whom access token was issued"
        API_URL = "https://graph.microsoft.com/v1.0/me"
        headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
                }

        response = requests.get(url=API_URL,
                                headers=headers,
                                verify=False)
        response_data = response.json()                        
        result = {'displayName':response_data.get('displayName'),'givenName':response_data.get('givenName')}
        return result                                    


        