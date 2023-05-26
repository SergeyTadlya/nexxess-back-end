from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from .views import TestView
from . import views



app_name = 'authentication'

urlpatterns = [
    path('', views.main, name='main'),
    path('test/', TestView.as_view(), name='test'),
    path('profile/', views.profile_view, name='profile'),
    path('accounts/login/', views.MyLoginView.as_view(), name='account_login'),
    path('login/verification/', views.verification, name='verification'),
    path('accounts/logout/', views.MyLogoutView.as_view(), name='account_logout'),
    path('accounts/googlelogin/', views.google_login, name='google_login'),
    path('webhook/task/', views.webhook_task, name='webhook_task'),
    path('webhook/invoice/', views.webhook_invoice, name='webhook_invoice'),
    path('webhook/service_section/', views.webhook_service_section),
    path('webhook/task/comment_add/', views.webhook_task_comment, name='webhook_task_comment'),
    path('ajax_errors/', views.ajax_errors),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
