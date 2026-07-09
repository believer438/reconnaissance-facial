from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.attendance"
    verbose_name = "Reconnaissance faciale"

    def ready(self):
        from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
        from django.db.models.signals import post_save
        from django.dispatch import receiver

        @receiver(user_logged_in)
        def on_login(sender, request, user, **kwargs):
            try:
                from .models import SystemLog
                ip = _get_ip(request)
                SystemLog.objects.create(
                    user=user.username,
                    action=SystemLog.ACTION_LOGIN,
                    object_type=SystemLog.OBJ_USER,
                    object_repr=user.get_full_name() or user.username,
                    details=f"Connexion reussie — {user.email or 'email non renseigne'}",
                    ip_address=ip,
                    success=True,
                )
            except Exception:
                pass

        @receiver(user_logged_out)
        def on_logout(sender, request, user, **kwargs):
            try:
                from .models import SystemLog
                if not user:
                    return
                ip = _get_ip(request)
                SystemLog.objects.create(
                    user=user.username,
                    action=SystemLog.ACTION_LOGOUT,
                    object_type=SystemLog.OBJ_USER,
                    object_repr=user.get_full_name() or user.username,
                    details="Deconnexion",
                    ip_address=ip,
                    success=True,
                )
            except Exception:
                pass

        @receiver(user_login_failed)
        def on_login_failed(sender, credentials, request, **kwargs):
            try:
                from .models import SystemLog
                ip = _get_ip(request)
                SystemLog.objects.create(
                    user=credentials.get("username", "inconnu"),
                    action=SystemLog.ACTION_LOGIN,
                    object_type=SystemLog.OBJ_USER,
                    object_repr=credentials.get("username", "inconnu"),
                    details="Tentative de connexion echouee — mot de passe incorrect",
                    ip_address=ip,
                    success=False,
                )
            except Exception:
                pass

        # ── Auto-entraînement LBPH dès qu'une nouvelle photo est ajoutée ────────
        from .models import TrainingPhoto

        @receiver(post_save, sender=TrainingPhoto)
        def on_photo_saved(sender, instance, created, **kwargs):
            if not created:
                return
            try:
                from .services.train_state import schedule_auto_retrain
                schedule_auto_retrain(delay_seconds=6)
            except Exception:
                pass


def _get_ip(request) -> str:
    if not request:
        return ""
    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip[:45]
