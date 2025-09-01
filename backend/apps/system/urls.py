from django.urls import path
from . import views

app_name = 'system'

urlpatterns = [
    path('logs/', views.get_logs, name='get_logs'),
    path('logs/stats/', views.get_log_stats, name='get_log_stats'),
    path('info/', views.get_system_info, name='get_system_info'),
]
