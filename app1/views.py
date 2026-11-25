from django.shortcuts import render, redirect, get_object_or_404
from app1.models import Arrivage, Comptable
from .forms import ArrivageForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from django.contrib import messages
from .utils import get_deadline_info, get_deadline_for_arrivage
from django.utils import timezone
from django.db import connection # Import connection for raw SQL


def ajax_login(request):
    """
    Handles AJAX login requests. Returns a JSON response indicating success
    or failure. Redirects to the admin index page on successful login for
    non-Comptable users, and to the comptable profile for Comptable users.
    """
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                if est_comptable(user):
                    return JsonResponse({'success': True, 'redirect_url': reverse('profil_comptable')})
                else:
                    return JsonResponse({'success': True, 'redirect_url': reverse('admin:index')})
            else:
                return JsonResponse({'success': False, 'error': _('Nom d\'utilisateur ou mot de passe incorrect.')}, status=400)
        else:
            return JsonResponse({'error': _('Requête non AJAX')}, status=400)
    else:
        return JsonResponse({'error': _('Méthode non autorisée.')}, status=405)


@login_required
def profil_comptable(request):
    return render(request, 'app1/profil_comptable.html', {'user': request.user})


def est_comptable(user):
    """
    Checks if a user belongs to the 'Comptable' group.
    """
    return user.groups.filter(name='Comptable').exists()


@login_required
def ajouter_arrivage(request):
    if request.method == 'POST':
        form = ArrivageForm(request.POST)
        if form.is_valid():
            arrivage = form.save(commit=False)
            arrivage.user = request.user
            arrivage.save()
            form.save_m2m()
            return redirect('consulter_envois')
    else:
        form = ArrivageForm()
    return render(request, 'app1/ajouter_arrivage.html', {'form': form})

@login_required
def consulter_envois(request):
    """
    Displays a list of arrivages for the currently logged-in user, with filtering
    and ordering options.
    """
    current_user = request.user
    arrivages = Arrivage.objects.filter(user=current_user)

    # Get filter parameters from the request
    ordering = request.GET.get('ordering')
    date_filter = request.GET.get('date')

    # Apply filters
    if date_filter:
        arrivages = arrivages.filter(date_arrivage=date_filter)
    if ordering:
        arrivages = arrivages.order_by(ordering)

    # Prepare context. Pass the filter values back to the template.
    context = {
        'arrivages': arrivages,
        'ordering': ordering,
        'date_filter': date_filter,
    }
    return render(request, 'app1/consulter_envois.html', context)


def liste_arrivages(request):
    """
    Displays all arrivages. This view is accessible to all users.
    """
    arrivages = Arrivage.objects.all()
    context = {
        'arrivages': arrivages,
    }
    return render(request, 'app1/liste_arrivages.html', context)


def home(request):
    form = AuthenticationForm()
    return render(request, 'app1/home.html', {'form': form})

def eq(request):
    return render(request, 'app1/eq.html')

@login_required
def modifier_arrivage(request, arrivage_id):
    arrivage = get_object_or_404(Arrivage, pk=arrivage_id)
    if request.method == 'POST':
        form = ArrivageForm(request.POST, instance=arrivage)
        if form.is_valid():
            form.save()
            messages.success(request, _('L\'arrivage a été modifié avec succès.'))
            return redirect('consulter_envois') # Rediriger vers la liste après la modification
        else:
            messages.error(request, _('Il y a eu une erreur lors de la modification de l\'arrivage. Veuillez vérifier le formulaire.'))
    else:
        form = ArrivageForm(instance=arrivage)
    return render(request, 'app1/modifier_arrivage.html', {'form': form, 'arrivage': arrivage})

@login_required
def alertes_page(request):
    user_arrivages = Arrivage.objects.filter(user=request.user)
    arrivages_with_delays = []
    with connection.cursor() as cursor:
        for arrivage in user_arrivages:
            annee_gestion = arrivage.date_arrivage.year if arrivage.date_arrivage else timezone.now().year

            # Get the list of trimester numbers as a comma-separated string
            trimestres_str = ''.join([str(t.numero) for t in arrivage.trimestres.all()])

            # Call the MySQL function
            cursor.execute(
                "SELECT calcul_delais(%s, %s, %s)",
                [annee_gestion, arrivage.date_arrivage, trimestres_str]
            )
            result = cursor.fetchone()[0] # The function returns a single value

            # Parse the JSON-like string result
            # The result is like '[+5 jours,0 jours,0 jours,0 jours]'
            delays_raw = result.strip('[]').split(',')
            delays = {
                'T1': delays_raw[0],
                'T2': delays_raw[1],
                'T3': delays_raw[2],
                'T4': delays_raw[3],
            }

            # Determine if any delay is positive (indicating lateness)
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
        'title': _("Alertes de Délais"),
    }
    return render(request, 'app1/alertes_page.html', context)













