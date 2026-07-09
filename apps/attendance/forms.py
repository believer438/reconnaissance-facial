import random

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import (
    AttendanceRecord,
    Camera,
    Classe,
    ClassroomSchedule,
    Course,
    CourseSession,
    DailyAttendance,
    JourFerie,
    RecognitionReviewQueue,
    Salle,
    Schedule,
    SchoolDayConfig,
    Student,
    SystemConfig,
    UserProfile,
)


class ClasseForm(forms.ModelForm):
    NIVEAU_CHOICES = [("", "Niveau")] + [(f"{i}e", f"{i}e") for i in range(1, 11)]
    LETTRE_CHOICES = [("", "Lettre")] + [(letter, letter) for letter in "ABCDEFGHIJ"]
    OPTION_CHOICES = [
        ("", "Sans option"),
        ("Scientifique", "Scientifique"),
        ("Litteraire", "Litteraire"),
        ("Commerciale et Gestion", "Commerciale et Gestion"),
        ("Pedagogie Generale", "Pedagogie Generale"),
        ("Technique Sociale", "Technique Sociale"),
        ("Electricite", "Electricite"),
        ("Mecanique", "Mecanique"),
        ("Construction", "Construction"),
        ("Nutrition", "Nutrition"),
        ("Coupe et Couture", "Coupe et Couture"),
    ]

    niveau = forms.ChoiceField(choices=NIVEAU_CHOICES, label="Niveau")
    lettre = forms.ChoiceField(choices=LETTRE_CHOICES, label="Lettre")
    option = forms.ChoiceField(choices=OPTION_CHOICES, label="Section / option", required=False)

    class Meta:
        model = Classe
        fields = ["niveau", "option", "annee_academique", "is_active"]
        widgets = {
            "annee_academique": forms.TextInput(attrs={"placeholder": "Ex. 2025-2026"}),
        }

    def clean(self):
        cleaned = super().clean()
        niveau = cleaned.get("niveau", "").strip()
        lettre = cleaned.get("lettre", "").strip()
        option = cleaned.get("option", "").strip()
        annee = cleaned.get("annee_academique", "").strip()

        if niveau and lettre:
            nom = f"{niveau} {lettre}"
            if option:
                nom = f"{nom} - {option}"
            cleaned["nom"] = nom

            duplicate = Classe.objects.filter(nom__iexact=nom, annee_academique=annee)
            if self.instance.pk:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise forms.ValidationError("Cette classe existe deja pour cette annee.")

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.nom = self.cleaned_data["nom"]
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ["nom", "batiment", "capacite", "description", "is_active"]
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Ex. Salle 101, Laboratoire A"}),
            "batiment": forms.TextInput(attrs={"placeholder": "Ex. Bâtiment Principal, Annexe"}),
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Informations complémentaires..."}),
        }


