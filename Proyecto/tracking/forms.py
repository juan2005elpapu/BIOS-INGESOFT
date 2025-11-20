from __future__ import annotations

from decimal import Decimal
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from animals.models import Animal
from .models import Peso, Produccion


class BaseTrackingForm(forms.ModelForm):
    animal = forms.ModelChoiceField(
        queryset=Animal.objects.none(),
        label="Animal",
        widget=forms.Select(attrs={"class": "bios-select"})
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["animal"].queryset = self._get_animal_queryset()
        self._apply_field_styles()

    def _get_animal_queryset(self) -> QuerySet[Animal]:
        if not self.user:
            return Animal.objects.none()
        return (
            Animal.objects.filter(batch__usuario=self.user)
            .select_related("batch")
            .order_by("codigo", "especie")
        )

    def _apply_field_styles(self) -> None:
        for name, field in self.fields.items():
            if name == "animal":
                continue
            if isinstance(field.widget, forms.DateTimeInput):
                field.widget.attrs.setdefault("class", "bios-input")
                field.widget.attrs.setdefault("type", "datetime-local")
                field.widget.attrs.setdefault("step", "60")
                continue
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "bios-select")
                continue
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", "bios-input min-h-[120px]")
                continue
            field.widget.attrs.setdefault("class", "bios-input")

    def clean_animal(self) -> Animal | None:
        animal = self.cleaned_data.get("animal")
        if not self.user or not animal:
            return animal
        if animal.batch.usuario_id != self.user.id:
            raise ValidationError("No puedes registrar información para este animal.")
        return animal


class PesoForm(BaseTrackingForm):
    datetime_format = "%Y-%m-%dT%H:%M"

    class Meta:
        model = Peso
        fields = ["animal", "fecha", "peso", "notas"]
        labels = {
            "fecha": "Fecha de registro",
            "peso": "Peso (kg)",
            "notas": "Notas",
        }
        widgets = {
            "fecha": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "bios-input", "step": "60"},
                format="%Y-%m-%dT%H:%M",
            ),
            "peso": forms.NumberInput(
                attrs={"class": "bios-input", "step": "0.01", "min": "0"}
            ),
            "notas": forms.Textarea(
                attrs={"class": "bios-input", "rows": 3, "placeholder": "Observaciones opcionales"}
            ),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        fecha = self.fields["fecha"]
        fecha.widget.format = self.datetime_format
        existing_formats = list(fecha.input_formats or [])
        fecha.input_formats = [self.datetime_format, *existing_formats]

    def clean_peso(self) -> Decimal:
        peso = self.cleaned_data.get("peso")
        if peso is None or peso <= 0:
            raise ValidationError("El peso debe ser mayor a cero.")
        return peso


class ProduccionForm(BaseTrackingForm):
    datetime_format = "%Y-%m-%dT%H:%M"

    class Meta:
        model = Produccion
        fields = ["animal", "fecha", "tipo", "cantidad"]
        labels = {
            "fecha": "Fecha de registro",
            "tipo": "Tipo de producción",
            "cantidad": "Cantidad",
        }
        widgets = {
            "fecha": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "bios-input", "step": "60"},
                format="%Y-%m-%dT%H:%M",
            ),
            "tipo": forms.TextInput(
                attrs={"class": "bios-input", "placeholder": "Leche, lana, huevos..."}
            ),
            "cantidad": forms.NumberInput(
                attrs={"class": "bios-input", "step": "0.01", "min": "0"}
            ),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        fecha = self.fields["fecha"]
        fecha.widget.format = self.datetime_format
        existing_formats = list(fecha.input_formats or [])
        fecha.input_formats = [self.datetime_format, *existing_formats]

    def clean_tipo(self) -> str:
        tipo = (self.cleaned_data.get("tipo") or "").strip()
        if not tipo:
            raise ValidationError("El tipo de producción es obligatorio.")
        return tipo

    def clean_cantidad(self) -> Decimal:
        cantidad = self.cleaned_data.get("cantidad")
        if cantidad is None or cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a cero.")
        return cantidad