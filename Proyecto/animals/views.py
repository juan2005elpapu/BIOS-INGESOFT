from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from batches.models import Batch

from .forms import AnimalForm
from .models import Animal


class AnimalListView(LoginRequiredMixin, ListView):
    model = Animal
    template_name = "animals/animal_list.html"
    context_object_name = "animals"
    paginate_by = 12

    def get_queryset(self):
        user_batches = Batch.objects.by_user(self.request.user)
        queryset = Animal.objects.filter(batch__in=user_batches).select_related("batch")

        search_query = self.request.GET.get("search", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(codigo__icontains=search_query) |
                Q(especie__icontains=search_query) |
                Q(raza__icontains=search_query)
            )

        batch_filter = self.request.GET.get("batch", "").strip()
        if batch_filter:
            queryset = queryset.filter(batch_id=batch_filter)

        sex_filter = self.request.GET.get("sex", "").strip()
        if sex_filter:
            queryset = queryset.filter(sexo=sex_filter)

        return queryset.order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["selected_batch"] = self.request.GET.get("batch", "")
        context["selected_sex"] = self.request.GET.get("sex", "")
        context["user_batches"] = Batch.objects.by_user(self.request.user)

        for animal in context["animals"]:
            if animal.fecha_de_nacimiento:
                age = (date.today() - animal.fecha_de_nacimiento).days
                years = age // 365
                months = (age % 365) // 30
                if years > 0:
                    animal.edad_display = f"{years} año{'s' if years != 1 else ''}"
                elif months > 0:
                    animal.edad_display = f"{months} mes{'es' if months != 1 else ''}"
                else:
                    animal.edad_display = f"{age} día{'s' if age != 1 else ''}"
            else:
                animal.edad_display = "N/A"

        return context


class AnimalCreateView(LoginRequiredMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = "animals/animal_form.html"
    success_url = reverse_lazy("animals:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Animal agregado exitosamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al agregar el animal. Verifica los datos")
        return super().form_invalid(form)


class AnimalUpdateView(LoginRequiredMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = "animals/animal_form.html"
    success_url = reverse_lazy("animals:list")

    def get_queryset(self):
        user_batches = Batch.objects.by_user(self.request.user)
        return Animal.objects.filter(batch__in=user_batches)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Animal actualizado exitosamente")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar el animal. Verifica los datos")
        return super().form_invalid(form)


class AnimalDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user_batches = Batch.objects.by_user(request.user)
        animal = get_object_or_404(Animal, pk=pk, batch__in=user_batches)
        codigo = animal.codigo
        animal.delete()
        messages.success(request, f'Animal "{codigo}" eliminado exitosamente')
        return redirect("animals:list")
