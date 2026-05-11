from django.urls import path
from . import views

app_name = 'predictor'

urlpatterns = [
    path('', views.home, name='home'),
    # Microbiology section
    path('micro/salmonella/', views.salmonella_predict, name='salmonella'),
    path('micro/ecoli/', views.ecoli_predict, name='ecoli'),
    path('micro/saureus/', views.saureus_predict, name='saureus'),
    # Biochemistry section
    path('bio/egg/', views.egg_predict, name='egg'),
    path('bio/egg/calculate/', views.egg_calculator, name='egg_calculate'),
    path('bio/biomass/', views.biomass_predict, name='biomass'),
]