from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .models import Arrivage, TypePiece, Poste, Trimestre, CategorieEquation, EquationPonderee, TermeEquation,Matiere
from django.db.models.functions import ExtractYear, ExtractMonth # Gardez ExtractWeek, ExtractDay si vous les utilisez ailleurs
import datetime
from django.db import connection

import csv
from django.http import HttpResponse
from django.db.models.functions import ExtractMonth
from django.utils import timezone

import traceback # Pour un meilleur débogage des exceptions


import csv
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required 
from django.utils.translation import gettext_lazy as _ 

import json 

import datetime
import calendar
import json
from django.db.models import Count, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from django.shortcuts import render
from django.db import connection
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required

# IMPORTANT: Make sure your models are correctly imported.
# Replace 'your_app_name' with the actual name of your Django app

# --- Constants ---
TARGET_ARRIVAGES_PER_POSTE_PER_YEAR = 194

# --- French Month Names Dictionary ---
FRENCH_MONTH_NAMES = {
    1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
    5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
    9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
}

# --- Helper Functions ---
def get_late_count(raw_dict, key):
    """Safely retrieves the count of late arrivals from a dictionary, defaulting to 0."""
    return raw_dict.get(key, 0)

@staff_member_required
def statistiques_tgr(request):
    """
    Renders the TGR statistics dashboard, filtering data based on
    selected year and/or trimester.
    """
    selected_year = request.GET.get('year')
    selected_trimestre = request.GET.get('trimestre')

    current_year = datetime.date.today().year

    # 1. Base Queryset for Arrivages
    all_arrivages_queryset = Arrivage.objects.select_related('type_piece', 'poste').prefetch_related('trimestres').all()

    # Apply year filter if selected
    selected_year_int = None
    if selected_year and selected_year != 'all':
        try:
            selected_year_int = int(selected_year)
            all_arrivages_queryset = all_arrivages_queryset.filter(date_arrivage__year=selected_year_int)
        except ValueError:
            selected_year = None

    # Apply trimester filter if selected
    selected_trimestre_int = None
    if selected_trimestre and selected_trimestre != 'all':
        try:
            selected_trimestre_int = int(selected_trimestre)
            all_arrivages_queryset = all_arrivages_queryset.filter(trimestres__numero=selected_trimestre_int).distinct()
        except ValueError:
            selected_trimestre = None

    total_arrivages = all_arrivages_queryset.count()

    # --- Calculate Late Arrivals (using custom SQL function) ---
    total_alertes_calculees = 0
    arrivages_en_retard_calcules = 0

    late_arrivages_by_year_raw = {}
    late_arrivages_by_month_raw = {}
    late_arrivages_by_type_piece_raw = {}
    late_arrivages_by_poste_raw = {}
    late_arrivages_by_trimestre_raw = {}

    with connection.cursor() as cursor:
        for arrivage in all_arrivages_queryset:
            annee_gestion = arrivage.date_arrivage.year if arrivage.date_arrivage else timezone.now().year
            trimestres_list = [str(t.numero) for t in arrivage.trimestres.all().order_by('numero')]
            trimestres_str = ''.join(trimestres_list)

            try:
                cursor.execute(
                    "SELECT calcul_delais(%s, %s, %s)",
                    [annee_gestion, arrivage.date_arrivage, trimestres_str]
                )
                result = cursor.fetchone()[0]

                is_late = False
                if result:
                    delays_raw = result.strip('[]').split(',')
                    for delay_value in delays_raw:
                        if delay_value and delay_value.strip().startswith('+'):
                            is_late = True
                            break

                if is_late:
                    total_alertes_calculees += 1
                    arrivages_en_retard_calcules += 1

                    if arrivage.date_arrivage:
                        late_arrivages_by_year_raw[arrivage.date_arrivage.year] = late_arrivages_by_year_raw.get(arrivage.date_arrivage.year, 0) + 1
                        if not selected_year or arrivage.date_arrivage.year == (selected_year_int if selected_year_int else current_year):
                            late_arrivages_by_month_raw[arrivage.date_arrivage.month] = late_arrivages_by_month_raw.get(arrivage.date_arrivage.month, 0) + 1

                    if arrivage.type_piece:
                        late_arrivages_by_type_piece_raw[arrivage.type_piece.libelle] = late_arrivages_by_type_piece_raw.get(arrivage.type_piece.libelle, 0) + 1

                    if arrivage.poste:
                        late_arrivages_by_poste_raw[arrivage.poste.libelle] = late_arrivages_by_poste_raw.get(arrivage.poste.libelle, 0) + 1

                    for t in arrivage.trimestres.all():
                        if not selected_trimestre_int or t.numero == selected_trimestre_int:
                            late_arrivages_by_trimestre_raw[t.numero] = late_arrivages_by_trimestre_raw.get(t.numero, 0) + 1
            except Exception as e:
                print(f"Error executing calcul_delais for arrivage ID {arrivage.pk}: {e}")

    # --- Prepare Data for Charts and Tables ---

    # Arrivages par Année
    arrivages_par_annee_combined = []
    if not selected_year or selected_year == 'all':
        for stat in Arrivage.objects.annotate(annee=ExtractYear('date_arrivage')).values('annee').annotate(total=Count('id')).order_by('annee'):
            if stat['annee'] is not None:
                arrivages_par_annee_combined.append({
                    'annee': stat['annee'],
                    'total': stat['total'],
                    'en_retard': get_late_count(late_arrivages_by_year_raw, stat['annee'])
                })

    # Arrivages par Mois (Current/Selected Year)
    target_year_for_month_chart = selected_year_int if selected_year_int else current_year
    month_chart_queryset_aggregated = Arrivage.objects.filter(date_arrivage__year=target_year_for_month_chart)
    if selected_trimestre_int:
        month_chart_queryset_aggregated = month_chart_queryset_aggregated.filter(trimestres__numero=selected_trimestre_int).distinct()

    month_chart_queryset_aggregated = month_chart_queryset_aggregated \
        .annotate(mois=ExtractMonth('date_arrivage')) \
        .values('mois') \
        .annotate(total=Count('id')) \
        .order_by('mois')

    # Data for the MONTH CHART (only months with arrivals)
    arrivages_par_mois_chart_data = []
    for stat in month_chart_queryset_aggregated:
        if stat['mois'] is not None:
            arrivages_par_mois_chart_data.append({
                'mois_numero': stat['mois'],
                'mois_nom': FRENCH_MONTH_NAMES.get(stat['mois'], f'Mois {stat["mois"]}'), # French month name
                'total': stat['total'],
                'en_retard': get_late_count(late_arrivages_by_month_raw, stat['mois'])
            })

    # Data for the MONTH TABLE (all 12 months)
    arrivages_par_mois_table_data = []
    all_months_template = {i: {'mois_numero': i, 'mois_nom': FRENCH_MONTH_NAMES.get(i, f'Mois {i}'), 'total': 0, 'en_retard': 0} for i in range(1, 13)}

    # Populate totals for months that have data
    for stat in month_chart_queryset_aggregated:
        if stat['mois'] is not None:
            all_months_template[stat['mois']]['total'] = stat['total']
            all_months_template[stat['mois']]['en_retard'] = get_late_count(late_arrivages_by_month_raw, stat['mois'])

    arrivages_par_mois_table_data = list(all_months_template.values())
    arrivages_par_mois_table_data.sort(key=lambda x: x['mois_numero']) # Ensure proper month order


    # Arrivages par Type de Pièce
    arrivages_par_type_piece_combined = []
    for stat in all_arrivages_queryset.values('type_piece__libelle').annotate(total=Count('id')).order_by('type_piece__libelle'):
        if stat['type_piece__libelle'] is not None:
            arrivages_par_type_piece_combined.append({
                'libelle': stat['type_piece__libelle'],
                'total': stat['total'],
                'en_retard': get_late_count(late_arrivages_by_type_piece_raw, stat['type_piece__libelle'])
            })

    # Arrivages par Poste (Simple Chart - if you still use this one, otherwise 'target_combined' is preferred)
    arrivages_par_poste_simple_combined = []
    for stat in all_arrivages_queryset.values('poste__libelle').annotate(total=Count('id')).order_by('poste__libelle'):
        if stat['poste__libelle'] is not None:
            arrivages_par_poste_simple_combined.append({
                'libelle': stat['poste__libelle'],
                'total': stat['total'],
                'en_retard': get_late_count(late_arrivages_by_poste_raw, stat['poste__libelle'])
            })

    # Arrivages par Trimestre
    arrivages_par_trimestre_combined = []
    if not selected_trimestre or selected_trimestre == 'all':
        trimestre_chart_queryset = Arrivage.objects.all()
        if selected_year_int:
            trimestre_chart_queryset = trimestre_chart_queryset.filter(date_arrivage__year=selected_year_int)

        all_trimesters_data = {i: {'numero': i, 'total': 0, 'en_retard': 0} for i in range(1, 5)}
        for stat in trimestre_chart_queryset.values('trimestres__numero').annotate(total=Count('id')).order_by('trimestres__numero'):
            if stat['trimestres__numero'] is not None:
                all_trimesters_data[stat['trimestres__numero']]['total'] = stat['total']
                all_trimesters_data[stat['trimestres__numero']]['en_retard'] = get_late_count(late_arrivages_by_trimestre_raw, stat['trimestres__numero'])
        arrivages_par_trimestre_combined = list(all_trimesters_data.values())


    # --- Data for Arrivages par Poste vs Target Chart ---
    arrivages_par_poste_target_combined = []
    effective_target_per_poste = float(TARGET_ARRIVAGES_PER_POSTE_PER_YEAR)
    if selected_trimestre_int:
        effective_target_per_poste = effective_target_per_poste / 4.0
    if effective_target_per_poste == 0:
        effective_target_per_poste = TARGET_ARRIVAGES_PER_POSTE_PER_YEAR

    arrivages_counts_by_poste_libelle_qs = all_arrivages_queryset \
                                            .values('poste__libelle') \
                                            .annotate(total_recus_aggregated=Count('id')) \
                                            .order_by('poste__libelle')

    counts_dict = {item['poste__libelle']: item['total_recus_aggregated'] for item in arrivages_counts_by_poste_libelle_qs}

    all_distinct_poste_libelles = Poste.objects.values_list('libelle', flat=True).distinct().order_by('libelle')

    for poste_libelle in all_distinct_poste_libelles:
        if poste_libelle is None:
            continue

        total_recus = counts_dict.get(poste_libelle, 0)
        remains_to_receive = max(0, effective_target_per_poste - total_recus)
        exceeded_target = max(0, total_recus - effective_target_per_poste)

        arrivages_par_poste_target_combined.append({
            'type_poste': poste_libelle,
            'total_recus': total_recus,
            'remains_to_receive': remains_to_receive,
            'exceeded_target': exceeded_target,
            'effective_target': effective_target_per_poste
        })

    # --- Context for Template ---
    context = {
        'total_arrivages': total_arrivages,
        'total_alertes': total_alertes_calculees,
        'arrivages_en_retard': arrivages_en_retard_calcules,
        'current_year': current_year,

        'arrivages_par_annee_combined': arrivages_par_annee_combined,
        'arrivages_par_mois_chart_data': arrivages_par_mois_chart_data, # For the chart
        'arrivages_par_mois_table_data': arrivages_par_mois_table_data, # For the table
        'arrivages_par_type_piece_combined': arrivages_par_type_piece_combined,
        'arrivages_par_poste_simple_combined': arrivages_par_poste_simple_combined,
        'arrivages_par_trimestre_combined': arrivages_par_trimestre_combined,

        'selected_year': selected_year,
        'selected_trimestre': selected_trimestre,
        'available_years': sorted(list(Arrivage.objects.annotate(year=ExtractYear('date_arrivage')).values_list('year', flat=True).distinct().exclude(year__isnull=True))),
        'available_trimestres': sorted(list(Trimestre.objects.values_list('numero', flat=True).distinct())),

        'arrivages_par_poste_target_combined': arrivages_par_poste_target_combined,
        'TARGET_ARRIVAGES_PER_POSTE_PER_YEAR': TARGET_ARRIVAGES_PER_POSTE_PER_YEAR,
    }
    return render(request, 'admin/statistiques_tgr.html', context)

