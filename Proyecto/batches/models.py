from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from batches.storage import SupabaseStorage

def get_batch_storage():
    """Retorna SupabaseStorage si está habilitado."""
    if getattr(settings, 'USE_SUPABASE_STORAGE', False):
        return SupabaseStorage()
    return None

class BatchManager(models.Manager):
    def active_batches(self):
        return self.filter(is_active=True)

    def by_user(self, user):
        return self.filter(usuario=user, is_active=True)


class Batch(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario propietario"),
        related_name="lotes"
    )
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
    imagen = models.ImageField(
        upload_to="lotes/",
        storage=get_batch_storage,
        verbose_name=_("Imagen del lote"),
        blank=True,
        null=True
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
            models.Index(fields=["usuario", "nombre"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.nombre}"

    def animal_count(self) -> int:
        return self.animal_set.count()
