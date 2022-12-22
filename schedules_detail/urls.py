from . import views
from django.urls import path

urlpatterns = [
    path('servicequick/api/repairstart', views.RepairStartController.as_view(), name="repairstart"),
    path('servicequick/api/RepairDetails', views.RepairDetailsController.as_view(), name="repairdetails"),
    path('servicequick/api/PartsUsage', views.PartsUsageController.as_view(), name="partsusage"),
    path('servicequick/api/uploadpicture', views.UploadPictureController.as_view(), name="uploadpicture"),
    path('servicequick/api/WorkOrderHistory', views.WorkOrderHistoryController.as_view(), name="workorderhistory"),
    path('servicequick/api/SchedulableDate', views.SchedulableDateController.as_view(), name="schedulabledate"),
    path('servicequick/api/CloseWorkorder', views.CloseWorkOrderController.as_view(), name="closeworkorder"),
    path('servicequick/api/TechNote', views.TechNoteController.as_view(), name="technote"),
    path('servicequick/api/EmailReceipt', views.EmailReceiptController.as_view(), name="emailreceipt"),
    path('servicequick/api/partserials/<psid>', views.PartSerialsController.as_view(), name="partserials"),
    path('servicequick/api/partserials', views.PartSerialsController.as_view(), name="partserials"),
    path('servicequick/api/warehouses', views.WarehousesController.as_view(), name="warehouses"),
    path('servicequick/api/warehouses/<id>', views.WarehousesController.as_view(), name="warehousesbyid"),
    path('servicequick/api/movepart', views.MovePartController.as_view(), name="movepart"),
    path('servicequick/api/scheduledsqboxes', views.ScheduledSQBoxesController.as_view(), name="scheduledsqboxes"),
    path('servicequick/api/sqboxlabels', views.SQBoxLabelsController.as_view(), name="sqboxlabels"),
    path('servicequick/api/dos', views.DOsController.as_view(), name="dos"),
    path('servicequick/api/partseriallist', views.PartSerialListController.as_view(), name="partseriallist"),
    path('servicequick/api/dispatchtickets', views.DispatchTicketsController.as_view(), name="dispatchtickets"),
    path('servicequick/api/lastuserticket', views.LastUserTicketController.as_view(), name="lastuserticket"),
]
