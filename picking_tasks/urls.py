from . import views
from django.urls import path

urlpatterns = [
    path('servicequick/api/pickingbatches', views.PickingBatchesController.as_view(), name="pickingbatches"),
    path('servicequick/api/pickinglabels/<id>', views.PickingLabelsController.as_view(), name="pickinglabels"),
    path('servicequick/api/receivinglabels/<id>', views.ReceivingLabelsController.as_view(), name="receivinglabels"),
]
