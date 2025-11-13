from django.db import models
from batches.models import Batch

class Animal(models.Model):
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="animals",
        verbose_name="Lote"
    )
    especie = models.CharField(
        max_length=50,
        verbose_name="Especie"
    )
    raza = models.CharField(
        max_length=30,
        verbose_name="Raza"
    )
    sexo = models.CharField(
        max_length=10,
        verbose_name="Sexo"
    )
    fecha_de_nacimiento = models.DateTimeField(
        verbose_name="Fecha de nacimiento"
    )

    def __str__(self) -> str:
        return f"{self.especie} - {self.raza} ({self.sexo})"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animales"
        ordering = ["fecha_de_nacimiento"]
