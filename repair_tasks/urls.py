from . import views
from django.urls import path

urlpatterns = [
    path('servicequick/api/rareasoncodes', views.RAReasonCodesController.as_view(), name="rareasoncodes"),
    path('servicequick/api/rashipping', views.RAShippingController.as_view(), name="rashipping"),
    path('servicequick/api/rarequest', views.RAIssueRequestController.as_view(), name="rarequest"),
    path('servicequick/api/CoreShipping', views.CoreShippingController.as_view(), name="CoreShipping"),
    path('servicequick/api/RDCWarehouses', views.RDCWarehousesController.as_view(), name="RDCWarehouses"),
    path('servicequick/api/rauploadpicture', views.RAUploadPictureController.as_view(), name="rauploadpicture"),
]
