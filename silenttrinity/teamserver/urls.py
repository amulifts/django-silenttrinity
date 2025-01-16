from django.urls import path
from . import views

app_name = 'teamserver'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sessions/', views.sessions_view, name='sessions'),
    path('users/', views.users_view, name='users'),
]