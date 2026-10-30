from django.urls import path
from . import views

app_name = 'personnel'

urlpatterns = [
    path('', views.staff_list, name='staff_list'),
    path('nouveau/', views.staff_create, name='staff_create'),
    path('<int:pk>/modifier/', views.staff_update, name='staff_edit'),
]
