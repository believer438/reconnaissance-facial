from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

FACULTY_CHOICES = [
    ("info", "Informatique"),
    ("sci", "Sciences"),
    ("med", "Medecine / Sante"),
    ("droit", "Droit"),
    ("eco", "Economie / Gestion"),
    ("lettres", "Lettres & Sciences Humaines"),
    ("ing", "Ingenierie"),
    ("autre", "Autre"),
]

FACULTY_MAP = dict(FACULTY_CHOICES)

JOURS_SEMAINE = [
    (0, "Lundi"),
    (1, "Mardi"),
    (2, "Mercredi"),
    (3, "Jeudi"),
    (4, "Vendredi"),
    (5, "Samedi"),
]


# ─────────────────────────────────────────────────────────────────────────────
# JOURS FERIES
# ─────────────────────────────────────────────────────────────────────────────

class JourFerie(models.Model):
    TYPE_FERIE = "ferie"
    TYPE_VACANCES = "vacances"
    TYPE_SUSPENSION = "suspension"
    TYPE_CHOICES = [
        (TYPE_FERIE, "Jour ferie"),
        (TYPE_VACANCES, "Vacances / Conge"),
        (TYPE_SUSPENSION, "Suspension de cours"),
    ]

    nom = models.CharField(max_length=150, verbose_name="Motif / Description")
    date = models.DateField(unique=True, verbose_name="Date")
    type_jour = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_FERIE, verbose_name="Type")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]
        verbose_name = "Jour ferie"
        verbose_name_plural = "Jours feries"

    def __str__(self) -> str:
        return f"{self.nom} — {self.date:%d/%m/%Y} ({self.get_type_jour_display()})"

    @classmethod
    def is_ferie(cls, date) -> bool:
        return cls.objects.filter(date=date).exists()


# ─────────────────────────────────────────────────────────────────────────────
# SALLES
# ─────────────────────────────────────────────────────────────────────────────

class Salle(models.Model):
    nom = models.CharField(max_length=80, unique=True, verbose_name="Nom de la salle")
    batiment = models.CharField(max_length=80, blank=True, default="", verbose_name="Batiment")
    capacite = models.PositiveIntegerField(default=30, verbose_name="Capacite (etudiants)")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["batiment", "nom"]
        verbose_name = "Salle"
        verbose_name_plural = "Salles"

    def __str__(self) -> str:
        if self.batiment:
            return f"{self.batiment} — {self.nom}"
        return self.nom


# ─────────────────────────────────────────────────────────────────────────────
# CLASSES
# ─────────────────────────────────────────────────────────────────────────────

class Classe(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la classe")
    niveau = models.CharField(max_length=50, verbose_name="Niveau", help_text="Ex: L1, L2, L3, G3, Master 1")
    option = models.CharField(max_length=100, blank=True, default="", verbose_name="Option / Specialite")
    annee_academique = models.CharField(max_length=20, default="2025-2026", verbose_name="Annee academique")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["niveau", "nom"]
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

    def __str__(self) -> str:
        return self.nom or self.niveau

    @property
    def display_name(self) -> str:
        label = str(self)
        return f"{label} ({self.annee_academique})"

    def student_count(self) -> int:
        return self.students.filter(is_active=True).count()


# ─────────────────────────────────────────────────────────────────────────────
# ETUDIANTS
# ─────────────────────────────────────────────────────────────────────────────

class Student(models.Model):
    SEXE_CHOICES = [("M", "Masculin"), ("F", "Féminin")]
    STATUT_CHOICES = [
        ("actif",      "Actif"),
        ("transfere",  "Transféré"),
        ("suspendu",   "Suspendu"),
        ("exclu",      "Exclu"),
        ("diplome",    "Diplômé"),
        ("inactif",    "Inactif"),
    ]

    # ── Identité ──────────────────────────────────────────────────────────────
    full_name = models.CharField(max_length=240, unique=True, verbose_name="Nom complet")
    nom       = models.CharField(max_length=80,  blank=True, default="", verbose_name="Nom de famille")
    post_nom  = models.CharField(max_length=80,  blank=True, default="", verbose_name="Post-nom")
    prenom    = models.CharField(max_length=80,  blank=True, default="", verbose_name="Prénom(s)")
    sexe      = models.CharField(max_length=1, choices=SEXE_CHOICES, blank=True, default="", verbose_name="Sexe")

    # ── Naissance & adresse ───────────────────────────────────────────────────
    date_of_birth   = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    lieu_naissance  = models.CharField(max_length=150, blank=True, default="", verbose_name="Lieu de naissance")
    adresse         = models.TextField(blank=True, default="", verbose_name="Adresse")

    # ── Parent / Tuteur ───────────────────────────────────────────────────────
    parent_nom       = models.CharField(max_length=150, blank=True, default="", verbose_name="Nom du parent / tuteur")
    parent_telephone = models.CharField(max_length=30,  blank=True, default="", verbose_name="Téléphone du parent")

    # ── Scolarité ─────────────────────────────────────────────────────────────
    student_code   = models.CharField(max_length=50, unique=True, verbose_name="Matricule")
    classe         = models.ForeignKey(
        Classe, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="students", verbose_name="Classe",
    )
    classroom      = models.CharField(max_length=80, blank=True, default="", verbose_name="Classe (snapshot)")
    section        = models.CharField(max_length=80,  blank=True, default="", verbose_name="Section")
    annee_scolaire = models.CharField(max_length=20,  blank=True, default="", verbose_name="Année scolaire")
    date_inscription = models.DateField(null=True, blank=True, verbose_name="Date d'inscription")
    statut         = models.CharField(max_length=20, choices=STATUT_CHOICES, default="actif", verbose_name="Statut")

    # ── Contact ───────────────────────────────────────────────────────────────
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="Téléphone élève")

    # ── Photo de profil officielle ────────────────────────────────────────────
    photo_profil = models.ImageField(
        upload_to="students/profil/", null=True, blank=True,
        verbose_name="Photo de profil",
    )

    # ── Champs hérités ────────────────────────────────────────────────────────
    faculty    = models.CharField(max_length=20, choices=FACULTY_CHOICES, blank=True, default="", verbose_name="Faculte")
    is_active  = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["student_code"]),
            models.Index(fields=["classe"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["statut"]),
        ]

    def save(self, *args, **kwargs):
        if self.nom:
            parts = [p for p in [self.nom, self.post_nom, self.prenom] if p]
            computed = " ".join(parts)
            self.full_name = computed
        elif not self.full_name:
            self.full_name = self.student_code or "—"
        self.is_active = self.statut == "actif"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.full_name} ({self.student_code})"

    @property
    def nom_complet(self) -> str:
        if self.nom:
            return " ".join(p for p in [self.nom, self.post_nom, self.prenom] if p)
        return self.full_name

    @property
    def classe_display(self) -> str:
        if self.classe:
            return str(self.classe)
        return self.classroom or "—"

    @property
    def faculty_display(self) -> str:
        return FACULTY_MAP.get(self.faculty, self.faculty or "—")

    @property
    def statut_badge(self) -> str:
        return {
            "actif":     "badge-green",
            "transfere": "badge-yellow",
            "suspendu":  "badge-orange",
            "exclu":     "badge-red",
            "diplome":   "badge-blue",
            "inactif":   "badge-muted",
        }.get(self.statut, "badge-muted")

    @property
    def nb_embeddings(self) -> int:
        return self.face_embeddings.count()

    def attendance_rate(self) -> float:
        total = self.daily_attendances.filter(status__in=["present", "retard", "absent", "excuse"]).count()
        absent = self.daily_attendances.filter(status="absent").count()
        if total == 0:
            return 0.0
        return round((total - absent) / total * 100, 1)

    def absences_count(self) -> int:
        return self.daily_attendances.filter(status="absent").count()


