from django.conf import settings
from django.core.mail import send_mail

def sendmailoversmtp(toaddr, subject, body, fromaddr=None): #using django send_mail utility
   "script to send mail using SMTP server" 
   try:
      if fromaddr is None:
         fromaddr = settings.FROM_ADDRESS
      send_mail(subject, body, fromaddr, [toaddr], fail_silently=False, html_message=body)
      print('Email Sent!')
      return True
   except Exception as e:
      print('Something went wrong....... '+str(e))
      return False 