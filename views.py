"""
RecenSmart — Vues API Production
Endpoints :
  GET/POST   /api/fiches/
  GET/PUT/PATCH/DELETE /api/fiches/<id>/
  GET        /api/stats/
  GET        /api/export/csv/
  GET        /api/me/
"""

import csv
import io
import math
from collections import Counter
from datetime import date

from django.http import HttpResponse
from rest_framework import filters, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Fiche
from .serializers import FicheSerializer, UserSerializer


# =========================================================
# HELPERS
# =========================================================

def age_group(age):
    if age < 18:
        return '0-17'
    if age < 30:
        return '18-29'
    if age < 45:
        return '30-44'
    if age < 60:
        return '45-59'
    return '60+'


def median(values):
    if not values:
        return 0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else s[mid]


def std_dev(values):
    if not values:
        return 0
    m = sum(values) / len(values)
    variance = sum((v - m) ** 2 for v in values) / len(values)
    return round(math.sqrt(variance), 1)


# =========================================================
# USER CURRENT
# =========================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def me(request):
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({"user": None})


# =========================================================
# CRUD FICHES
# =========================================================

class FicheListCreateView(generics.ListCreateAPIView):
    serializer_class = FicheSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'prenom', 'adresse', 'profession']
    ordering_fields = ['nom', 'age', 'date_saisie', 'menage']
    ordering = ['-date_saisie']

    def get_queryset(self):
        qs = Fiche.objects.select_related('saisi_par').all()

        sexe = self.request.query_params.get('sexe')
        profession = self.request.query_params.get('profession')
        revenu = self.request.query_params.get('revenu')

        if sexe:
            qs = qs.filter(sexe=sexe)
        if profession:
            qs = qs.filter(profession=profession)
        if revenu:
            qs = qs.filter(revenu=revenu)

        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(saisi_par=user)


class FicheDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fiche.objects.select_related('saisi_par').all()
    serializer_class = FicheSerializer
    permission_classes = [permissions.AllowAny]


# =========================================================
# STATS DASHBOARD
# =========================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def stats(request):
    fiches = list(Fiche.objects.select_related('saisi_par').all())
    n = len(fiches)

    if n == 0:
        return Response({
            'total_fiches': 0,
            'total_personnes': 0,
            'age_moyen': 0,
            'menage_moyen': 0,
            'age_median': 0,
            'age_ecart_type': 0,
            'menage_median': 0,
            'taux_besoins_critiques': 0,
            'repartition_sexe': {},
            'repartition_age': {},
            'repartition_profession': {},
            'repartition_logement': {},
            'repartition_statut_logement': {},
            'repartition_revenu': {},
            'repartition_menage': {},
            'besoins_count': {},
            'besoins_pct': {},
            'recents': [],
        })

    ages = [f.age for f in fiches]
    menages = [f.menage for f in fiches]

    age_groups = Counter(age_group(f.age) for f in fiches)
    age_groups_ordered = {
        k: age_groups.get(k, 0)
        for k in ['0-17', '18-29', '30-44', '45-59', '60+']
    }

    menage_groups = {'1-2': 0, '3-4': 0, '5-6': 0, '7+': 0}
    for f in fiches:
        if f.menage <= 2:
            menage_groups['1-2'] += 1
        elif f.menage <= 4:
            menage_groups['3-4'] += 1
        elif f.menage <= 6:
            menage_groups['5-6'] += 1
        else:
            menage_groups['7+'] += 1

    besoin_counter = Counter()
    for f in fiches:
        besoin_counter.update(f.besoins or [])

    besoins_pct = {b: round(c / n * 100) for b, c in besoin_counter.items()}

    critiques = sum(
        1 for f in fiches
        if 'Eau potable' in (f.besoins or []) or 'Électricité' in (f.besoins or [])
    )

    age_hist = [0] * 10
    for a in ages:
        age_hist[min(a // 10, 9)] += 1

    pro_counter = Counter(f.profession for f in fiches)

    recents = FicheSerializer(
        sorted(fiches, key=lambda f: (f.date_saisie, f.id), reverse=True)[:5],
        many=True
    ).data

    return Response({
        'total_fiches': n,
        'total_personnes': sum(menages),
        'age_moyen': round(sum(ages) / n, 1),
        'age_median': median(ages),
        'age_ecart_type': std_dev(ages),
        'menage_moyen': round(sum(menages) / n, 1),
        'menage_median': median(menages),
        'taux_besoins_critiques': round(critiques / n * 100),

        'repartition_sexe': dict(Counter(f.sexe for f in fiches)),
        'repartition_age': age_groups_ordered,
        'repartition_age_detail': {
            f'{i*10}-{i*10+9}' if i < 9 else '90+': age_hist[i]
            for i in range(10)
        },
        'repartition_profession': dict(pro_counter.most_common(10)),
        'repartition_logement': dict(Counter(f.logement for f in fiches if f.logement)),
        'repartition_statut_logement': dict(Counter(f.statut_logement for f in fiches if f.statut_logement)),
        'repartition_revenu': dict(Counter(f.revenu for f in fiches if f.revenu)),
        'repartition_menage': menage_groups,

        'besoins_count': dict(besoin_counter),
        'besoins_pct': besoins_pct,

        'recents': recents,
    })


# =========================================================
# EXPORT CSV
# =========================================================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def export_csv(request):
    fiches = Fiche.objects.select_related('saisi_par').all()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    writer.writerow([
        'ID', 'Nom', 'Prénom', 'Âge', 'Sexe', "Niveau d'études",
        'Taille ménage', 'Type logement', "Statut d'occupation", 'Adresse',
        'Profession', 'Revenu mensuel', 'Besoins non satisfaits',
        'Observations', 'Date saisie', 'Saisi par',
    ])

    for f in fiches:
        writer.writerow([
            f.id, f.nom, f.prenom, f.age, f.sexe, f.niveau,
            f.menage, f.logement, f.statut_logement, f.adresse,
            f.profession, f.revenu,
            ' | '.join(f.besoins or []),
            f.obs,
            f.date_saisie.strftime('%d/%m/%Y'),
            f.saisi_par.username if f.saisi_par else '',
        ])

    content = '\ufeff' + output.getvalue()
    response = HttpResponse(content, content_type='text/csv; charset=utf-8')
    filename = f'recensement_{date.today().isoformat()}.csv'
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    return response