
from django.db import models
from django.contrib.auth.models import User


class Fiche(models.Model):
    """Fiche de recensement RecenSmart"""

    # =========================================================
    # CHOIX
    # =========================================================
    SEXE_CHOICES = [
        ('Masculin', 'Masculin'),
        ('Féminin', 'Féminin'),
    ]

    NIVEAU_CHOICES = [
        ('', '—'),
        ('Aucun', 'Aucun'),
        ('Primaire', 'Primaire'),
        ('Secondaire', 'Secondaire'),
        ('Universitaire', 'Universitaire'),
        ('Formation technique', 'Formation technique'),
    ]

    LOGEMENT_CHOICES = [
        ('', '—'),
        ('Maison individuelle', 'Maison individuelle'),
        ('Appartement', 'Appartement'),
        ('Chambre en location', 'Chambre en location'),
        ('Habitat précaire', 'Habitat précaire'),
        ('Autre', 'Autre'),
    ]

    STATUT_LOGEMENT_CHOICES = [
        ('', '—'),
        ('Propriétaire', 'Propriétaire'),
        ('Locataire', 'Locataire'),
        ('Hébergé gratuitement', 'Hébergé gratuitement'),
        ('Autre', 'Autre'),
    ]

    PROFESSION_CHOICES = [
        ('', '—'),
        ('Agriculture / Élevage', 'Agriculture / Élevage'),
        ('Commerce informel', 'Commerce informel'),
        ('Fonctionnaire', 'Fonctionnaire'),
        ('Enseignant(e)', 'Enseignant(e)'),
        ('Artisan', 'Artisan'),
        ('Transporteur', 'Transporteur'),
        ('Salarié privé', 'Salarié privé'),
        ('Étudiant(e)', 'Étudiant(e)'),
        ('Sans emploi', 'Sans emploi'),
        ('Retraité(e)', 'Retraité(e)'),
        ('Autre', 'Autre'),
    ]

    REVENU_CHOICES = [
        ('', '—'),
        ('Moins de 50 000', 'Moins de 50 000'),
        ('50 000 – 100 000', '50 000 – 100 000'),
        ('100 000 – 200 000', '100 000 – 200 000'),
        ('200 000 – 500 000', '200 000 – 500 000'),
        ('Plus de 500 000', 'Plus de 500 000'),
    ]

    # =========================================================
    # IDENTITÉ
    # =========================================================
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True, default='')
    age = models.PositiveSmallIntegerField(default=0)
    sexe = models.CharField(max_length=10, choices=SEXE_CHOICES, blank=True, default='')
    niveau = models.CharField(max_length=30, choices=NIVEAU_CHOICES, blank=True, default='')

    # =========================================================
    # MÉNAGE / LOGEMENT
    # =========================================================
    menage = models.PositiveSmallIntegerField(default=1)
    logement = models.CharField(max_length=30, choices=LOGEMENT_CHOICES, blank=True, default='')
    statut_logement = models.CharField(max_length=30, choices=STATUT_LOGEMENT_CHOICES, blank=True, default='')
    adresse = models.CharField(max_length=200, blank=True, default='')

    # =========================================================
    # PROFESSION
    # =========================================================
    profession = models.CharField(max_length=100, choices=PROFESSION_CHOICES, blank=True, default='')
    revenu = models.CharField(max_length=30, choices=REVENU_CHOICES, blank=True, default='')

    # =========================================================
    # BESOINS
    # =========================================================
    besoins = models.JSONField(default=list, blank=True)

    # =========================================================
    # OBSERVATIONS
    # =========================================================
    obs = models.TextField(blank=True, default='')

    # =========================================================
    # META
    # =========================================================
    date_saisie = models.DateTimeField(auto_now_add=True)
    date_modif = models.DateTimeField(auto_now=True)

    saisi_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fiches'
    )

    class Meta:
        ordering = ['-date_saisie', '-id']
        verbose_name = 'Fiche de recensement'
        verbose_name_plural = 'Fiches de recensement'

    def __str__(self):
        return f'{self.nom} {self.prenom}'