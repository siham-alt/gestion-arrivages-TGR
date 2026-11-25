from django.contrib import admin
from .models import Arrivage, Poste, TypePiece, Comptable, Trimestre
from django.contrib.auth.models import User  # Importez le modèle User si ce n'est pas déjà fait
from django.urls import path
from . import admin_views


@admin.register(Poste)
class PosteAdmin(admin.ModelAdmin):
    list_display = ['code' ,'libelle']

@admin.register(TypePiece)
class TypePieceAdmin(admin.ModelAdmin):
    list_display = ['libelle']

@admin.register(Comptable)
class ComptableAdmin(admin.ModelAdmin):
    list_display = ['nomComplet']

@admin.register(Trimestre)
class TrimestreAdmin(admin.ModelAdmin):
    list_display = ['numero']

@admin.register(Arrivage)
class ArrivageAdmin(admin.ModelAdmin):
    # 'poste' affichera maintenant "code (libelle)" grâce à la modification de Poste.__str__
    list_display = ['date_arrivage', 'poste__code', 'poste__libelle', 'afficher_trimestres', 'type_piece', 'afficher_comptables','afficher_utilisateur_email' ]
    list_filter = ['poste', 'type_piece', 'comptables', 'date_arrivage', 'trimestres', 'user']
    # Ajoutez 'poste__libelle' et 'poste__code' aux champs de recherche pour permettre de filtrer par ces attributs
    search_fields = ['date_arrivage', 'poste__code', 'poste__libelle', 'type_piece__libelle']
    filter_horizontal = ['comptables', 'trimestres']

    def afficher_trimestres(self, obj):
        return ", ".join([str(t) for t in obj.trimestres.all()])
    afficher_trimestres.short_description = 'Trimestres'

    def afficher_comptables(self, obj):
        return ", ".join([c.nomComplet for c in obj.comptables.all()])
    afficher_comptables.short_description = 'Comptables'

    def afficher_utilisateur_email(self, obj):
        return obj.user.email if obj.user else None
    afficher_utilisateur_email.short_description = 'Utilisateur (Email)'

urlpatterns = (
    path('statistiques-tgr/', admin_views.statistiques_tgr, name='statistiques_tgr_admin'),
)













from .models import EquationPonderee, TermeEquation, CategorieEquation 

@admin.register(CategorieEquation)
class CategorieEquationAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

class TermeEquationInline(admin.TabularInline):
    model = TermeEquation
    extra = 1 # Nombre de formulaires vides à afficher
    fk_name = 'equation' # Spécifiez explicitement la clé étrangère si Django a du mal à la deviner

@admin.register(EquationPonderee)
class EquationPondereeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'constante', 'date_creation')
    inlines = [TermeEquationInline] # Intègre la gestion des termes directement dans le formulaire de l'équation
    search_fields = ('nom',)
    readonly_fields = ('date_creation', 'date_modification')