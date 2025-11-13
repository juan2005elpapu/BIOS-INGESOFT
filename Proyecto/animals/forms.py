from django import forms
from .models import Animal

class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ["batch", "especie", "raza", "sexo", "fecha_de_nacimiento"]
        widgets = {
            "fecha_de_nacimiento": forms.DateInput(attrs={"type": "date", "class": "bios-input"}),
            "sexo": forms.Select(choices=[("Male", "Male"), ("Female", "Female")], attrs={"class": "bios-select"}),
        }