@staff_member_required # This decorator ensures only staff (admin) users can access this view
def admin_alertes_page(request):
    all_arrivages = Arrivage.objects.all() # Get ALL arrivages
    arrivages_with_delays = []
    with connection.cursor() as cursor:
        for arrivage in all_arrivages:
            annee_gestion = arrivage.date_arrivage.year if arrivage.date_arrivage else timezone.now().year
            trimestres_str = ''.join([str(t.numero) for t in arrivage.trimestres.all()])

            cursor.execute(
                "SELECT calcul_delais(%s, %s, %s)",
                [annee_gestion, arrivage.date_arrivage, trimestres_str]
            )
            result = cursor.fetchone()[0]
            delays_raw = result.strip('[]').split(',')
            delays = {
                'T1': delays_raw[0], 'T2': delays_raw[1],
                'T3': delays_raw[2], 'T4': delays_raw[3],
            }
            is_late = False
            for delay_value in delays.values():
                if delay_value and delay_value.strip().startswith('+'):
                    is_late = True
                    break

            arrivages_with_delays.append({
                'arrivage': arrivage,
                'delays': delays,
                'is_late': is_late,
            })
    
    context = {
        'arrivages_with_delays': arrivages_with_delays,
        'title':("Toutes les Alertes de Délais (Admin)"), # A distinct title
    }
    return render(request, 'admin/admin_alertes_page.html', context) 




























