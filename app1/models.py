
from django.db import models
from django.contrib.auth.models import User

class Poste(models.Model):
    code = models.CharField(max_length=50, null=True, blank=True)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        if self.code:
            return self.code
        elif self.libelle:
            return self.libelle
        return f"Poste (ID: {self.pk})" 
    
class Comptable(models.Model):
    nomComplet = models.CharField(max_length=100)

    def __str__(self):
        return self.nomComplet

class TypePiece(models.Model):
    code = models.CharField(max_length=3)
    libelle = models.CharField(max_length=50)

    def __str__(self):
        return self.libelle

class Trimestre(models.Model):
    numero = models.IntegerField(choices=[(1, 'Trimestre 1'), (2, 'Trimestre 2'), (3, 'Trimestre 3'), (4, 'Trimestre 4')])

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f"Trimestre {self.numero}"
    
class Arrivage(models.Model):
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE)
    type_piece = models.ForeignKey(TypePiece, on_delete=models.CASCADE)
    comptables = models.ManyToManyField(Comptable)
    date_arrivage = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arrivages_tgr', verbose_name="Utilisateur TGR", default=1)
    trimestres = models.ManyToManyField(Trimestre)

    def __str__(self):
        return f"Arrivage du {self.date_arrivage if self.date_arrivage else 'Non daté'}"

    def afficher_trimestres(self):
        return ", ".join([str(t) for t in self.trimestres.all()])

    afficher_trimestres.short_description = 'Trimestres'
















from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Nouveaux modèles pour l'équation pondérée
class CategorieEquation(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nom

class Matiere(models.Model):
    categorie = models.ForeignKey(CategorieEquation, on_delete=models.CASCADE, related_name='matieres')
    code = models.CharField(max_length=50, unique=True, help_text="Code abrégé, ex: OR, AG")
    libelle = models.CharField(max_length=255, help_text="Nom complet, ex: Or, Argent")

    def __str__(self):
        return f"{self.categorie.nom}: {self.libelle} ({self.code})"
class EquationPonderee(models.Model):
    nom = models.CharField(max_length=255, unique=True) # Nom de l'équation (ex: "Équation de Coût Total")
    description = models.TextField(blank=True, null=True)
    constante = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class TermeEquation(models.Model):
    # La ForeignKey qui lie un terme à une équation spécifique
    equation = models.ForeignKey(EquationPonderee, on_delete=models.CASCADE, related_name='termes') 
    
    # La catégorie du terme (ex: "Type de Pièce")
    categorie = models.ForeignKey(CategorieEquation, on_delete=models.CASCADE, related_name='termes_liees')
    
    code_libelle = models.CharField(max_length=255) 
    
    coefficient = models.DecimalField(max_digits=10, decimal_places=2, default=1.00) 

    def __str__(self):
        return f"[{self.equation.nom}] {self.categorie.nom}: {self.code_libelle} (Coeff: {self.coefficient})"

    class Meta:
        # Pour s'assurer qu'un même couple (équation, catégorie, code_libelle) n'est pas dupliqué
        unique_together = ('equation', 'categorie', 'code_libelle')













