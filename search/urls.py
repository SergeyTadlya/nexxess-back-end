from django.urls import path
from . import views


urlpatterns = [
    path('service/', views.service_search, name='service_search'),
    path('service_detail/<int:pk>/', views.service_detail_search, name='servise_detail_search'),
    path('invoice/', views.invoice_search, name='invoice_search'),
    path('invoice_detail/<int:pk>/', views.invoice_detail_search, name='invoice_detail_search'),
    path('ticket/', views.ticket_search, name='ticket_search'),
    path('ticket_detail/<int:pk>/', views.ticket_detail_search, name='ticket_detail_search'),
    path('general/', views.general_search, name='general_search'),
    path('general_detail/<int:pk>/', views.general_detail_search, name='general_detail_search'),
]