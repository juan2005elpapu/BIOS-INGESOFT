from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, CreateView
from .models import Animal
from batches.models import Batch
from .forms import AnimalForm

class AnimalListView(ListView):
    model = Animal
    template_name = "animals/animal_list.html"
    context_object_name = "animals"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q")
        qs = Animal.objects.select_related("batch").order_by("-fecha_de_nacimiento")
        if query:
            return qs.filter(especie__icontains=query) | qs.filter(raza__icontains=query)
        return qs

class AnimalCreateView(CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = "animals/animal_form.html"

    def form_valid(self, form):
        animal = form.save()
        return redirect(reverse("animals:list"))

# Puedes agregar las rutas en urls.py:
# path('animals/', AnimalListView.as_view(), name='list')
# path('animals/add/', AnimalCreateView.as_view(), name='add')
