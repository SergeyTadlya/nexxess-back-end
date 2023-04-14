from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('authentication.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/v1/', include('api.urls')),
    path('invoices/', include('invoices.urls')),
    path('tickets/', include('tickets.urls')),
    path('services/', include('services.urls')),
    path('support/', include('support.urls')),
    path('telegram/', include('telegram_bot.urls')),
]
