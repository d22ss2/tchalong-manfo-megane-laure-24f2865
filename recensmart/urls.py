
from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.me, name='me'),
    path('fiches/', views.FicheListCreateView.as_view(), name='fiches-list'),
    path('fiches/<int:pk>/', views.FicheDetailView.as_view(), name='fiches-detail'),
    path('stats/', views.stats, name='stats'),
    path('export/csv/', views.export_csv, name='export-csv'),
]