class TrainingPhoto(models.Model):
    ANGLE_CHOICES = [
        ("face",     "Face"),
        ("gauche",   "Gauche"),
        ("droite",   "Droite"),
        ("incline",  "Légèrement incliné"),
        ("autre",    "Autre"),
    ]

    student       = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="photos")
    image         = models.ImageField(upload_to="students")
    angle_tag     = models.CharField(max_length=20, choices=ANGLE_CHOICES, blank=True, default="", verbose_name="Angle")
    trained_at    = models.DateTimeField(null=True, blank=True, verbose_name="Date d'entrainement")
    face_detected = models.BooleanField(default=True, verbose_name="Visage detecte")
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["student__full_name", "created_at"]

    def __str__(self) -> str:
        return f"Photo {self.student.full_name}"

    @property
    def is_trained(self) -> bool:
        return self.trained_at is not None


# ─────────────────────────────────────────────────────────────────────────────
# EMPREINTES FACIALES (Embeddings)
# ─────────────────────────────────────────────────────────────────────────────

class FaceEmbedding(models.Model):
    """
    Vecteur d'empreinte faciale (LBP histogram 256-dim).
    Généré automatiquement à l'ajout de chaque photo.
    Aucun réentraînement complet n'est nécessaire.
    """
    student  = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name="face_embeddings", verbose_name="Élève",
    )
    photo    = models.OneToOneField(
        TrainingPhoto, on_delete=models.CASCADE,
        null=True, blank=True, related_name="embedding",
        verbose_name="Photo source",
    )
    vector   = models.BinaryField(verbose_name="Vecteur (256 floats)")
    angle_tag = models.CharField(max_length=20, blank=True, default="", verbose_name="Angle")
    score_qualite = models.FloatField(default=0.0, verbose_name="Score qualité (netteté)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["student__full_name", "created_at"]
        verbose_name = "Empreinte faciale"
        verbose_name_plural = "Empreintes faciales"

    def __str__(self) -> str:
        return f"Embedding {self.student.full_name} ({self.created_at:%d/%m/%Y})"


# ─────────────────────────────────────────────────────────────────────────────
# COURS
# ─────────────────────────────────────────────────────────────────────────────

class Course(models.Model):
    code = models.CharField(max_length=30, unique=True, verbose_name="Code")
    name = models.CharField(max_length=150, verbose_name="Intitule")
    faculty = models.CharField(max_length=20, choices=FACULTY_CHOICES, blank=True, default="", verbose_name="Faculte")
    professor = models.CharField(max_length=120, blank=True, default="", verbose_name="Professeur")
    credits = models.PositiveIntegerField(default=3, verbose_name="Credits")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    @property
    def faculty_display(self) -> str:
        return FACULTY_MAP.get(self.faculty, self.faculty or "—")


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("student", "course")]
        ordering = ["student__full_name"]

    def __str__(self) -> str:
        return f"{self.student.full_name} -> {self.course.code}"


# ─────────────────────────────────────────────────────────────────────────────
# HORAIRES
# ─────────────────────────────────────────────────────────────────────────────