class JourFerieForm(forms.ModelForm):
    class Meta:
        model = JourFerie
        fields = ["nom", "date", "type_jour"]
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Ex. Fête nationale, Début vacances de Pâques..."}),
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            "classe", "course", "salle", "jour_semaine",
            "heure_debut", "heure_fin",
            "tolerance_retard_minutes", "minutes_avant_cours", "is_active",
        ]
        widgets = {
            "heure_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_fin": forms.TimeInput(attrs={"type": "time"}),
        }
        labels = {
            "classe": "Classe",
            "course": "Cours",
            "salle": "Salle",
            "jour_semaine": "Jour de la semaine",
            "heure_debut": "Heure de début",
            "heure_fin": "Heure de fin",
            "tolerance_retard_minutes": "Tolérance retard (min)",
            "minutes_avant_cours": "Fenêtre pré-cours (min)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["salle"].queryset = Salle.objects.filter(is_active=True).order_by("batiment", "nom")
        self.fields["salle"].empty_label = "— Pas de salle liée —"
        self.fields["salle"].required = False


class StudentForm(forms.ModelForm):
    CODE_MODE_AUTO = "auto"
    CODE_MODE_MANUAL = "manual"
    CODE_MODE_CHOICES = [
        (CODE_MODE_AUTO, "Automatique"),
        (CODE_MODE_MANUAL, "Manuel"),
    ]

    matricule_mode = forms.ChoiceField(
        choices=CODE_MODE_CHOICES,
        initial=CODE_MODE_AUTO,
        label="Mode matricule",
        required=False,
        widget=forms.RadioSelect,
    )
    student_code = forms.CharField(
        label="Matricule *",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Ex. MAT12345",
            "autocomplete": "off",
        }),
    )

    class Meta:
        model = Student
        fields = [
            "nom", "post_nom", "prenom", "sexe",
            "date_of_birth", "lieu_naissance", "adresse",
            "parent_nom", "parent_telephone",
            "student_code", "classe", "section", "annee_scolaire",
            "date_inscription", "statut",
            "email", "phone",
            "photo_profil",
        ]
        widgets = {
            "nom":             forms.TextInput(attrs={"placeholder": "Ex. Kabila"}),
            "post_nom":        forms.TextInput(attrs={"placeholder": "Ex. Mwangi"}),
            "prenom":          forms.TextInput(attrs={"placeholder": "Ex. Jean-Baptiste"}),
            "sexe":            forms.Select(),
            "date_of_birth":   forms.DateInput(attrs={"type": "date"}),
            "lieu_naissance":  forms.TextInput(attrs={"placeholder": "Ex. Kinshasa"}),
            "adresse":         forms.Textarea(attrs={"rows": 2, "placeholder": "Ex. Avenue de la Paix, Commune de Gombe..."}),
            "parent_nom":      forms.TextInput(attrs={"placeholder": "Ex. M. Jean Kabila"}),
            "parent_telephone":forms.TextInput(attrs={"placeholder": "+243 xxx xxx xxx"}),
            "student_code":    forms.TextInput(attrs={"placeholder": "Ex. 2025-001"}),
            "section":         forms.TextInput(attrs={"placeholder": "Ex. Sciences, Littéraire, Commerciale..."}),
            "annee_scolaire":  forms.TextInput(attrs={"placeholder": "Ex. 2025-2026"}),
            "date_inscription":forms.DateInput(attrs={"type": "date"}),
            "email":           forms.EmailInput(attrs={"placeholder": "eleve@ecole.cd"}),
            "phone":           forms.TextInput(attrs={"placeholder": "+243 xxx xxx xxx"}),
        }
        labels = {
            "nom":             "Nom de famille *",
            "post_nom":        "Post-nom",
            "prenom":          "Prénom(s)",
            "sexe":            "Sexe",
            "date_of_birth":   "Date de naissance",
            "lieu_naissance":  "Lieu de naissance",
            "adresse":         "Adresse",
            "parent_nom":      "Nom du parent / tuteur",
            "parent_telephone":"Téléphone du parent",
            "student_code":    "Matricule *",
            "classe":          "Classe",
            "section":         "Section",
            "annee_scolaire":  "Année scolaire",
            "date_inscription":"Date d'inscription",
            "statut":          "Statut",
            "email":           "Email (élève)",
            "phone":           "Téléphone (élève)",
            "photo_profil":    "Photo de profil officielle",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["matricule_mode"].initial = self.CODE_MODE_MANUAL
        self.fields["classe"].queryset = Classe.objects.filter(is_active=True).order_by("niveau", "nom")
        self.fields["classe"].empty_label = "— Sélectionner une classe —"
        self.fields["classe"].required = False
        self.fields["post_nom"].required = False
        self.fields["prenom"].required = False
        self.fields["sexe"].required = False
        self.fields["date_of_birth"].required = False
        self.fields["lieu_naissance"].required = False
        self.fields["adresse"].required = False
        self.fields["parent_nom"].required = False
        self.fields["parent_telephone"].required = False
        self.fields["section"].required = False
        self.fields["annee_scolaire"].required = False
        self.fields["date_inscription"].required = False
        self.fields["email"].required = False
        self.fields["phone"].required = False
        self.fields["photo_profil"].required = False

    def clean_nom(self):
        nom = self.cleaned_data.get("nom", "").strip()
        if not nom:
            raise forms.ValidationError("Le nom de famille est obligatoire.")
        return nom

    @staticmethod
    def generate_student_code() -> str:
        for _ in range(200):
            code = f"MAT{random.randint(0, 99999):05d}"
            if not Student.objects.filter(student_code__iexact=code).exists():
                return code
        raise forms.ValidationError("Impossible de generer un matricule disponible. Reessayez.")

    def clean_student_code(self):
        code = (self.cleaned_data.get("student_code") or "").strip().upper()
        mode = self.data.get(self.add_prefix("matricule_mode"))
        if not mode:
            mode = self.CODE_MODE_MANUAL if code else self.CODE_MODE_AUTO

        if mode == self.CODE_MODE_AUTO and not (self.instance and self.instance.pk):
            return self.generate_student_code()

        if not code:
            raise forms.ValidationError("Le matricule est obligatoire en mode manuel.")

        qs = Student.objects.filter(student_code__iexact=code)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ce matricule est deja utilise.")
        return code


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "faculty", "professor", "credits"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "Ex. MATH01"}),
            "name": forms.TextInput(attrs={"placeholder": "Ex. Mathématiques"}),
            "professor": forms.TextInput(attrs={"placeholder": "Ex. M. Kasongo"}),
        }


