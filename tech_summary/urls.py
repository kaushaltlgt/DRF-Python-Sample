from . import views
from django.urls import path

urlpatterns = [
    path('servicequick/api/TechSummary', views.TechSummaryController, name="techsummarycontroller"),
    path('servicequick/api/techKPI', views.TechKPIController, name="techkpicontroller"),
    path('servicequick/api/TechIncentive', views.TechIncentiveController.as_view(), name="techincentivecontroller"),
    path('servicequick/api/technicianroute', views.TechnicianRouteController.as_view(), name="technicianroute"),
    path('servicequick/api/technicians', views.TechniciansController.as_view(), name="technicians"),
]
