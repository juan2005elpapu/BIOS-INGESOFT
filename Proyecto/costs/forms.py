from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from animals.models import Animal
from batches.models import Batch

from .models import Cost


class CostForm(forms.ModelForm):
    class Meta:
        model = Cost
        fields = ["batch", "animal", "tipo", "concepto", "monto", "fecha", "notas"]
        widgets = {
            "batch": forms.Select(attrs={"class": "bios-select"}),
            "animal": forms.Select(attrs={"class": "bios-select"}),
            "tipo": forms.Select(attrs={"class": "bios-select"}),
            "concepto": forms.TextInput(attrs={"class": "bios-input", "placeholder": "Ej: Alimento balanceado"}),
            "monto": forms.NumberInput(attrs={"class": "bios-input", "step": "0.01", "min": "0"}),
            "fecha": forms.DateInput(attrs={"class": "bios-input", "type": "date"}),
            "notas": forms.Textarea(attrs={"class": "bios-input", "rows": 3, "placeholder": "Detalle opcional"}),
        }
        labels = {
            "batch": "Lote",
            "animal": "Animal",
            "tipo": "Tipo de costo",
            "concepto": "Concepto",
            "monto": "Monto",
            "fecha": "Fecha",
            "notas": "Notas",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        batch_queryset = Batch.objects.by_user(self.user) if self.user else Batch.objects.none()
        self.fields["batch"].queryset = batch_queryset

        animal_queryset = Animal.objects.filter(batch__usuario=self.user) if self.user else Animal.objects.none()
        self.fields["animal"].queryset = animal_queryset.select_related("batch")
        self.fields["animal"].required = False
        self.fields["animal"].empty_label = "Costo general"

    def clean_concepto(self) -> str:
        concepto = (self.cleaned_data.get("concepto") or "").strip()
        if not concepto:
            raise ValidationError("El concepto es obligatorio.")
        return concepto

    def clean_monto(self):
        monto = self.cleaned_data.get("monto")
        if monto is None or monto <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")
        return monto

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")
        if fecha and fecha > date.today():
            raise ValidationError("La fecha no puede ser futura.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        batch = cleaned_data.get("batch")
        animal = cleaned_data.get("animal")

        if self.user and batch and batch.usuario_id != self.user.id:
            raise ValidationError("No puedes registrar costos en este lote.")

        if animal and batch and animal.batch_id != batch.id:
            raise ValidationError("El animal seleccionado no pertenece al lote.")

        return cleaned_data
