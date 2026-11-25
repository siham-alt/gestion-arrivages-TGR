import logging
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app1 import views  # Importez les vues depuis votre application 'app1'

logger = logging.getLogger(__name__)

def logout_view(request):
    logger.info("Tentative de déconnexion de l'utilisateur.")
    return auth_views.LogoutView.as_view(next_page='home')(request)

urlpatterns = [
    path('admin/', include('app1.admin')),  # Incluez VOS URLs d'admin EN PREMIER
    path('admin/', admin.site.urls),        # Ensuite, incluez les URLs d'admin par défaut
    path('arrivages/', include('app1.urls')),
    path('login/', views.ajax_login, name='login'), # Utilisez la vue importée
    path('', views.home, name='home'),
    path('logout/', logout_view, name='logout'),
 ]