class Schedule(models.Model):
    """Horaire hebdomadaire : classe + cours + jour + horaires."""

    classe = models.ForeignKey(
        Classe, on_delete=models.CASCADE, related_name="schedules", verbose_name="Classe",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="schedules", verbose_name="Cours",
    )
    salle = models.ForeignKey(
        Salle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="schedules", verbose_name="Salle",
    )
    jour_semaine = models.IntegerField(choices=JOURS_SEMAINE, verbose_name="Jour de la semaine")
    heure_debut = models.TimeField(verbose_name="Heure de debut")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    tolerance_retard_minutes = models.PositiveIntegerField(
        default=15, verbose_name="Tolerance retard (min)",
        help_text="Minutes apres le debut avant d'etre marque en retard",
    )
    minutes_avant_cours = models.PositiveIntegerField(
        default=10, verbose_name="Fenetre pre-cours (min)",
        help_text="Nombre de minutes avant le debut ou la detection est autorisee",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["jour_semaine", "heure_debut"]
        verbose_name = "Horaire"
        verbose_name_plural = "Horaires"

    def __str__(self) -> str:
        jour = dict(JOURS_SEMAINE).get(self.jour_semaine, "?")
        return f"{self.classe} | {self.course.code} | {jour} {self.heure_debut:%H:%M}–{self.heure_fin:%H:%M}"

    @property
    def jour_display(self) -> str:
        return dict(JOURS_SEMAINE).get(self.jour_semaine, "—")

    def clean(self):
        """Validation : empêcher les chevauchements d'horaires pour la même classe."""
        if not self.heure_debut or not self.heure_fin or not self.classe_id:
            return
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de debut doit être avant l'heure de fin.")

        # Detect overlaps for same class on same day
        overlapping = Schedule.objects.filter(
            classe=self.classe,
            jour_semaine=self.jour_semaine,
            is_active=True,
        ).exclude(pk=self.pk)

        for s in overlapping:
            # Two intervals overlap if start1 < end2 AND start2 < end1
            if self.heure_debut < s.heure_fin and s.heure_debut < self.heure_fin:
                raise ValidationError(
                    f"Chevauchement d'horaire : la classe {self.classe} a deja "
                    f"{s.course.code} ce jour de {s.heure_debut:%H:%M} a {s.heure_fin:%H:%M}."
                )

        # Detect overlaps for same professor on same day (if professor set)
        if self.course.professor:
            prof_overlapping = Schedule.objects.filter(
                course__professor=self.course.professor,
                jour_semaine=self.jour_semaine,
                is_active=True,
            ).exclude(pk=self.pk).exclude(course=self.course)
            for s in prof_overlapping:
                if self.heure_debut < s.heure_fin and s.heure_debut < self.heure_fin:
                    raise ValidationError(
                        f"Chevauchement : le professeur {self.course.professor} "
                        f"a deja {s.course.code} pour {s.classe} ce jour."
                    )

        # Detect overlaps for same room on same day
        if self.salle_id:
            salle_overlapping = Schedule.objects.filter(
                salle=self.salle,
                jour_semaine=self.jour_semaine,
                is_active=True,
            ).exclude(pk=self.pk)
            for s in salle_overlapping:
                if self.heure_debut < s.heure_fin and s.heure_debut < self.heure_fin:
                    raise ValidationError(
                        f"Chevauchement de salle : {self.salle} est deja occupee "
                        f"par {s.course.code} ({s.classe}) ce jour."
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ClassroomSchedule(models.Model):
    """Ancien modele d'horaire — conserve pour compatibilite."""
    classroom = models.CharField(max_length=80, unique=True)
    start_time = models.TimeField()
    late_after_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["classroom"]

    def __str__(self) -> str:
        return f"{self.classroom} - {self.start_time}"


# ─────────────────────────────────────────────────────────────────────────────
# CAMERAS
# ─────────────────────────────────────────────────────────────────────────────

class Camera(models.Model):
    TYPE_WEBCAM = "webcam"
    TYPE_USB = "usb"
    TYPE_RTSP = "rtsp"
    TYPE_CHOICES = [
        ("webcam", "Webcam navigateur"),
        ("usb", "Camera USB (serveur)"),
        ("rtsp", "Camera IP (RTSP)"),
    ]

    name = models.CharField(max_length=100, verbose_name="Nom")
    location = models.CharField(max_length=150, blank=True, default="", verbose_name="Emplacement")
    salle = models.ForeignKey(
        Salle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="cameras", verbose_name="Salle associee",
    )
    camera_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="webcam", verbose_name="Type")
    source = models.CharField(
        max_length=300, blank=True, default="",
        verbose_name="Source",
        help_text="Vide = webcam par defaut. '0','1' = index USB. 'rtsp://...' = camera IP.",
    )
    ZONE_CHECK_IN = "check_in"
    ZONE_CHECK_OUT = "check_out"
    ZONE_MONITORING = "monitoring"
    ZONE_CHOICES = [
        (ZONE_CHECK_IN, "Entree ecole (CHECK-IN)"),
        (ZONE_MONITORING, "Surveillance (monitoring)"),
    ]

    zone_type = models.CharField(
        max_length=12, choices=ZONE_CHOICES, default=ZONE_MONITORING,
        verbose_name="Zone",
        help_text="CHECK-IN = enregistre l'arrivee des eleves. MONITORING = surveillance sans presence.",
    )

    # ── Mode de détection ────────────────────────────────────────────────────
    MODE_RECOGNITION = "recognition"
    MODE_MONITORING = "monitoring_only"
    MODE_OFF = "off"
    MODE_CHOICES = [
        (MODE_RECOGNITION, "Reconnaissance active (RECOGNITION)"),
        (MODE_MONITORING, "Surveillance seulement (MONITORING)"),
        (MODE_OFF, "Desactivee (OFF)"),
    ]
    detection_mode = models.CharField(
        max_length=16, choices=MODE_CHOICES, default=MODE_RECOGNITION,
        verbose_name="Mode detection",
        help_text="RECOGNITION = IA active. MONITORING = flux video sans IA. OFF = camera inactive.",
    )

    # ── Statut temps réel ────────────────────────────────────────────────────
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Dernier contact")
    is_online = models.BooleanField(default=False, verbose_name="En ligne")
    fps_estimate = models.FloatField(default=0.0, verbose_name="FPS estime")
    frames_processed = models.PositiveIntegerField(default=0, verbose_name="Images traitees")
    error_count = models.PositiveIntegerField(default=0, verbose_name="Nb erreurs")
    last_error = models.CharField(max_length=500, blank=True, default="", verbose_name="Derniere erreur")

    resolution_w = models.PositiveIntegerField(default=640, verbose_name="Largeur (px)")
    resolution_h = models.PositiveIntegerField(default=480, verbose_name="Hauteur (px)")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_camera_type_display()})"

    @property
    def source_display(self) -> str:
        if self.camera_type == self.TYPE_WEBCAM:
            return "Navigateur (getUserMedia)"
        if self.camera_type == self.TYPE_USB:
            return f"USB index {self.source or '0'}"
        return self.source or "rtsp://..."

    @property
    def status_badge(self) -> str:
        """Badge CSS selon l'état de la caméra."""
        if not self.is_active:
            return "badge-muted"
        if self.detection_mode == self.MODE_OFF:
            return "badge-muted"
        if not self.is_online:
            return "badge-red"
        if self.detection_mode == self.MODE_RECOGNITION:
            return "badge-green"
        return "badge-yellow"

    @property
    def status_label(self) -> str:
        if not self.is_active:
            return "Inactive"
        if self.detection_mode == self.MODE_OFF:
            return "OFF"
        if not self.is_online:
            return "Hors ligne"
        if self.detection_mode == self.MODE_RECOGNITION:
            return "RECOGNITION"
        return "MONITORING"

    def mark_online(self, fps: float = 0.0) -> None:
        """Appelé par le heartbeat de la caméra pour mettre à jour le statut."""
        now = timezone.now()
        self.last_seen = now
        self.is_online = True
        self.fps_estimate = fps
        self.frames_processed += 1
        Camera.objects.filter(pk=self.pk).update(
            last_seen=now, is_online=True, fps_estimate=fps,
            frames_processed=models.F("frames_processed") + 1,
        )

    def mark_offline(self, error: str = "") -> None:
        Camera.objects.filter(pk=self.pk).update(
            is_online=False,
            last_error=error[:500],
            error_count=models.F("error_count") + 1,
        )


