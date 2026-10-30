from django.urls import path
from . import views

app_name = 'taches'

urlpatterns = [
    path('', views.board, name='board'),
    path('nouvelle/', views.tache_create, name='tache_create'),
    path('<int:pk>/modifier/', views.tache_update, name='tache_edit'),
    path('<int:pk>/supprimer/', views.tache_delete, name='tache_delete'),
    path('<int:pk>/deplacer/', views.tache_move, name='tache_move'),
]