def export_arrivages_par_mois_csv(request):
    response = HttpResponse(content_type='text/csv')
    current_year = timezone.now().year
    response['Content-Disposition'] = f'attachment; filename="arrivages_par_mois_{current_year}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Mois', 'Nombre d\'Arrivages'])
    arrivages_par_mois_current_year = Arrivage.objects.filter(
        date_arrivage__year=current_year
    ).annotate(
        mois=ExtractMonth('date_arrivage')
    ).values('mois').annotate(
        total=Count('id')
    ).order_by('mois')
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
        7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    for stat in arrivages_par_mois_current_year:
        month_name = month_names.get(stat['mois'], f'Mois {stat["mois"]}')
        writer.writerow([month_name, stat['total']])
    return response
# ... (votre code précédent)






def export_details_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="details_statistiques.csv"'
    writer = csv.writer(response)
    writer.writerow(['Catégorie', 'Nombre'])
    current_year = timezone.now().year

    # Calculer arrivages_en_retard dynamiquement
    arrivages_en_retard_calcules = 0
    all_arrivages = Arrivage.objects.select_related('type_piece', 'poste').prefetch_related('trimestres').all()
    
    with connection.cursor() as cursor:
        for arrivage in all_arrivages:
            annee_gestion = arrivage.date_arrivage.year if arrivage.date_arrivage else timezone.now().year
            trimestres_str = ''.join([str(t.numero) for t in arrivage.trimestres.all()])
            
            cursor.execute(
                "SELECT calcul_delais(%s, %s, %s)",
                [annee_gestion, arrivage.date_arrivage, trimestres_str]
            )
            result = cursor.fetchone()[0]
            delays_raw = result.strip('[]').split(',')
            
            is_late = False
            for delay_value in delays_raw:
                if delay_value and delay_value.strip().startswith('+'):
                    is_late = True
                    break
            
            if is_late:
                arrivages_en_retard_calcules += 1

    arrivages_2025 = Arrivage.objects.filter(date_arrivage__year=2025).count()
    arrivages_2026 = Arrivage.objects.filter(date_arrivage__year=2026).count()

    writer.writerow(['Total Arrivages', Arrivage.objects.count()])
    writer.writerow(['Arrivages en retard', arrivages_en_retard_calcules]) 
    return response

