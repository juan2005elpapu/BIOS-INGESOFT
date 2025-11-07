from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class BatchManager(models.Manager):
    def active_batches(self):
        return self.filter(is_active=True)
    
    def by_user(self, user):
        return self.filter(usuariolote__id_usuario=user)


class Batch(models.Model):
    nombre = models.CharField(
        max_length=50,
        verbose_name=_("Nombre del lote"),
        help_text=_("Identificador único del lote")
    )
    direccion = models.CharField(
        max_length=50,
        verbose_name=_("Dirección"),
        blank=True,
        help_text=_("Ubicación física del lote")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Activo")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de creación")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última actualización")
    )

    objects = BatchManager()

    class Meta:
        verbose_name = _("Lote")
        verbose_name_plural = _("Lotes")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["nombre"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.nombre

    def animal_count(self) -> int:
        return self.animal_set.count()


class UserBatch(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", _("Propietario")
        MANAGER = "manager", _("Administrador")
        VIEWER = "viewer", _("Visualizador")

    id_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
        related_name="user_batches"
    )
    id_lote = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        verbose_name=_("Lote"),
        related_name="batch_users"
    )
    rol = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.VIEWER,
        verbose_name=_("Rol")
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de asignación")
    )

    class Meta:
        verbose_name = _("Usuario-Lote")
        verbose_name_plural = _("Usuarios-Lotes")
        unique_together = [["id_usuario", "id_lote"]]
        indexes = [
            models.Index(fields=["id_usuario", "id_lote"]),
        ]

    def __str__(self) -> str:
        return f"{self.id_usuario} - {self.id_lote} ({self.get_rol_display()})"

    def is_owner(self) -> bool:
        return self.rol == self.Role.OWNER

    def can_manage(self) -> bool:
        return self.rol in [self.Role.OWNER, self.Role.MANAGER]
