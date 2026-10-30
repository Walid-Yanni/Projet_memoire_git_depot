from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('health/', views.health, name='health'),
    path('demo/', views.demo_login, name='demo_login'),
]