# ... (gardez vos autres fonctions d'exportation telles quelles si elles ne dépendent pas d'Alerte)
def export_arrivages_par_poste_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="arrivages_par_poste.csv"'
    writer = csv.writer(response)
    writer.writerow(['Poste', 'Nombre d\'Arrivages'])
    arrivages_par_poste = Arrivage.objects.values('poste__libelle').annotate(total=Count('id')).order_by('poste__libelle')
    for stat in arrivages_par_poste:
        writer.writerow([stat['poste__libelle'], stat['total']])
    return response

def export_arrivages_par_type_piece_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="arrivages_par_type_piece.csv"'
    writer = csv.writer(response)
    writer.writerow(['Type de Pièce', 'Nombre d\'Arrivages'])
    arrivages_par_type_piece = Arrivage.objects.values('type_piece__libelle').annotate(total=Count('id')).order_by('type_piece__libelle')
    for stat in arrivages_par_type_piece:
        writer.writerow([stat['type_piece__libelle'], stat['total']])
    return response












# This function remains unchanged as it only prepares data for the template.
@staff_member_required
def creer_equation_ponderee(request):
    """
    Rend la page de création d'équation pondérée et passe les données nécessaires au template.
    """
    categories_disponibles = list(CategorieEquation.objects.values('id', 'nom'))
    
    type_pieces = list(TypePiece.objects.values('id', 'libelle'))
    postes = list(Poste.objects.values('id', 'libelle'))
    matieres = list(Matiere.objects.values('id', 'code', 'libelle', 'categorie_id'))

    context = {
        'title': "Créer une Nouvelle Équation Pondérée",
        'categories_disponibles': categories_disponibles,
        'type_pieces': type_pieces, 
        'postes': postes, 
        'matieres': matieres, 
    }
    return render(request, 'admin/creer_equation_ponderee.html', context)


