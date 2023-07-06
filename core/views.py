from django.shortcuts import render
from django.views.generic import TemplateView

# PAGINA DE INICIO
class HomeView(TemplateView):
    template_name = 'home.html'

# PAGINA DE PRECIOS
class PricingView(TemplateView):
    template_name = 'pricing.html'