from django import forms
from datetime import date
from django.core.exceptions import ValidationError

from batches.models import Batch

from .models import Animal


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ["codigo", "batch", "especie", "raza", "sexo", "fecha_de_nacimiento"]
        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "bios-input",
                "placeholder": "Ej: A001, BOV-123, etc."
            }),
            "batch": forms.Select(attrs={
                "class": "bios-select"
            }),
            "especie": forms.TextInput(attrs={
                "class": "bios-input",
                "placeholder": "Ej: Bovino, Ovino, Porcino..."
            }),
            "raza": forms.TextInput(attrs={
                "class": "bios-input",
                "placeholder": "Ej: Holstein, Angus..."
            }),
            "sexo": forms.Select(attrs={
                "class": "bios-select"
            }),
            "fecha_de_nacimiento": forms.DateInput(attrs={
                "class": "bios-input",
                "type": "date"
            }),
        }
        labels = {
            "codigo": "Código/Identificación",
            "batch": "Lote",
            "especie": "Especie",
            "raza": "Raza",
            "sexo": "Sexo",
            "fecha_de_nacimiento": "Fecha de Nacimiento",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["batch"].queryset = Batch.objects.by_user(user)

        self.fields["sexo"].empty_label = "Selecciona el sexo"
        self.fields["raza"].required = False
        self.fields["codigo"].required = False

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo", "")
        
        if not codigo:
            return ""
        
        codigo = codigo.strip().upper()
        
        if not codigo:
            return ""

        qs = Animal.objects.filter(codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe un animal con este código.")

        return codigo

    def clean_especie(self):
        especie = self.cleaned_data.get("especie", "")
        return especie.strip()

    def clean_raza(self):
        raza = self.cleaned_data.get("raza", "")
        return raza.strip() if raza else None

    def clean_fecha_de_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_de_nacimiento")
        if fecha and fecha > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser futura.")
        return fecha
