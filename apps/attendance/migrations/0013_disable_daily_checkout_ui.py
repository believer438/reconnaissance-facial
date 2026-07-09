# Generated manually to keep model state aligned with the school attendance flow.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0012_alter_systemconfig_seuil_confiance_haute_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="camera",
            name="zone_type",
            field=models.CharField(
                choices=[
                    ("check_in", "Entree ecole (CHECK-IN)"),
                    ("monitoring", "Surveillance (monitoring)"),
                ],
                default="monitoring",
                help_text="CHECK-IN = enregistre l'arrivee des eleves. MONITORING = surveillance sans presence.",
                max_length=12,
                verbose_name="Zone",
            ),
        ),
        migrations.AlterField(
            model_name="schooldayconfig",
            name="heure_sortie_precoce",
            field=models.TimeField(default="15:00", verbose_name="Champ historique non utilise"),
        ),
        migrations.AlterField(
            model_name="dailyattendance",
            name="status",
            field=models.CharField(
                choices=[
                    ("present", "Present"),
                    ("retard", "En retard"),
                    ("absent", "Absent"),
                    ("excuse", "Excuse / Justifie"),
                ],
                default="absent",
                max_length=20,
                verbose_name="Statut",
            ),
        ),
        migrations.AlterField(
            model_name="dailyattendance",
            name="heure_sortie",
            field=models.TimeField(blank=True, null=True, verbose_name="Champ historique non utilise"),
        ),
        migrations.AlterField(
            model_name="dailyattendance",
            name="camera_sortie",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="check_outs",
                to="attendance.camera",
                verbose_name="Champ historique non utilise",
            ),
        ),
    ]
