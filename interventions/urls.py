"""
URLs for interventions app.
"""
from django.urls import path
from . import views

app_name = 'interventions'

urlpatterns = [
    # Interventions
    path('', views.intervention_list, name='intervention_list'),
    path('calendar/', views.intervention_calendar, name='intervention_calendar'),
    path('<str:intervention_id>/', views.intervention_detail, name='intervention_detail'),
    
    # Techniciens
    path('technician/<int:technician_id>/', views.technician_dashboard, name='technician_dashboard'),
    
    # Équipements
    path('equipment/', views.equipment_list, name='equipment_list'),
]
