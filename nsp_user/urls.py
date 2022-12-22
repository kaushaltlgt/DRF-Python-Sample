from . import views
from django.urls import path

urlpatterns = [
    path('', views.HomePage.as_view(), name="home"),
    #path('signin', views.sign_in, name='signin'),
    path('signout', views.sign_out, name='signout'),
    #path('callback', views.callback, name='callback'),
    path('mobilews/device.asmx', views.LoginView.as_view(), name="loginview"), #Sign IN by API
    path('mobilews/device.asmx/SignInRest', views.LoginView.as_view(), name="loginview"), #Sign IN by API
    path('servicequick/api/NSPUsers/<int:user_id>', views.get_user_by_id, name="get_user_by_id"), #NSPUsersController - ByID
    path('servicequick/api/NSPUsers/<userName>', views.get_user_by_username, name="get_user_by_username"), #NSPUsersController - ByNAME
    path('servicequick/api/NSPUsers', views.get_nsp_user, name="get_nsp_user"), #NSPUsersController
    path('servicequick/api/IsUserSOUpdated', views.IsUserSOUpdatedController.as_view(), name="isusersoupdated"),
    path('servicequick/api/nspUserLocation', views.NSPUserLocationController.as_view(), name="nspuserlocation"),
    path('servicequick/api/usertickets', views.UserTicketsController.as_view(), name="usertickets"),
]
