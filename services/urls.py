from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from . import views

app_name = 'services'


urlpatterns = [
    # services pages
    path('', views.services, name='services'),
    path('my_services/', views.my_services, name='my_services'),
    path('create_invoice/', views.create_invoice, name='create_invoice'),
    path('about_service/<int:id>/', views.product_detail, name='product_detail'),
    path('service_1/', views.service_1, name='service1'),
    path('service_2/', views.service_2, name='service2'),
    path('service_3/', views.service_3, name='service3'),
    path('search/', include('search.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
