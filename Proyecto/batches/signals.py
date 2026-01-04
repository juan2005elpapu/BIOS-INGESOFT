import logging

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Batch

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Batch)
def delete_old_image_on_update(sender, instance: Batch, **kwargs):
    """Elimina la imagen antigua cuando se actualiza a una nueva."""
    if not instance.pk:
        return

    try:
        old_instance = Batch.objects.get(pk=instance.pk)
    except Batch.DoesNotExist:
        return

    if not old_instance.imagen:
        return

    # Si no hay imagen nueva o es diferente a la anterior, borrar la vieja
    if not instance.imagen or old_instance.imagen.name != instance.imagen.name:
        try:
            old_instance.imagen.delete(save=False)
            logger.info(f"Old image {old_instance.imagen.name} deleted")
        except Exception as e:
            logger.error(f"Error deleting old image: {e}")


@receiver(post_delete, sender=Batch)
def delete_image_on_delete(sender, instance: Batch, **kwargs):
    """Elimina la imagen del storage cuando se borra el lote."""
    if instance.imagen:
        try:
            instance.imagen.delete(save=False)
            logger.info(f"Image {instance.imagen.name} deleted with batch")
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
