"""
URLs for interventions app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Interventions
    path('', views.InterventionListCreateView.as_view(), name='intervention-list'),
    path('<int:pk>/', views.InterventionDetailView.as_view(), name='intervention-detail'),
    path('calendar/', views.InterventionCalendarView.as_view(), name='intervention-calendar'),
    path('stats/', views.intervention_stats_view, name='intervention-stats'),
    path('<int:pk>/start/', views.start_intervention_view, name='intervention-start'),
    path('<int:pk>/complete/', views.complete_intervention_view, name='intervention-complete'),
    
    # Intervention tasks
    path('tasks/', views.InterventionTaskListCreateView.as_view(), name='intervention-task-list'),
    path('tasks/<int:pk>/', views.InterventionTaskDetailView.as_view(), name='intervention-task-detail'),
    
    # Intervention documents
    path('documents/', views.InterventionDocumentListCreateView.as_view(), name='intervention-document-list'),
    path('documents/<int:pk>/', views.InterventionDocumentDetailView.as_view(), name='intervention-document-detail'),
    
    # Intervention notes
    path('notes/', views.InterventionNoteListCreateView.as_view(), name='intervention-note-list'),
    path('notes/<int:pk>/', views.InterventionNoteDetailView.as_view(), name='intervention-note-detail'),
]
