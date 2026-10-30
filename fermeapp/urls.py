"""fermeapp URL Configuration"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('core.urls', namespace='core')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('cheptel/', include('cheptel.urls', namespace='cheptel')),
    path('cultures/', include('cultures.urls', namespace='cultures')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('finances/', include('finances.urls', namespace='finances')),
    path('taches/', include('taches.urls', namespace='taches')),
    path('personnel/', include('personnel.urls', namespace='personnel')),
    path('stocks/', include('stocks.urls', namespace='stocks')),
    path('stock/', include(('stocks.urls', 'stocks'), namespace='stock_alias')),
]

handler403 = 'core.views.forbidden'
