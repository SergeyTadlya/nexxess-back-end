from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
    path('webhook/', views.b24_webhook, name='b24_webhook'),
    # invoices pages
    path('invoices/', views.invoices, name='invoices'),
    path('invoice/<int:id>/', views.invoice_detail, name="invoice_detail"),
    # support pages
    path('support/', views.support, name='support'),
    # services pages
    path('services/', views.services, name='services'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)