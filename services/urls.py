from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views

app_name = 'services'


urlpatterns = [
    # services pages
    path('', views.services, name='services'),
    path('about_service/<int:id>/', views.product_detail, name='product_detail'),
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('service_1/', views.service_1, name='service1'),
    path('service_2/', views.service_2, name='service2'),
    path('service_3/', views.service_3, name='service3'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
