from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views
from .views import TestView


app_name = 'authentication'

urlpatterns = [
    path('', views.main, name='main'),
    path('accounts/login/', views.MyLoginView.as_view(), name='account_login'),
    path('test/', TestView.as_view(), name='test'),
    path('login/verification/', views.verification, name='verification'),
    path('webhook/task/', views.webhook_task, name='webhook_task'),
    path('webhook/invoice/', views.webhook_invoice, name='webhook_invoice'),
    path('profile/', views.profile_view, name='profile'),
    path('accounts/logout/', views.MyLogoutView.as_view(), name='account_logout'),
    path('ajax_errors/', views.ajax_errors),
    path('accounts/googlelogin/', views.google_login, name='google_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
