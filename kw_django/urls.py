from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    #path('admin/', admin.site.urls),
    #path('oauth2/', include('django_auth_adfs.urls')), #use oauth2/login for login using an account registered in Azure AD
    path('', include('nsp_user.urls')),
    path('', include('tech_summary.urls')),
    path('', include('schedules_list_map.urls')),
    path('', include('schedules_detail.urls')),
    path('', include('repair_tasks.urls')),
    path('', include('picking_tasks.urls')),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
