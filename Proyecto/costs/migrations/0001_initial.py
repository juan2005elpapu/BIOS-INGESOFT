from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("batches", "0003_batch_imagen_batch_batches_bat_created_56977f_idx"),
        ("animals", "0003_animal_codigo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Cost",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("tipo", models.CharField(choices=[("feed", "Alimentación"), ("health", "Salud"), ("maintenance", "Mantenimiento"), ("labor", "Mano de obra"), ("other", "Otro")], max_length=20, verbose_name="Tipo de costo")),
                ("concepto", models.CharField(max_length=120, verbose_name="Concepto")),
                ("monto", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Monto")),
                ("fecha", models.DateField(verbose_name="Fecha")),
                ("notas", models.TextField(blank=True, verbose_name="Notas")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "animal",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="costos",
                        to="animals.animal",
                        verbose_name="Animal",
                    ),
                ),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="costos",
                        to="batches.batch",
                        verbose_name="Lote",
                    ),
                ),
            ],
            options={
                "verbose_name": "Costo",
                "verbose_name_plural": "Costos",
                "ordering": ["-fecha", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="cost",
            index=models.Index(fields=["batch", "fecha"], name="costs_cost_batch_i_63c1ee_idx"),
        ),
        migrations.AddIndex(
            model_name="cost",
            index=models.Index(fields=["tipo"], name="costs_cost_tipo_a918f7_idx"),
        ),
        migrations.AddIndex(
            model_name="cost",
            index=models.Index(fields=["-created_at"], name="costs_cost_created_9b76f1_idx"),
        ),
        migrations.AddConstraint(
            model_name="cost",
            constraint=models.CheckConstraint(check=Q(("monto__gt", 0)), name="cost_monto_positive"),
        ),
    ]
