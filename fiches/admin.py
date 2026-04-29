
from django.contrib import admin
from .models import Fiche


@admin.register(Fiche)
class FicheAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'prenom', 'age', 'sexe', 'profession', 'menage', 'adresse', 'date_saisie', 'saisi_par']
    list_filter   = ['sexe', 'profession', 'revenu', 'logement', 'statut_logement', 'date_saisie']
    search_fields = ['nom', 'prenom', 'adresse', 'profession', 'obs']
    readonly_fields = ['date_saisie', 'date_modif', 'saisi_par']
    fieldsets = [
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'age', 'sexe', 'niveau')
        }),
        ('Ménage & logement', {
            'fields': ('menage', 'logement', 'statut_logement', 'adresse')
        }),
        ('Activité professionnelle', {
            'fields': ('profession', 'revenu')
        }),
        ('Besoins & observations', {
            'fields': ('besoins', 'obs')
        }),
        ('Méta', {
            'fields': ('date_saisie', 'date_modif', 'saisi_par'),
            'classes': ('collapse',)
        }),
    ]
