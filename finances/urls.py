from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('export/', views.transaction_export, name='transaction_export'),
    path('nouvelle/', views.transaction_create, name='transaction_create'),
    path('<int:pk>/modifier/', views.transaction_update, name='transaction_edit'),
    path('<int:pk>/supprimer/', views.transaction_delete, name='transaction_delete'),
]
