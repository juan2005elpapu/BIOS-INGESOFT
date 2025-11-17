from django import forms

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

        # Agregar placeholder al select de sexo
        self.fields["sexo"].empty_label = "Selecciona el sexo"

        # Hacer raza opcional
        self.fields["raza"].required = False

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo", "")
        codigo = codigo.strip().upper()

        # Verificar si existe otro animal con el mismo código (excepto el actual en edición)
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
