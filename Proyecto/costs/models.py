from __future__ import annotations

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from animals.models import Animal
from batches.models import Batch


class CostQuerySet(models.QuerySet):
    def for_user(self, user) -> "CostQuerySet":
        if not user or not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(batch__usuario=user)

    def with_relations(self) -> "CostQuerySet":
        return self.select_related("batch", "animal")


class Cost(models.Model):
    class CostType(models.TextChoices):
        FEED = ("feed", _("Alimentación"))
        HEALTH = ("health", _("Salud"))
        MAINTENANCE = ("maintenance", _("Mantenimiento"))
        LABOR = ("labor", _("Mano de obra"))
        OTHER = ("other", _("Otro"))

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="costos",
        verbose_name=_("Lote"),
    )
    animal = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        related_name="costos",
        blank=True,
        null=True,
        verbose_name=_("Animal"),
    )
    tipo = models.CharField(
        max_length=20,
        choices=CostType.choices,
        verbose_name=_("Tipo de costo"),
    )
    concepto = models.CharField(
        max_length=120,
        verbose_name=_("Concepto"),
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Monto"),
    )
    fecha = models.DateField(verbose_name=_("Fecha"))
    notas = models.TextField(
        verbose_name=_("Notas"),
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CostQuerySet.as_manager()

    class Meta:
        verbose_name = _("Costo")
        verbose_name_plural = _("Costos")
        ordering = ["-fecha", "-created_at"]
        indexes = [
            models.Index(fields=["batch", "fecha"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["-created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(monto__gt=0),
                name="cost_monto_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.concepto} - {self.batch.nombre}"
