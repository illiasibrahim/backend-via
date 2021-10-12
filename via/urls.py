from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('ad/', admin.site.urls),
    path('user/',include('user_app.api.urls')),
    path('hub/',include('hub_app.api.urls')),
    path('admin/',include('administrator.api.urls')),
    path('rider/',include('rider_app.api.urls')),
    path('order/',include('order.api.urls')),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT) 