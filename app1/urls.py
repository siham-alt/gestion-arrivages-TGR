from django.urls import path
from . import views         # Pour les vues générales de l'app1 (home, login, etc.)
from . import admin_views   # Pour les vues d'administration et d'exportation (statistiques_tgr, export_...)
from django.contrib.auth import views as auth_views  # Importez les vues d'authentification de Django

urlpatterns = [
    # URLs de l'application 'app1' (vues générales)
    path('liste/', views.liste_arrivages, name='liste_arrivages'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('ajouter_arrivage/', views.ajouter_arrivage, name='ajouter_arrivage'),
    # path('liste_arrivages/', views.liste_arrivages, name='liste_arrivages'), # Potentiellement en double avec 'liste/'
    path('consulter_envois/', views.consulter_envois, name='consulter_envois'),
    path('profil_comptable/', views.profil_comptable, name='profil_comptable'),
    path('arrivages/modifier/<int:arrivage_id>/', views.modifier_arrivage, name='modifier_arrivage'),
    path('alertes/', views.alertes_page, name='alertes_page'),

    # Nouvelle URL pour la page de statistiques (avec un préfixe admin pour la clarté)
    path('admin/statistiques-tgr/', admin_views.statistiques_tgr, name='statistiques_tgr_admin'),
    path('admin/alertes/', admin_views.admin_alertes_page, name='admin_alertes_page'), # Admin's alerts

    # URLs pour les exports CSV
    path('admin/statistiques/export/mois/csv/', admin_views.export_arrivages_par_mois_csv, name='export_arrivages_par_mois_csv'),
    path('admin/statistiques/export/details/csv/', admin_views.export_details_csv, name='export_details_csv'),
    path('admin/statistiques/export/poste/csv/', admin_views.export_arrivages_par_poste_csv, name='export_arrivages_par_poste_csv'),
    path('admin/statistiques/export/type_piece/csv/', admin_views.export_arrivages_par_type_piece_csv, name='export_arrivages_par_type_piece_csv'),

   path('creer-equation/', admin_views.creer_equation_ponderee, name='creer_equation_ponderee'),
    path('sauvegarder-equation/', admin_views.sauvegarder_equation_ponderee, name='sauvegarder_equation_ponderee'),
]