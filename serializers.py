from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Fiche


# =========================================================
# USER SERIALIZER
# =========================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# =========================================================
# FICHE SERIALIZER
# =========================================================

class FicheSerializer(serializers.ModelSerializer):
    saisi_par = UserSerializer(read_only=True)
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model = Fiche
        fields = [
            'id',
            'nom',
            'prenom',
            'nom_complet',
            'age',
            'sexe',
            'niveau',
            'menage',
            'logement',
            'statut_logement',
            'adresse',
            'profession',
            'revenu',
            'besoins',
            'obs',
            'date_saisie',
            'date_modif',
            'saisi_par',
        ]
        read_only_fields = ['id', 'date_saisie', 'date_modif', 'saisi_par']

    # =====================================================
    # FULL NAME
    # =====================================================
    def get_nom_complet(self, obj):
        return f"{obj.nom} {obj.prenom}".strip()

    # =====================================================
    # VALIDATIONS
    # =====================================================
    def validate_nom(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Le nom est obligatoire.")
        return value.strip()

    def validate_age(self, value):
        if value is None:
            return 0
        if not (0 <= value <= 120):
            raise serializers.ValidationError("L'âge doit être entre 0 et 120.")
        return value

    def validate_menage(self, value):
        if value is None:
            return 1
        if not (1 <= value <= 30):
            raise serializers.ValidationError("La taille du ménage doit être entre 1 et 30.")
        return value

    def validate_besoins(self, value):
        if value is None:
            return []

        valides = set([
            'Eau potable',
            'Électricité',
            'Internet',
            'Accès santé',
            'Éducation',
            'Sécurité',
            'Transport',
            'Assainissement',
            'Sécurité alimentaire',
        ])

        invalides = [b for b in value if b not in valides]

        if invalides:
            raise serializers.ValidationError(f"Besoins inconnus : {invalides}")

        return value