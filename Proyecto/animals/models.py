from django.db import models
from batches.models import Batch

class Animal(models.Model):
    SEXO_CHOICES = [
        ("M", "Macho"),
        ("F", "Hembra"),
    ]
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código/Identificación",
        blank=True,
        null=True
    )
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
        verbose_name="Raza",
        blank=True,
        null=True
    )
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name="Sexo"
    )
    fecha_de_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento"
    )

    def __str__(self) -> str:
        if self.codigo:
            return f"{self.codigo} - {self.especie}"
        return f"{self.especie}"

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animales"
        ordering = ["-fecha_de_nacimiento"]
