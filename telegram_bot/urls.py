from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('', views.main, name='main'),
    path('setwebhook/', views.set_telegram_webhook, name='set_webhook')
]
