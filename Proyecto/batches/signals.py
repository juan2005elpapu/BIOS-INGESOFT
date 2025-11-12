import logging
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from .models import Batch

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Batch)
def delete_batch_image_on_delete(sender, instance, **kwargs):
    """Elimina la imagen del storage cuando se borra el lote."""
    if not instance.imagen:
        return

    try:
        storage = instance.imagen.storage
        imagen_name = instance.imagen.name
        
        if storage.exists(imagen_name):
            storage.delete(imagen_name)
    except Exception as e:
        logger.error(f"Error al eliminar imagen: {e}")


@receiver(pre_save, sender=Batch)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Elimina la imagen antigua cuando se actualiza a una nueva."""
    if not instance.pk:
        return

    try:
        old_instance = Batch.objects.get(pk=instance.pk)
    except Batch.DoesNotExist:
        return

    if not old_instance.imagen or old_instance.imagen == instance.imagen:
        return

    try:
        storage = old_instance.imagen.storage
        old_imagen_name = old_instance.imagen.name
        
        if storage.exists(old_imagen_name):
            storage.delete(old_imagen_name)
    except Exception as e:
        logger.error(f"Error al eliminar imagen antigua: {e}")