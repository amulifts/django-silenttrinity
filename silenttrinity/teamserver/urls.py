from django.urls import path
from . import views

app_name = 'teamserver'

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('user/info/', views.user_info, name='user_info'),
    path('users/', views.list_users, name='list_users'),
]