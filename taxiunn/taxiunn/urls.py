from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clients/auth/', include('client_auth.urls')),
    path('clients', include('client_profile.urls')),
    path('drivers/auth/', include('driver_auth.urls')),
    path('admins/auth/', include('admin_auth.urls')),
    path('taxi_fare/', include('taxi_fare.urls')),
    path('order/', include('order_system.urls')),
    path('admins', include('admin_profile.urls')),
]