# ─────────────────────────────────────────────────────────────────────────────
# FILE DE REVUE — Reconnaissances incertaines (LOW_CONFIDENCE / MULTIPLE_MATCH)
# ─────────────────────────────────────────────────────────────────────────────

class RecognitionReviewQueue(models.Model):
    """
    File de validation manuelle pour les reconnaissances à faible confiance.

    Quand le score LBPH se situe dans la zone de doute (entre seuil_haute et seuil_limite),
    le système NE marque PAS la présence automatiquement. Il crée un ticket ici pour
    que l'admin puisse valider ou rejeter manuellement.

    Règle d'or : mieux vaut un faux rejet qu'un faux positif (mauvaise présence officielle).
    """
    # Statut du ticket
    STATUS_PENDING = "pending"
    STATUS_VALIDATED = "validated"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente de revue"),
        (STATUS_VALIDATED, "Valide — presence enregistree"),
        (STATUS_REJECTED, "Rejete — pas de presence"),
    ]

    # Raison technique
    TECH_LOW_CONFIDENCE = "low_confidence"
    TECH_MULTIPLE_MATCH = "multiple_match"
    TECH_CHOICES = [
        (TECH_LOW_CONFIDENCE, "Faible confiance (LOW_CONFIDENCE)"),
        (TECH_MULTIPLE_MATCH, "Correspondance ambigue (MULTIPLE_MATCH)"),
    ]

    # Étudiant proposé par le modèle IA
    student_proposed = models.ForeignKey(
        "Student", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="review_proposals",
        verbose_name="Etudiant propose par l'IA",
    )
    confidence_proposed = models.FloatField(
        default=0.0, verbose_name="Score confiance (0-100, plus haut = meilleur)"
    )
    distance_lbph = models.FloatField(
        default=0.0, verbose_name="Distance LBPH brute"
    )

    # Second candidat (pour MULTIPLE_MATCH)
    second_candidate = models.ForeignKey(
        "Student", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="review_second_proposals",
        verbose_name="Second candidat",
    )
    confidence_second = models.FloatField(default=0.0, verbose_name="Score second candidat")

    # Contexte de détection
    technical_status = models.CharField(
        max_length=20, choices=TECH_CHOICES, default=TECH_LOW_CONFIDENCE,
        verbose_name="Statut technique",
    )
    camera = models.ForeignKey(
        Camera, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="review_queue_items",
        verbose_name="Camera",
    )
    course_session = models.ForeignKey(
        "CourseSession", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="review_queue_items",
        verbose_name="Session de cours",
    )
    daily_date = models.DateField(null=True, blank=True, verbose_name="Date (presence journaliere)")
    face_image = models.ImageField(
        upload_to="review_queue/%Y/%m/%d/",
        null=True, blank=True,
        verbose_name="Capture du visage",
    )
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name="Detecte le")
    source = models.CharField(max_length=20, default="live", verbose_name="Source")

    # Revue admin
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING,
        verbose_name="Statut revue",
    )
    reviewed_by = models.CharField(max_length=120, blank=True, default="", verbose_name="Revise par")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Revise le")
    review_notes = models.TextField(blank=True, default="", verbose_name="Notes")

    class Meta:
        ordering = ["-detected_at"]
        verbose_name = "Ticket de revue reconnaissance"
        verbose_name_plural = "File de revue reconnaissance"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["detected_at"]),
        ]

    def __str__(self) -> str:
        name = self.student_proposed.full_name if self.student_proposed else "Inconnu"
        return f"{name} — {self.get_technical_status_display()} — {self.detected_at:%d/%m %H:%M}"

    @property
    def confidence_badge(self) -> str:
        if self.confidence_proposed >= 75:
            return "badge-yellow"
        if self.confidence_proposed >= 60:
            return "badge-orange"
        return "badge-red"


# ─────────────────────────────────────────────────────────────────────────────
# SESSIONS DE COURS
# ─────────────────────────────────────────────────────────────────────────────

