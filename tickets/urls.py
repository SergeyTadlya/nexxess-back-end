from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from . import views


urlpatterns = [
    # tickets pages (b24 tasks)
    path('', views.tasks, name='tasks'),
    path('detail/<int:id>/', views.task_detail, name="task_detail"),
    path('list', views.task_data, name='list'),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
