from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


app_name = 'tickets'

urlpatterns = [
    # tickets pages (b24 tasks)
    path('', views.tasks, name='tasks'),
    path('detail/<int:id>/', views.task_detail, name="task_detail"),
    path('create-task/', views.create_bitrix_task, name='create_task'),
    path('list', views.task_data, name='list'),
    path('ajax_tasks_filter/', views.ajax_tasks_filter)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