@staff_member_required
def sauvegarder_equation_ponderee(request):
    """
    Gère la logique de sauvegarde d'une nouvelle équation pondérée.
    Inclut des validations côté serveur.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nom_equation = data.get('nom_equation', '').strip()
            constante = float(data.get('constante', 0.0)) 
            termes_data = data.get('termes', [])

            # --- Validations préliminaires ---
            if not nom_equation:
                return JsonResponse({'status': 'error', 'message': 'Le nom de l\'équation est requis.'}, status=400)
            
            if EquationPonderee.objects.filter(nom=nom_equation).exists():
                return JsonResponse({'status': 'error', 'message': f'Une équation nommée "{nom_equation}" existe déjà. Veuillez choisir un autre nom.'}, status=400)

            # Determine all CategorieEquation IDs that correspond to any Matiere.
            # This set will contain IDs like 1 (for 'Chimie'), 2 (for 'Métaux Industriels'), etc.,
            # if these categories are linked to Matiere objects.
            matiere_category_ids = set(Matiere.objects.values_list('categorie_id', flat=True))

            # Calculate the sum of coefficients ONLY for terms belonging to 'Matiere' categories.
            total_matiere_coefficients_sum = 0.0
            has_matiere_terms = False # Flag to check if any Matiere terms were added

            for terme_info in termes_data:
                terme_categorie_id = int(terme_info.get('categorie_id'))
                
                # If the term's category is one of the 'Matiere' categories, add its coefficient to the sum
                if terme_categorie_id in matiere_category_ids: 
                    try:
                        coeff = float(terme_info.get('coefficient', 0.0))
                        total_matiere_coefficients_sum += coeff
                        has_matiere_terms = True
                    except (ValueError, TypeError):
                        # This specific error should ideally be caught by general term validation later,
                        # but keeping it here for clarity regarding sum calculation.
                        return JsonResponse(
                            {'status': 'error', 
                             'message': 'Un coefficient invalide a été fourni pour un terme de type Matière.'}, 
                            status=400
                        )
            
            epsilon = 0.001 # Tolerance for floating point comparison (e.g., 0.999 to 1.001)

            # --- Perform GLOBAL validation for Matiere terms ---
            # This condition ensures that if NO Matiere terms are present, the validation doesn't trigger,
            # but if they ARE present, their sum MUST be 1.00.
            if has_matiere_terms:
                if not (total_matiere_coefficients_sum >= (1.0 - epsilon) and total_matiere_coefficients_sum <= (1.0 + epsilon)):
                    return JsonResponse(
                        {'status': 'error', 
                         'message': f'La somme de tous les coefficients doit être égale à 1.00. La somme actuelle est de {total_matiere_coefficients_sum:.2f}.'}, 
                        status=400
                    )
            # --- End of global sum of coefficients validation ---

            # If all validations pass, proceed to create the EquationPonderee object.
            equation = EquationPonderee.objects.create(
                nom=nom_equation,
                constante=constante
            )

            # Create the TermeEquation instances
            for terme_info in termes_data:
                categorie_id = terme_info.get('categorie_id')
                code_libelle = terme_info.get('code_libelle')
                coefficient = terme_info.get('coefficient') 

                if categorie_id is not None and code_libelle is not None and coefficient is not None:
                    try:
                        categorie = CategorieEquation.objects.get(id=categorie_id)
                        TermeEquation.objects.create(
                            equation=equation,
                            categorie=categorie,
                            code_libelle=code_libelle,
                            coefficient=float(coefficient) 
                        )
                    except CategorieEquation.DoesNotExist:
                        equation.delete() 
                        return JsonResponse(
                            {'status': 'error', 'message': f'Catégorie non trouvée pour le terme: {code_libelle}. Sauvegarde annulée.'}, 
                            status=400
                        )
                    except (ValueError, TypeError):
                        equation.delete()
                        return JsonResponse(
                            {'status': 'error', 'message': f'Le coefficient pour le terme "{code_libelle}" est invalide. Sauvegarde annulée.'}, 
                            status=400
                        )
                else:
                    equation.delete() 
                    return JsonResponse(
                        {'status': 'error', 'message': 'Un terme de l\'équation est incomplet (catégorie, libellé ou coefficient manquant). Sauvegarde annulée.'}, 
                        status=400
                    )
            
            return JsonResponse({'status': 'success', 'message': 'Équation enregistrée avec succès!', 'equation_id': equation.id})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Requête JSON invalide.'}, status=400)
        except Exception as e:
            traceback.print_exc() # Log the full traceback for debugging
            return JsonResponse({'status': 'error', 'message': f'Erreur interne du serveur: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)