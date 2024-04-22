from django.db import models

# Create your models here.
from django.db import models
#---------------etablissemnt------------------

class EtablissementMedical(models.Model):
    TYPE_CHOICES = (
        ('cabinet', 'Cabinet médical'),
        ('hopital', 'Hôpital'),
        # Ajoutez d'autres choix selon vos besoins
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nom} - {self.type}"

class Medecin(models.Model):
    etablissement = models.ForeignKey(EtablissementMedical, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    #-----------------------fin etablissement----------------

    from django.contrib.auth.hashers import make_password, check_password
from django.db import models

#--------------classe patient-----------------------------

class Patient(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=128)
    adresse = models.CharField(max_length=200)

    @classmethod
    def creer_compte(cls, nom, prenom, email, mot_de_passe, adresse):
        hashed_password = make_password(mot_de_passe)
        patient = cls.objects.create(nom=nom, prenom=prenom, email=email, mot_de_passe=hashed_password, adresse=adresse)
        return patient

    def s_authentifier(self, email, mot_de_passe):
        try:
            patient = Patient.objects.get(email=email)
            if check_password(mot_de_passe, patient.mot_de_passe):
                return True
            else:
                return False
        except Patient.DoesNotExist:
            return False

    def ajouter_rdv(self, date_heure, medecin):
        rendez_vous = RendezVous.objects.create(patient=self, medecin=medecin, date_heure=date_heure)
        return rendez_vous

    def modifier_rdv(self, rendez_vous, nouvelle_date_heure, nouveau_medecin):
        rendez_vous.date_heure = nouvelle_date_heure
        rendez_vous.medecin = nouveau_medecin
        rendez_vous.save()

    def consulter(self):
        return RendezVous.objects.filter(patient=self)

    def annuler(self, rendez_vous):
        rendez_vous.delete()

    def verifier_dispo_medecin(self, medecin, date_heure):
        return not RendezVous.objects.filter(medecin=medecin, date_heure=date_heure).exists()

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    

    #--------------------fin patient------------------------------

#------------debut secretaire-------------------------------

class SecretaireMedicale(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=128)

    def s_authentifier(self, email, mot_de_passe):
        try:
            secretaire = SecretaireMedicale.objects.get(email=email)
            if secretaire.mot_de_passe == mot_de_passe:
                return True
            else:
                return False
        except SecretaireMedicale.DoesNotExist:
            return False

    def planifier_rdv(self, rendez_vous):
        # Vérifier la disponibilité du médecin
        if rendez_vous.medecin.verifier_dispo(rendez_vous.date_heure):
            # Demander au médecin de confirmer le rendez-vous avec la salle de consultation et le matériel utilisé
            if rendez_vous.medecin.confirmer_rdv(rendez_vous):
                # Envoi de la notification de confirmation au patient et au médecin
                self.envoyer_notification_confirmation(rendez_vous)
                return True
        return False

    def verifier_dispo_medecin(self, medecin, date_heure):
        return medecin.verifier_dispo(date_heure)

    @staticmethod
    def envoyer_notification_confirmation(rendez_vous):
        # Envoi de la notification au patient
        rendez_vous.patient.envoyer_notification_confirmation(rendez_vous)
        # Envoi de la notification au médecin
        rendez_vous.medecin.envoyer_notification_confirmation(rendez_vous)

    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    #----------fin secretaire-------------------------


#----------------dossiers Patient---------------------------
    
class DossierPatient(models.Model):
    id = models.AutoField(primary_key=True)
    antecedant = models.TextField(blank=True)
    allergie = models.TextField(blank=True)
    medicament_actuel = models.TextField(blank=True)
    medecin = models.ForeignKey('Medecin', on_delete=models.CASCADE, related_name='dossiers_patient')
    secretaire_medicale = models.ForeignKey('SecretaireMedicale', on_delete=models.CASCADE, related_name='dossiers_patient', null=True, blank=True)
    # Autres champs de modèle, si nécessaire

    def __str__(self):
        return f"Dossier Patient #{self.id}"

    def mettre_a_jour_antecedant(self, nouvel_antecedant):
        self.antecedant = nouvel_antecedant
        self.save()

    def ajouter_allergie(self, nouvelle_allergie):
        if self.allergie:
            self.allergie += f", {nouvelle_allergie}"
        else:
            self.allergie = nouvelle_allergie
        self.save()

    def ajouter_medicament_actuel(self, nouveau_medicament):
        if self.medicament_actuel:
            self.medicament_actuel += f", {nouveau_medicament}"
        else:
            self.medicament_actuel = nouveau_medicament
        self.save()
#----------------------fin---------------------------------------
#---------------------debut rendez-vous---------------------
        
        from django.db import models
from datetime import datetime

class RendezVous(models.Model):
    id = models.AutoField(primary_key=True)
    date_heure = models.DateTimeField()
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='rendez_vous')
    medecin = models.ForeignKey('Medecin', on_delete=models.CASCADE, related_name='rendez_vous')
    salle_consultation = models.CharField(max_length=100, blank=True)
    materiel_utilise = models.CharField(max_length=100, blank=True)
    est_confirme = models.BooleanField(default=False)

    def __str__(self):
        return f"Rendez-vous #{self.id} - {self.date_heure}"
    
 #---------------------------fin rendez-vous------------------------------


#------debut ressources-----------------------------------------
    from django.db import models
class Ressource(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantite = models.IntegerField(default=0)
    etat = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    def mettre_a_jour_etat(self, etat):
        self.etat = etat
        self.save()

    @classmethod
    def ajouter(cls, nom, description='', quantite=0, etat=True):
        return cls.objects.create(nom=nom, description=description, quantite=quantite, etat=etat)
