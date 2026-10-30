# dashboard/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from datetime import date
from . import reports
from django.core.cache import cache
from .services import (
    get_kpis,
    get_alertes,
    get_production_data,
    get_animaux_par_espece,
    get_recent_activities,
    get_finances,
    get_stock_evolution,
    get_depenses_par_produit,
    get_health_score,
    get_health_status,
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Vue principale du tableau de bord - V2 avec cache et nouveaux services"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # CACHE (60 secondes pour éviter les calculs trop fréquents)
        cache_key = f"dashboard_v2_{user.id}_{user.ferme.id}"
        data = cache.get(cache_key)
        
        if not data:
            # Récupérer les KPIs d'abord (nécessaires pour health_score)
            kpis = get_kpis(user)
            
            # Récupérer toutes les données via les services
            data = {
                'kpis': kpis,
                'alertes': get_alertes(user),
                'production_data': get_production_data(user),
                'animaux_par_espece': get_animaux_par_espece(user),
                'activites': get_recent_activities(user),
                'finances': get_finances(user),
                'stock_evolution': get_stock_evolution(user),
                'depenses_par_produit': get_depenses_par_produit(user),
                'health_score': get_health_score(kpis),
                'health_status': get_health_status(get_health_score(kpis)),
            }
            cache.set(cache_key, data, 60)  # 60 secondes
        
        context.update(data)
        return context


@login_required
def alertes(request):
    return render(request, 'dashboard/alertes.html', {'alertes': get_alertes(request.user, limit=100)})


@login_required
def rapports(request):
    return render(request, 'dashboard/rapports.html', {'lignes': reports.synthese_mensuelle(request.user.ferme)})


@login_required
def rapports_export(request):
    resp = HttpResponse(reports.export_xlsx(request.user.ferme, with_finances=request.user.role != 'EMPLOYE'),
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="fermeapp_synthese_{date.today():%Y%m%d}.xlsx"'
    return resp
