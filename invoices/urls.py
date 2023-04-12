from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    # invoices pages
    path('', views.invoices, name='invoices'),
    path('detail/<int:id>/', views.invoice_detail, name="invoice_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)