from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Batch


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["nombre", "direccion", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "bios-input",
                "placeholder": _("Ej: Lote Norte")
            }),
            "direccion": forms.TextInput(attrs={
                "class": "bios-input",
                "placeholder": _("Ej: Finca El Paraíso, Km 5")
            }),
            "imagen": forms.FileInput(attrs={
                "class": "bios-input",
                "accept": "image/*"
            })
        }
        labels = {
            "nombre": _("Nombre del lote"),
            "direccion": _("Dirección"),
            "imagen": _("Imagen del lote")
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre")
        if not nombre:
            return nombre

        nombre = nombre.strip()

        if len(nombre) < 3:
            raise forms.ValidationError(_("El nombre debe tener al menos 3 caracteres."))

        return nombre
