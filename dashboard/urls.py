# dashboard/urls.py
from django.urls import path
from . import views
from .views import DashboardView

app_name = 'dashboard'

urlpatterns = [
    path('alertes/', views.alertes, name='alertes'),
    path('rapports/', views.rapports, name='rapports'),
    path('rapports/export/', views.rapports_export, name='rapports_export'),
    path('', DashboardView.as_view(), name='home'),
]