class CourseSessionForm(forms.ModelForm):
    class Meta:
        model = CourseSession
        fields = ["date", "start_time", "end_time", "room", "late_after_minutes", "minutes_avant_cours", "schedule", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "room": forms.TextInput(attrs={"placeholder": "Ex. Salle 101"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["schedule"].required = False
        self.fields["schedule"].empty_label = "— Aucun horaire lié —"


class SessionCancelForm(forms.Form):
    motif_annulation = forms.CharField(
        label="Motif d'annulation",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Ex. Professeur absent, Événement scolaire..."}),
    )


class AttendanceManualEditForm(forms.Form):
    STATUS_CHOICES = [
        (AttendanceRecord.STATUS_PRESENT, "Présent"),
        (AttendanceRecord.STATUS_LATE, "Retard"),
        (AttendanceRecord.STATUS_ABSENT, "Absent"),
        (AttendanceRecord.STATUS_EXCUSE, "Excusé / Justifié"),
    ]
    JUSTIFICATION_CHOICES = [
        ("", "— Aucun justificatif —"),
        ("maladie", "Maladie"),
        ("mission", "Mission officielle"),
        ("deuil", "Deuil"),
        ("autorisation", "Autorisation parentale"),
        ("autre", "Autre"),
    ]

    nouveau_statut = forms.ChoiceField(choices=STATUS_CHOICES, label="Nouveau statut")
    excuse_reason = forms.ChoiceField(
        choices=JUSTIFICATION_CHOICES, label="Type de justificatif", required=False,
    )
    excuse_notes = forms.CharField(
        label="Notes / Observations", required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Détails du justificatif, contexte..."}),
    )
    modifie_par = forms.CharField(
        label="Modifié par",
        max_length=120,
        initial="Admin",
        widget=forms.TextInput(attrs={"placeholder": "Ex. Direction, Secrétariat"}),
    )
    raison = forms.CharField(
        label="Raison de la modification",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Ex. Justificatif médical reçu..."}),
    )


class EnrollmentForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(is_active=True).order_by("full_name"),
        empty_label="— Sélectionner un élève —",
        label="Élève",
    )


class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ["name", "location", "salle", "zone_type", "detection_mode", "camera_type", "source", "resolution_w", "resolution_h", "is_active", "notes"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex. Entrée principale"}),
            "location": forms.TextInput(attrs={"placeholder": "Ex. Portail nord, Couloir A"}),
            "source": forms.TextInput(attrs={"placeholder": "Vide = webcam | 0/1 = USB | rtsp://... = IP"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
        help_texts = {
            "source": "Laissez vide pour webcam navigateur. '0' ou '1' pour caméra USB. URL RTSP pour caméra IP.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["salle"].queryset = Salle.objects.filter(is_active=True).order_by("batiment", "nom")
        self.fields["salle"].empty_label = "— Aucune salle liée —"
        self.fields["salle"].required = False
        self.fields["zone_type"].choices = [
            (Camera.ZONE_CHECK_IN, "Entree ecole (CHECK-IN)"),
            (Camera.ZONE_MONITORING, "Surveillance uniquement"),
        ]
        self.fields["zone_type"].help_text = "Seule la zone CHECK-IN enregistre la presence. La sortie n'est pas prise en compte."
        self.fields["zone_type"].widget.attrs.update({"class": "form-select"})


class ClassroomScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassroomSchedule
        fields = ["classroom", "start_time", "late_after_minutes"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
        }


class SchoolDayConfigForm(forms.ModelForm):
    class Meta:
        model = SchoolDayConfig
        fields = [
            "nom",
            "heure_ouverture", "heure_debut_cours", "heure_limite_arrivee",
            "heure_fin_cours", "heure_fermeture",
            "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi",
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Ex. Journée scolaire standard"}),
            "heure_ouverture": forms.TimeInput(attrs={"type": "time"}),
            "heure_debut_cours": forms.TimeInput(attrs={"type": "time"}),
            "heure_limite_arrivee": forms.TimeInput(attrs={"type": "time"}),
            "heure_fin_cours": forms.TimeInput(attrs={"type": "time"}),
            "heure_fermeture": forms.TimeInput(attrs={"type": "time"}),
        }
        labels = {
            "nom": "Nom de la configuration",
            "heure_ouverture": "Ouverture portail",
            "heure_debut_cours": "Début des cours (arrivée = Présent)",
            "heure_limite_arrivee": "Limite arrivée (après = Retard)",
            "heure_fin_cours": "Fin des cours",
            "heure_fermeture": "Fermeture portail",
        }

    @property
    def jours_fields(self):
        """Retourne les champs jours sous forme de liste itérable pour le template."""
        return [self["lundi"], self["mardi"], self["mercredi"],
                self["jeudi"], self["vendredi"], self["samedi"]]

    def clean(self):
        cleaned = super().clean()
        ordered_fields = [
            ("heure_ouverture", "Ouverture portail"),
            ("heure_debut_cours", "Début des cours"),
            ("heure_limite_arrivee", "Limite arrivée"),
            ("heure_fin_cours", "Fin des cours"),
            ("heure_fermeture", "Fermeture portail"),
        ]
        previous_value = None
        previous_label = ""
        for field_name, label in ordered_fields:
            value = cleaned.get(field_name)
            if value is None:
                continue
            if previous_value is not None and value < previous_value:
                raise forms.ValidationError(
                    f"Ordre horaire invalide : {label} doit etre apres {previous_label}."
                )
            previous_value = value
            previous_label = label
        if not any(cleaned.get(day) for day in ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]):
            raise forms.ValidationError("Selectionnez au moins un jour de classe.")
        return cleaned


class DailyAttendanceEditForm(forms.Form):
    STATUS_CHOICES = [
        (DailyAttendance.STATUS_PRESENT, "Présent"),
        (DailyAttendance.STATUS_RETARD, "En retard"),
        (DailyAttendance.STATUS_ABSENT, "Absent"),
        (DailyAttendance.STATUS_EXCUSE, "Excusé / Justifié"),
    ]

    nouveau_statut = forms.ChoiceField(choices=STATUS_CHOICES, label="Statut")
    heure_entree = forms.TimeField(
        required=False, label="Heure d'arrivée",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    excuse_reason = forms.ChoiceField(
        choices=DailyAttendance.EXCUSE_CHOICES,
        required=False, label="Type de justificatif",
    )
    excuse_notes = forms.CharField(
        required=False, label="Notes",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Contexte, documents reçus..."}),
    )
    modifie_par = forms.CharField(
        max_length=120, initial="Admin", label="Modifié par",
        widget=forms.TextInput(attrs={"placeholder": "Ex. Direction, Secrétariat..."}),
    )


User = get_user_model()


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe..."}),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Répéter le mot de passe..."}),
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial=UserProfile.ROLE_SECRETARIAT,
        label="Rôle dans l'établissement",
        widget=forms.RadioSelect,
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_staff", "is_superuser"]
        labels = {
            "username": "Nom d'utilisateur",
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse email",
            "is_staff": "Accès admin Django",
            "is_superuser": "Super-administrateur",
        }
        help_texts = {
            "username": "",
            "is_staff": "Donne accès à l'interface /admin/",
            "is_superuser": "Accès complet à toutes les fonctions",
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        if p1:
            try:
                validate_password(p1)
            except Exception as e:
                self.add_error("password1", e)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            role = self.cleaned_data.get("role", UserProfile.ROLE_SECRETARIAT)
            UserProfile.objects.update_or_create(user=user, defaults={"role": role})
        return user


class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="Rôle dans l'établissement",
        widget=forms.RadioSelect,
        required=False,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_staff", "is_superuser", "is_active"]
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse email",
            "is_staff": "Accès admin Django",
            "is_superuser": "Super-administrateur",
            "is_active": "Compte actif",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                profile = self.instance.profile
                self.fields["role"].initial = profile.role
            except Exception:
                self.fields["role"].initial = UserProfile.ROLE_SECRETARIAT

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            role = self.cleaned_data.get("role", UserProfile.ROLE_SECRETARIAT)
            if role:
                UserProfile.objects.update_or_create(user=user, defaults={"role": role})
        return user


class UserResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Nouveau mot de passe..."}),
    )
    password2 = forms.CharField(
        label="Confirmer",
        widget=forms.PasswordInput(attrs={"placeholder": "Répéter..."}),
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        if p1:
            try:
                validate_password(p1)
            except Exception as e:
                self.add_error("password1", e)
        return cleaned


class ReviewQueueValidateForm(forms.Form):
    ACTION_VALIDATE = "validate"
    ACTION_REJECT = "reject"
    ACTION_CHOICES = [
        (ACTION_VALIDATE, "Valider — enregistrer la présence"),
        (ACTION_REJECT, "Rejeter — ne pas enregistrer"),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, label="Décision")
    reviewed_by = forms.CharField(
        max_length=120, initial="Admin", label="Révisé par",
        widget=forms.TextInput(attrs={"placeholder": "Votre nom ou poste..."}),
    )
    review_notes = forms.CharField(
        required=False, label="Notes",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Justification de la décision..."}),
    )


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = [
            "retard_minutes",
            "ouverture_avant_minutes",
            "cooldown_detection_minutes",
            "seuil_confiance_haute",
            "seuil_distance_lbph",
            "seuil_alerte_absences",
            "filtrer_par_classe",
            "archiver_evenements_bruts",
        ]
        labels = {
            "retard_minutes": "Tolérance retard (min)",
            "ouverture_avant_minutes": "Fenêtre pré-cours (min)",
            "cooldown_detection_minutes": "Cooldown anti-doublon (min)",
            "seuil_distance_lbph": "Distance LBPH max (seuil de confiance)",
            "seuil_alerte_absences": "Seuil alerte absences",
            "filtrer_par_classe": "Filtrer la reconnaissance par classe",
            "archiver_evenements_bruts": "Archiver les événements bruts de détection",
        }
        widgets = {
            "retard_minutes": forms.NumberInput(attrs={"min": 0, "max": 120}),
            "ouverture_avant_minutes": forms.NumberInput(attrs={"min": 0, "max": 60}),
            "cooldown_detection_minutes": forms.NumberInput(attrs={"min": 1, "max": 60}),
            "seuil_distance_lbph": forms.NumberInput(attrs={"min": 10, "max": 150, "step": "0.5"}),
            "seuil_alerte_absences": forms.NumberInput(attrs={"min": 1, "max": 30}),
        }
