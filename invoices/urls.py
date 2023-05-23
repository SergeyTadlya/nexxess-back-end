from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    # invoices pages
    path('', views.invoices, name='invoices'),
    path('detail/<int:id>/', views.invoice_detail, name="invoice_detail"),
    path('invoices/<int:id>/pdf/', views.create_invoice_pdf, name='create_invoice_pdf'),
    path('create_payment_link/', views.create_payment_link),
    path('complete/', views.complete_payment_link),
    path('ajax_filter/', views.ajax_invoice_filter),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
