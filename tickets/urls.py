from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from . import views


app_name = 'tickets'

urlpatterns = [
    path('', views.tasks, name='tasks'),
    path('list', views.task_data, name='list'),
    path('create-task/', views.create_bitrix_task, name='create_task'),
    path('detail/<int:id>/', views.task_detail, name="task_detail"),
    path('ajax_tasks_filter/', views.ajax_tasks_filter),
    path('send_user_message/', views.send_user_message, name="send_user_message"),
    path('search/', include('search.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
