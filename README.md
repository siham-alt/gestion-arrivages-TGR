# GAC-TGR – Gestion des Arrivages Comptables

## Présentation du projet

Dans le cadre de sa stratégie de modernisation et de digitalisation, la Trésorerie Générale du Royaume (TGR) a exprimé le besoin de mettre en place une application web dédiée à la gestion des arrivages comptables.

**GAC-TGR** est une application web conçue pour faciliter le suivi, la traçabilité et le traitement des documents entrants au sein de la TGR.

Elle permet aux responsables de saisir et de suivre les arrivages, tout en offrant aux administrateurs une vision globale de l'activité grâce à des fonctionnalités de gestion et de consultation des statistiques.

L'application vise à optimiser les processus internes, réduire les erreurs liées à la gestion manuelle et améliorer le suivi des délais de traitement.

## Objectifs du projet

- Améliorer la traçabilité des documents entrants.
- Faciliter le suivi des délais de traitement des arrivages.
- Réduire les erreurs liées à la gestion manuelle.
- Centraliser les informations relatives aux arrivages comptables.
- Offrir une interface conviviale et intuitive aux utilisateurs.
- Permettre une consultation rapide des statistiques liées aux arrivages.
- Faciliter le travail des administrateurs et des responsables de la TGR.

## Fonctionnalités principales

### 1. Espace administrateur

L'administrateur dispose d'un accès étendu à l'application lui permettant de :

- Gérer les comptes des utilisateurs : création, modification et suppression.
- Consulter l'ensemble des arrivages enregistrés.
- Ajouter, modifier et supprimer les arrivages.
- Visualiser les statistiques générales.
- Consulter les statistiques par période et par poste comptable.
- Suivre les délais de traitement.
- Gérer les paramètres du système, notamment les délais et les alertes.

### 2. Espace responsable TGR

Les responsables disposent d'un accès adapté à leurs besoins opérationnels.

Ils peuvent :

- Ajouter de nouveaux arrivages comptables.
- Consulter la liste des arrivages qu'ils ont saisis.
- Modifier leurs propres arrivages.
- Supprimer leurs propres arrivages.
- Suivre l'état de leurs arrivages.
- Recevoir des alertes en cas de non-respect des délais de traitement.

### 3. Suivi et statistiques

L'application permet notamment de :

- Consulter les arrivages enregistrés.
- Suivre les délais de traitement.
- Identifier les arrivages en retard.
- Visualiser des statistiques globales.
- Analyser les arrivages selon différentes périodes et différents postes comptables.

## Règles de gestion

L'application repose sur les règles de gestion suivantes :

1. L'accès aux fonctionnalités dépend du rôle de l'utilisateur : administrateur ou responsable TGR.
2. Les responsables peuvent gérer uniquement les arrivages qu'ils ont eux-mêmes saisis.
3. Les administrateurs peuvent consulter et gérer l'ensemble des arrivages.
4. Chaque arrivage doit être associé aux informations nécessaires à son suivi.
5. Les délais de traitement doivent être surveillés afin d'identifier les retards.
6. Des alertes permettent de signaler les arrivages dont les délais ne sont pas respectés.
7. Les statistiques sont calculées à partir des arrivages enregistrés dans le système.

## Technologies utilisées

### Backend
- **Python** : langage de programmation utilisé pour le développement côté serveur.
- **Django** : framework Python utilisé pour la gestion des fonctionnalités, des routes, des vues, des modèles et de l'authentification.

### Frontend
- **HTML5** : structure des pages web.
- **CSS3** : mise en forme et conception de l'interface utilisateur.
- **JavaScript** : gestion des interactions et dynamisation de l'interface.

### Base de données
- **MySQL** : système de gestion de base de données relationnelle utilisé pour stocker les données de l'application.

### Outils de développement
- **Visual Studio Code** : environnement de développement.
- **MySQL Workbench** : outil de gestion et d'administration de la base de données.
- **Git et GitHub** : gestion des versions et hébergement du code source.

## Installation et lancement

### 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- Python
- Django
- MySQL Server
- MySQL Workbench
- Git

### 2. Cloner le repository

```bash
git clone https://github.com/siham-alt/gac-tgr-gestion-arrivages.git
```

Accéder au dossier du projet :

```bash
cd gac-tgr-gestion-arrivages
```

### 3. Créer un environnement virtuel

```bash
python -m venv venv
```

Activer l'environnement virtuel sous Windows :

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configurer la base de données

Créer une base de données MySQL, puis configurer les paramètres de connexion dans le fichier de configuration Django (`settings.py`) ou dans le fichier d'environnement utilisé par le projet.

Exemple de configuration :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nom_de_la_base',
        'USER': 'root',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

Remplacer les valeurs par celles de votre environnement.

### 6. Appliquer les migrations

```bash
python manage.py migrate
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Accéder à l'application depuis le navigateur :

http://127.0.0.1:8000/


## Contexte du projet

Ce projet s'inscrit dans le cadre de la modernisation des processus internes de la Trésorerie Générale du Royaume.

Il vise à fournir une solution numérique centralisée permettant d'améliorer la gestion des arrivages comptables, de renforcer leur traçabilité et de faciliter le suivi des délais de traitement.

---

**Nom du projet :** GAC-TGR – Gestion des Arrivages Comptables

**Organisme :** Trésorerie Générale du Royaume (TGR) – Maroc

**Technologies :** Python, Django, HTML5, CSS3, JavaScript et MySQL
