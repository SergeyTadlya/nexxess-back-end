from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from . import views

app_name = 'authentication'

urlpatterns = [
    path('', views.main, name='main'),
    path('login/', views.login_view, name='login'),
    path('webhook/task/', views.webhook_task, name='webhook_task'),
    path('webhook/invoice/', views.webhook_invoice, name='webhook_invoice'),
    path('profile/', views.profile_view, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)