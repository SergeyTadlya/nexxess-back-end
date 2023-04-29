from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    # services pages
    path('', views.services, name='services'),
    path('about_service/<int:id>/', views.product_detail, name='product_detail')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
