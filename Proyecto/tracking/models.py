from django.db import models

from animals.models import Animal


class Peso(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="registros_peso")
    fecha = models.DateTimeField()
    peso = models.DecimalField(max_digits=8, decimal_places=2)
    notas = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Registro de peso"
        verbose_name_plural = "Registros de peso"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.animal} - {self.peso} kg ({self.fecha:%Y-%m-%d})"


class Produccion(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="registros_produccion")
    fecha = models.DateTimeField()
    tipo = models.CharField(max_length=30)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Registro de producción"
        verbose_name_plural = "Registros de producción"
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.animal} - {self.tipo}: {self.cantidad}"
