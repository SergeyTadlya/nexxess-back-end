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
    # invoices pages
    path('invoice/', views.invoices, name='invoices'),
    path('invoice/<int:id>/', views.invoice_detail, name="invoice_detail"),
    # tickets pages (b24 tasks)
    path('ticket/', views.tasks, name='tasks'),
    path('ticket/<int:id>/', views.task_detail, name="task_detail"),
    # support pages
    path('support/', views.support, name='support'),
    # services pages
    path('services/', views.services, name='services'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)