class CourseSession(models.Model):
    STATUS_EN_ATTENTE = "en_attente"
    STATUS_OUVERT = "ouvert"
    STATUS_FERME = "ferme"
    STATUS_ANNULE = "annule"
    STATUS_CHOICES = [
        (STATUS_EN_ATTENTE, "En attente"),
        (STATUS_OUVERT, "Ouvert"),
        (STATUS_FERME, "Ferme"),
        (STATUS_ANNULE, "Annule"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    schedule = models.ForeignKey(
        Schedule, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sessions", verbose_name="Horaire source",
    )
    date = models.DateField(verbose_name="Date")
    start_time = models.TimeField(verbose_name="Heure debut")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Heure fin")
    room = models.CharField(max_length=80, blank=True, default="", verbose_name="Salle")
    late_after_minutes = models.PositiveIntegerField(default=15, verbose_name="Retard apres (min)")
    minutes_avant_cours = models.PositiveIntegerField(default=10, verbose_name="Fenetre pre-cours (min)")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    motif_annulation = models.CharField(max_length=200, blank=True, default="", verbose_name="Motif d'annulation")
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_EN_ATTENTE, verbose_name="Statut",
    )
    closed = models.BooleanField(default=False, verbose_name="Session fermee (legacy)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-start_time"]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["course", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.course.code} — {self.date} {self.start_time}"

    @property
    def is_open(self) -> bool:
        return self.status == self.STATUS_OUVERT

    @property
    def is_closed(self) -> bool:
        return self.status == self.STATUS_FERME

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.STATUS_ANNULE

    @property
    def status_badge_class(self) -> str:
        return {
            self.STATUS_EN_ATTENTE: "badge-warning",
            self.STATUS_OUVERT: "badge-success",
            self.STATUS_FERME: "badge-muted",
            self.STATUS_ANNULE: "badge-red",
        }.get(self.status, "")

    def get_enrolled_students(self):
        if self.schedule:
            return self.schedule.classe.students.filter(is_active=True)
        return Student.objects.filter(
            enrollments__course=self.course, is_active=True
        )

    def generate_absents(self) -> int:
        enrolled = self.get_enrolled_students()
        present_ids = set(
            AttendanceRecord.objects.filter(
                course_session=self,
                status__in=[AttendanceRecord.STATUS_PRESENT, AttendanceRecord.STATUS_LATE, AttendanceRecord.STATUS_EXCUSE],
            ).values_list("student_id", flat=True)
        )
        count = 0
        for student in enrolled:
            if student.id not in present_ids:
                AttendanceRecord.objects.get_or_create(
                    student=student,
                    course_session=self,
                    defaults={
                        "student_name_snapshot": student.full_name,
                        "classroom_snapshot": student.classe_display,
                        "recognized_at": timezone.now(),
                        "confidence_score": 0,
                        "status": AttendanceRecord.STATUS_ABSENT,
                        "source": "auto",
                    },
                )
                count += 1
        return count


# ─────────────────────────────────────────────────────────────────────────────
# PRESENCES
# ─────────────────────────────────────────────────────────────────────────────

class AttendanceRecord(models.Model):
    STATUS_PRESENT = "present"
    STATUS_LATE = "late"
    STATUS_ABSENT = "absent"
    STATUS_UNKNOWN = "unknown"
    STATUS_REFUSED = "refused"
    STATUS_EXCUSE = "excuse"
    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_LATE, "Retard"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_EXCUSE, "Excuse / Justifie"),
        (STATUS_UNKNOWN, "Inconnu"),
        (STATUS_REFUSED, "Refuse (hors horaire)"),
    ]

    JUSTIFICATION_CHOICES = [
        ("", "—"),
        ("maladie", "Maladie"),
        ("mission", "Mission officielle"),
        ("deuil", "Deuil"),
        ("autorisation", "Autorisation speciale"),
        ("autre", "Autre"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendance_records", null=True, blank=True,
    )
    course_session = models.ForeignKey(
        CourseSession, on_delete=models.SET_NULL, related_name="attendance_records", null=True, blank=True,
    )
    camera = models.ForeignKey(
        Camera, on_delete=models.SET_NULL, related_name="attendance_records", null=True, blank=True,
    )
    student_name_snapshot = models.CharField(max_length=120)
    classroom_snapshot = models.CharField(max_length=80, blank=True)
    recognized_at = models.DateTimeField(default=timezone.now)
    confidence_score = models.FloatField(default=0)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)
    source = models.CharField(max_length=20, default="photo")

    # Justificatif
    excuse_reason = models.CharField(
        max_length=20, choices=JUSTIFICATION_CHOICES, blank=True, default="",
        verbose_name="Type de justificatif",
    )
    excuse_notes = models.TextField(blank=True, default="", verbose_name="Notes justificatif")
    modified_by = models.CharField(max_length=120, blank=True, default="", verbose_name="Modifie par")

    class Meta:
        ordering = ["-recognized_at"]
        indexes = [
            models.Index(fields=["student"]),
            models.Index(fields=["course_session"]),
            models.Index(fields=["status"]),
            models.Index(fields=["recognized_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.student_name_snapshot} — {self.recognized_at:%Y-%m-%d %H:%M}"


# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL D'AUDIT
# ─────────────────────────────────────────────────────────────────────────────

class AttendanceAuditLog(models.Model):
    attendance_record = models.ForeignKey(
        AttendanceRecord, on_delete=models.CASCADE, related_name="audit_logs",
    )
    modifie_par = models.CharField(max_length=120, default="admin", verbose_name="Modifie par")
    ancienne_valeur = models.CharField(max_length=20, verbose_name="Ancienne valeur")
    nouvelle_valeur = models.CharField(max_length=20, verbose_name="Nouvelle valeur")
    raison = models.TextField(blank=True, default="", verbose_name="Raison / Justificatif")
    date_modification = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_modification"]
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"

    def __str__(self) -> str:
        return (
            f"{self.modifie_par} : {self.ancienne_valeur} → {self.nouvelle_valeur} "
            f"({self.date_modification:%d/%m/%Y %H:%M})"
        )


class UnknownFaceLog(models.Model):
    image = models.ImageField(upload_to="unknown_faces/", null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, default="photo")
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["-detected_at"]

    def __str__(self) -> str:
        return f"Inconnu — {self.detected_at:%Y-%m-%d %H:%M}"


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION SYSTEME (singleton)
# ─────────────────────────────────────────────────────────────────────────────

class SystemConfig(models.Model):
    """
    Configuration globale du systeme — un seul enregistrement (pk=1).
    Toutes les regles metier configurables sont ici.
    Utilisez SystemConfig.get() pour acceder aux valeurs.
    """

    # Regles temporelles
    retard_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name="Tolerance retard (min)",
        help_text="Minutes apres le debut du cours avant d'etre marque en retard.",
    )
    ouverture_avant_minutes = models.PositiveIntegerField(
        default=10,
        verbose_name="Fenetre pre-cours (min)",
        help_text="Minutes avant le debut ou la detection est acceptee.",
    )
    cooldown_detection_minutes = models.PositiveIntegerField(
        default=5,
        verbose_name="Cooldown anti-doublon (min)",
        help_text="Intervalle minimal entre deux detections du meme etudiant dans la meme session.",
    )

    # Seuils de confiance (distance inverse du score — plus bas = meilleure correspondance)
    seuil_confiance_haute = models.FloatField(
        default=58.0,
        verbose_name="Seuil haute confiance (auto-accepte)",
        help_text="Distance EN DESSOUS de ce seuil : reconnaissance directe sans revue. Recommande : 55-62.",
    )
    seuil_distance_lbph = models.FloatField(
        default=75.0,
        verbose_name="Seuil limite (zone de doute)",
        help_text="Distance EN DESSOUS de ce seuil : mis en file de revue. Au-dessus : INCONNU. Recommande : 70-80.",
    )

    # Alertes
    seuil_alerte_absences = models.PositiveIntegerField(
        default=3,
        verbose_name="Seuil alerte absences",
        help_text="Nombre d'absences a partir duquel l'alerte apparait sur le tableau de bord.",
    )

    # Comportements
    filtrer_par_classe = models.BooleanField(
        default=True,
        verbose_name="Filtrer par classe",
        help_text="Ne reconnaitre que les etudiants de la classe liee a la session active.",
    )
    archiver_evenements_bruts = models.BooleanField(
        default=True,
        verbose_name="Archiver evenements bruts",
        help_text="Journaliser chaque detection dans FaceDetectionEvent pour audit et debug.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration systeme"
        verbose_name_plural = "Configuration systeme"

    def __str__(self) -> str:
        return "Configuration du systeme"

    @classmethod
    def get(cls) -> "SystemConfig":
        """Retourne l'instance singleton, la cree si elle n'existe pas."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL D'EVENEMENTS BRUTS (pipeline de detection)
# ─────────────────────────────────────────────────────────────────────────────

class FaceDetectionEvent(models.Model):
    """
    Journal d'evenements bruts — chaque detection produit un evenement.
    Pipeline : DETECTE → RECONNU → VALIDE → ENREGISTRE
                                 → REFUSE / DOUBLON / HORS_CLASSE / INCONNU
    """

    ETAPE_DETECTE = "detecte"
    ETAPE_RECONNU = "reconnu"
    ETAPE_ENREGISTRE = "enregistre"
    ETAPE_REFUSE = "refuse"
    ETAPE_HORS_CLASSE = "hors_cl"
    ETAPE_INCONNU = "inconnu"
    ETAPE_DOUBLON = "doublon"
    ETAPE_TROP_TOT = "trop_tot"

    ETAPE_CHOICES = [
        (ETAPE_DETECTE, "Visage detecte"),
        (ETAPE_RECONNU, "Identite probable"),
        (ETAPE_ENREGISTRE, "Presence enregistree"),
        (ETAPE_REFUSE, "Refuse (hors horaire)"),
        (ETAPE_HORS_CLASSE, "Hors classe (filtre)"),
        (ETAPE_INCONNU, "Visage inconnu"),
        (ETAPE_DOUBLON, "Doublon (deja marque)"),
        (ETAPE_TROP_TOT, "Trop tot (avant fenetre)"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="detection_events",
    )
    course_session = models.ForeignKey(
        CourseSession, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="detection_events",
    )
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True, blank=True)
    etape = models.CharField(max_length=10, choices=ETAPE_CHOICES)
    confiance = models.FloatField(default=0.0, verbose_name="Confiance (%)")
    source = models.CharField(max_length=20, default="live")
    raison = models.CharField(max_length=200, blank=True, default="", verbose_name="Raison")
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-detected_at"]
        verbose_name = "Evenement de detection"
        verbose_name_plural = "Evenements de detection"
        indexes = [
            models.Index(fields=["detected_at"]),
            models.Index(fields=["etape"]),
            models.Index(fields=["student", "detected_at"]),
        ]

    def __str__(self) -> str:
        nom = self.student.full_name if self.student else "Inconnu"
        return f"{self.get_etape_display()} — {nom} ({self.detected_at:%H:%M:%S})"

    @property
    def etape_badge_class(self) -> str:
        return {
            self.ETAPE_ENREGISTRE: "badge-green",
            self.ETAPE_RECONNU: "badge-blue",
            self.ETAPE_REFUSE: "badge-red",
            self.ETAPE_HORS_CLASSE: "badge-yellow",
            self.ETAPE_INCONNU: "badge-muted",
            self.ETAPE_DOUBLON: "badge-muted",
            self.ETAPE_TROP_TOT: "badge-yellow",
            self.ETAPE_DETECTE: "badge-muted",
        }.get(self.etape, "badge-muted")


# ─────────────────────────────────────────────────────────────────────────────
# ECOLE SECONDAIRE — CONFIGURATION JOURNEE SCOLAIRE
# ─────────────────────────────────────────────────────────────────────────────

class SchoolDayConfig(models.Model):
    """
    Configuration de la journée scolaire pour école secondaire (singleton pk=1).
    Définit les plages horaires d'arrivée, de retard et de fin des cours.
    """
    nom = models.CharField(max_length=100, default="Journee scolaire")

    # Horaires clés
    heure_ouverture = models.TimeField(default="06:30", verbose_name="Ouverture portail")
    heure_debut_cours = models.TimeField(default="07:00", verbose_name="Debut cours (arrivee = Present)")
    heure_limite_arrivee = models.TimeField(default="07:30", verbose_name="Heure limite arrivee (apres = Retard)")
    heure_fin_cours = models.TimeField(default="15:30", verbose_name="Fin des cours")
    heure_sortie_precoce = models.TimeField(default="15:00", verbose_name="Champ historique non utilise")
    heure_fermeture = models.TimeField(default="17:00", verbose_name="Fermeture portail")

    # Jours de classe
    lundi = models.BooleanField(default=True, verbose_name="Lundi")
    mardi = models.BooleanField(default=True, verbose_name="Mardi")
    mercredi = models.BooleanField(default=True, verbose_name="Mercredi")
    jeudi = models.BooleanField(default=True, verbose_name="Jeudi")
    vendredi = models.BooleanField(default=True, verbose_name="Vendredi")
    samedi = models.BooleanField(default=False, verbose_name="Samedi")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuration journee scolaire"
        verbose_name_plural = "Configuration journee scolaire"

    def __str__(self) -> str:
        return self.nom

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls) -> "SchoolDayConfig":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def is_school_day(self, date) -> bool:
        """Retourne True si cette date est un jour de classe selon la config."""
        weekday = date.weekday()  # 0=lundi, 6=dimanche
        mapping = [self.lundi, self.mardi, self.mercredi, self.jeudi, self.vendredi, self.samedi, False]
        return mapping[weekday]


# ─────────────────────────────────────────────────────────────────────────────
# ECOLE SECONDAIRE — PRESENCE JOURNALIERE
# ─────────────────────────────────────────────────────────────────────────────

class DailyAttendance(models.Model):
    """
    Présence journalière d'un élève à l'école secondaire.
    Un enregistrement par élève par jour.

    Pipeline :
      Caméra CHECK-IN → heure_entree + status (present / retard)
      Fin des cours   → generate_absents() pour les élèves sans enregistrement
    """
    STATUS_PRESENT = "present"
    STATUS_RETARD = "retard"
    STATUS_ABSENT = "absent"
    STATUS_SORTI = "sorti"
    STATUS_SORTIE_PRECOCE = "sortie_precoce"
    STATUS_EXCUSE = "excuse"

    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_RETARD, "En retard"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_EXCUSE, "Excuse / Justifie"),
    ]

    EXCUSE_CHOICES = [
        ("", "— Aucun justificatif —"),
        ("maladie", "Maladie"),
        ("mission", "Mission officielle"),
        ("deuil", "Deuil"),
        ("autorisation", "Autorisation parentale"),
        ("autre", "Autre"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name="daily_attendances",
        verbose_name="Eleve",
    )
    date = models.DateField(verbose_name="Date")
    heure_entree = models.TimeField(null=True, blank=True, verbose_name="Heure d'arrivee")
    heure_sortie = models.TimeField(null=True, blank=True, verbose_name="Champ historique non utilise")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ABSENT,
        verbose_name="Statut",
    )
    camera_entree = models.ForeignKey(
        Camera, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="check_ins", verbose_name="Camera entree",
    )
    camera_sortie = models.ForeignKey(
        Camera, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="check_outs", verbose_name="Champ historique non utilise",
    )
    modified_by = models.CharField(max_length=120, blank=True, default="", verbose_name="Modifie par")
    excuse_reason = models.CharField(
        max_length=50, blank=True, default="",
        choices=EXCUSE_CHOICES, verbose_name="Type justificatif",
    )
    excuse_notes = models.TextField(blank=True, default="", verbose_name="Notes justificatif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("student", "date")]
        ordering = ["-date", "student__full_name"]
        verbose_name = "Presence journaliere"
        verbose_name_plural = "Presences journalieres"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["student", "date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.student.full_name} — {self.date} — {self.get_status_display()}"

    @property
    def status_badge_class(self) -> str:
        return {
            self.STATUS_PRESENT: "badge-green",
            self.STATUS_RETARD: "badge-yellow",
            self.STATUS_ABSENT: "badge-red",
            self.STATUS_SORTI: "badge-muted",
            self.STATUS_SORTIE_PRECOCE: "badge-yellow",
            self.STATUS_EXCUSE: "badge-blue",
        }.get(self.status, "badge-muted")


# ─────────────────────────────────────────────────────────────────────────────
# JOURNAL D'ACTIVITE SYSTEME — Toutes les actions importantes
# ─────────────────────────────────────────────────────────────────────────────

class SystemLog(models.Model):
    """
    Journal centralisé de toutes les actions importantes du système.
    Enregistre : connexions/déconnexions, CRUD étudiant/caméra/utilisateur,
    entraînement IA, changements de configuration, validations de revue, etc.
    Non-modifiable par les utilisateurs.
    """

    # Types d'actions
    ACTION_LOGIN = "login"
    ACTION_LOGOUT = "logout"
    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"
    ACTION_TRAIN = "train"
    ACTION_RECOGNIZE = "recognize"
    ACTION_CONFIG = "config"
    ACTION_CAMERA = "camera"
    ACTION_REVIEW = "review"
    ACTION_EXPORT = "export"
    ACTION_ACCESS = "access"
    ACTION_ERROR = "error"
    ACTION_OTHER = "other"

    ACTION_CHOICES = [
        (ACTION_LOGIN,     "Connexion"),
        (ACTION_LOGOUT,    "Deconnexion"),
        (ACTION_CREATE,    "Creation"),
        (ACTION_UPDATE,    "Modification"),
        (ACTION_DELETE,    "Suppression"),
        (ACTION_TRAIN,     "Entrainement IA"),
        (ACTION_RECOGNIZE, "Reconnaissance"),
        (ACTION_CONFIG,    "Configuration"),
        (ACTION_CAMERA,    "Camera"),
        (ACTION_REVIEW,    "Revue"),
        (ACTION_EXPORT,    "Export"),
        (ACTION_ACCESS,    "Acces"),
        (ACTION_ERROR,     "Erreur"),
        (ACTION_OTHER,     "Autre"),
    ]

    # Types d'objets concernés
    OBJ_STUDENT   = "student"
    OBJ_CAMERA    = "camera"
    OBJ_CLASSE    = "classe"
    OBJ_COURSE    = "course"
    OBJ_SESSION   = "session"
    OBJ_USER      = "user"
    OBJ_CONFIG    = "config"
    OBJ_MODEL     = "model"
    OBJ_ATTENDANCE = "attendance"
    OBJ_REVIEW    = "review"
    OBJ_PHOTO     = "photo"
    OBJ_SYSTEM    = "system"

    OBJ_CHOICES = [
        (OBJ_STUDENT,    "Etudiant"),
        (OBJ_CAMERA,     "Camera"),
        (OBJ_CLASSE,     "Classe"),
        (OBJ_COURSE,     "Cours"),
        (OBJ_SESSION,    "Session"),
        (OBJ_USER,       "Utilisateur"),
        (OBJ_CONFIG,     "Configuration"),
        (OBJ_MODEL,      "Modele IA"),
        (OBJ_ATTENDANCE, "Presence"),
        (OBJ_REVIEW,     "Revue"),
        (OBJ_PHOTO,      "Photo"),
        (OBJ_SYSTEM,     "Systeme"),
    ]

    user        = models.CharField(max_length=150, default="anonyme", verbose_name="Utilisateur")
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES, default=ACTION_OTHER, verbose_name="Action")
    object_type = models.CharField(max_length=20, choices=OBJ_CHOICES, blank=True, default="", verbose_name="Type objet")
    object_id   = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID objet")
    object_repr = models.CharField(max_length=255, blank=True, default="", verbose_name="Description objet")
    details     = models.TextField(blank=True, default="", verbose_name="Details")
    ip_address  = models.CharField(max_length=45, blank=True, default="", verbose_name="Adresse IP")
    success     = models.BooleanField(default=True, verbose_name="Succes")
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="Date/heure")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Journal systeme"
        verbose_name_plural = "Journal systeme"
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["object_type"]),
        ]

    def __str__(self) -> str:
        return f"[{self.get_action_display()}] {self.user} — {self.object_repr} ({self.created_at:%d/%m %H:%M})"

    @property
    def action_icon(self) -> str:
        return {
            self.ACTION_LOGIN:     "🔑",
            self.ACTION_LOGOUT:    "🚪",
            self.ACTION_CREATE:    "➕",
            self.ACTION_UPDATE:    "✏️",
            self.ACTION_DELETE:    "🗑️",
            self.ACTION_TRAIN:     "🤖",
            self.ACTION_RECOGNIZE: "👁️",
            self.ACTION_CONFIG:    "⚙️",
            self.ACTION_CAMERA:    "📷",
            self.ACTION_REVIEW:    "🔍",
            self.ACTION_EXPORT:    "📤",
            self.ACTION_ERROR:     "❌",
        }.get(self.action, "📋")

    @property
    def action_badge(self) -> str:
        return {
            self.ACTION_LOGIN:  "badge-green",
            self.ACTION_LOGOUT: "badge-muted",
            self.ACTION_CREATE: "badge-blue",
            self.ACTION_UPDATE: "badge-yellow",
            self.ACTION_DELETE: "badge-red",
            self.ACTION_TRAIN:  "badge-purple" if hasattr(self, "badge-purple") else "badge-blue",
            self.ACTION_ERROR:  "badge-red",
        }.get(self.action, "badge-muted")


# ─────────────────────────────────────────────────────────────────────────────
# HISTORIQUE D'ENTRAINEMENT — Chaque session d'entraînement du modèle IA
# ─────────────────────────────────────────────────────────────────────────────

class TrainingHistory(models.Model):
    """
    Enregistre chaque entraînement du modèle de reconnaissance faciale.
    Permet de suivre l'évolution du modèle dans le temps.
    """
    triggered_by     = models.CharField(max_length=150, default="system", verbose_name="Declenche par")
    started_at       = models.DateTimeField(auto_now_add=True, verbose_name="Debut")
    completed_at     = models.DateTimeField(null=True, blank=True, verbose_name="Fin")
    duration_seconds = models.FloatField(default=0.0, verbose_name="Duree (sec)")
    nb_students      = models.PositiveIntegerField(default=0, verbose_name="Etudiants traites")
    nb_photos        = models.PositiveIntegerField(default=0, verbose_name="Photos utilisees")
    nb_skipped_blurry = models.PositiveIntegerField(default=0, verbose_name="Photos floues ignorees")
    success          = models.BooleanField(default=True, verbose_name="Succes")
    error_message    = models.TextField(blank=True, default="", verbose_name="Message d'erreur")

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Historique entrainement"
        verbose_name_plural = "Historique entrainements"

    def __str__(self) -> str:
        status = "OK" if self.success else "ERREUR"
        return f"Entrainement {self.started_at:%d/%m/%Y %H:%M} — {status} — {self.nb_students} etud. / {self.nb_photos} photos"

    @property
    def duration_display(self) -> str:
        if self.duration_seconds < 60:
            return f"{self.duration_seconds:.1f}s"
        return f"{self.duration_seconds / 60:.1f} min"


# ─────────────────────────────────────────────────────────────────────────────
# PROFIL UTILISATEUR — Rôles (Admin / Enseignant / Secrétariat)
# ─────────────────────────────────────────────────────────────────────────────

AuthUser = get_user_model()


class UserProfile(models.Model):
    ROLE_ADMIN        = "admin"
    ROLE_ENSEIGNANT   = "enseignant"
    ROLE_SECRETARIAT  = "secretariat"

    ROLE_CHOICES = [
        (ROLE_ADMIN,       "Administrateur"),
        (ROLE_ENSEIGNANT,  "Enseignant"),
        (ROLE_SECRETARIAT, "Secrétariat"),
    ]

    user = models.OneToOneField(
        AuthUser, on_delete=models.CASCADE,
        related_name="profile", verbose_name="Utilisateur",
    )
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES,
        default=ROLE_SECRETARIAT, verbose_name="Rôle",
    )

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    @property
    def is_enseignant(self) -> bool:
        return self.role == self.ROLE_ENSEIGNANT

    @property
    def is_secretariat(self) -> bool:
        return self.role == self.ROLE_SECRETARIAT

    @property
    def role_badge(self) -> str:
        return {
            self.ROLE_ADMIN:       "badge-red",
            self.ROLE_ENSEIGNANT:  "badge-blue",
            self.ROLE_SECRETARIAT: "badge-yellow",
        }.get(self.role, "badge-muted")

    def can_manage_students(self) -> bool:
        return self.role in [self.ROLE_ADMIN, self.ROLE_SECRETARIAT]

    def can_train_model(self) -> bool:
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    def can_manage_system(self) -> bool:
        return self.role == self.ROLE_ADMIN or self.user.is_superuser

    def can_view_attendance(self) -> bool:
        return True

    def can_edit_attendance(self) -> bool:
        return self.role in [self.ROLE_ADMIN, self.ROLE_SECRETARIAT]


def get_user_profile(user) -> "UserProfile | None":
    """Retourne le profil de l'utilisateur, ou None si pas de profil."""
    try:
        return user.profile
    except Exception:
        return None
