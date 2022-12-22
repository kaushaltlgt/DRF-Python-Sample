from . import views
from django.urls import path

urlpatterns = [
    path('servicequick/api/UserWorkorders', views.UserWorkOrdersController.as_view(), name="userworkorders"),
    path('servicequick/api/editappointment', views.EditAppointmentController.as_view(), name="editappointment"),
    path('servicequick/api/contactlog', views.ContactLogController.as_view(), name="contactlog"),
    path('servicequick/api/workschedule', views.WorkScheduleController.as_view(), name="workschedule"),
    path('servicequick/api/inventorysurvey', views.InventorySurveyController.as_view(), name="inventorysurvey"),
    path('servicequick/api/workorders/<id>', views.WorkOrdersController.as_view(), name="workorders"),
    path('servicequick/api/TwilioDebugger', views.TwilioDebuggerController.as_view(), name="twiliodebugger"),
    path('servicequick/api/inventorylist', views.InventoryListController.as_view(), name="inventorylist"),
    path('servicequick/api/mmscontroller', views.MmsController.as_view(), name="mmscontroller"),
]
