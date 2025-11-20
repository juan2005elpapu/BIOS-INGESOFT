from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, QuerySet, Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from animals.models import Animal
from batches.models import Batch

from .forms import PesoForm, ProduccionForm
from .models import Peso, Produccion


class AnimalOwnerQuerysetMixin(LoginRequiredMixin):
    select_related_fields: tuple[str, ...] = ("animal", "animal__batch")

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        return queryset.filter(
            animal__batch__usuario=self.request.user
        ).select_related(*self.select_related_fields)

    def get_user_animals(self) -> QuerySet[Animal]:
        return (
            Animal.objects.filter(batch__usuario=self.request.user)
            .select_related("batch")
            .order_by("codigo", "especie")
        )

    def get_user_batches(self) -> QuerySet[Batch]:
        return (
            Batch.objects.filter(usuario=self.request.user, is_active=True)
            .order_by("nombre")
        )


class TrackingListView(AnimalOwnerQuerysetMixin, ListView):
    paginate_by = 12

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def build_filter_context(self, filters: Dict[str, str]) -> Dict[str, Any]:
        animals = list(self.get_user_animals())
        selected_batch = filters.get("batch")
        filtered_animals = (
            [animal for animal in animals if str(animal.batch_id) == selected_batch]
            if selected_batch
            else []
        )
        return {
            "batches": list(self.get_user_batches()),
            "animals": filtered_animals,
            "animals_data": [
                {
                    "id": animal.id,
                    "batch": animal.batch_id,
                    "batch_name": animal.batch.nombre,
                    "label": f"{animal.codigo or animal.especie} · {animal.batch.nombre}",
                }
                for animal in animals
            ],
        }


class TrackingFormViewMixin(AnimalOwnerQuerysetMixin):
    list_url_name: str = ""
    success_message: str = ""
    action_label: str = "Guardar"
    title: str = ""
    subtitle: str = ""

    def get_form_kwargs(self) -> Dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos marcados en rojo.")
        return super().form_invalid(form)

    def get_success_url(self):
        if not self.list_url_name:
            raise ValueError("Debes configurar list_url_name en la vista.")
        return reverse_lazy(self.list_url_name)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["action_label"] = self.action_label
        context["title"] = self.title
        context["subtitle"] = self.subtitle
        context["cancel_url"] = self.get_success_url()
        return context


class TrackingDeleteViewMixin(AnimalOwnerQuerysetMixin):
    list_url_name: str = ""
    success_message: str = ""
    entity_label: str = ""

    def get_success_url(self):
        if not self.list_url_name:
            raise ValueError("Debes configurar list_url_name en la vista.")
        return reverse_lazy(self.list_url_name)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entity_label"] = self.entity_label
        context["cancel_url"] = self.get_success_url()
        return context


class PesoListView(TrackingListView):
    model = Peso
    template_name = "tracking/peso_list.html"
    context_object_name = "pesos"
    ordering = ("-fecha",)

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.GET.get("batch")
        if batch_id:
            queryset = queryset.filter(animal__batch_id=batch_id)
        animal_id = self.request.GET.get("animal")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        start = self._parse_date(self.request.GET.get("start"))
        if start:
            queryset = queryset.filter(fecha__date__gte=start)
        end = self._parse_date(self.request.GET.get("end"))
        if end:
            queryset = queryset.filter(fecha__date__lte=end)
        return queryset.order_by("-fecha")

    def get_context_data(self, **kwargs: Any):
        full_queryset = self.object_list
        context = super().get_context_data(**kwargs)
        filters = {
            "batch": self.request.GET.get("batch", ""),
            "animal": self.request.GET.get("animal", ""),
            "start": self.request.GET.get("start", ""),
            "end": self.request.GET.get("end", ""),
        }
        context.update(self.build_filter_context(filters))
        context["filters"] = filters
        context["filters_query"] = urlencode({k: v for k, v in filters.items() if v})
        context["stats"] = {
            "total": full_queryset.count(),
            "avg": full_queryset.aggregate(avg=Avg("peso"))["avg"],
            "latest": full_queryset.first(),
        }
        return context


class ProduccionListView(TrackingListView):
    model = Produccion
    template_name = "tracking/produccion_list.html"
    context_object_name = "producciones"
    ordering = ("-fecha",)

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.GET.get("batch")
        if batch_id:
            queryset = queryset.filter(animal__batch_id=batch_id)
        animal_id = self.request.GET.get("animal")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        tipo = (self.request.GET.get("tipo") or "").strip()
        if tipo:
            queryset = queryset.filter(tipo__icontains=tipo)
        start = self._parse_date(self.request.GET.get("start"))
        if start:
            queryset = queryset.filter(fecha__date__gte=start)
        end = self._parse_date(self.request.GET.get("end"))
        if end:
            queryset = queryset.filter(fecha__date__lte=end)
        return queryset.order_by("-fecha")

    def get_context_data(self, **kwargs: Any):
        full_queryset = self.object_list
        context = super().get_context_data(**kwargs)
        filters = {
            "batch": self.request.GET.get("batch", ""),
            "animal": self.request.GET.get("animal", ""),
            "tipo": self.request.GET.get("tipo", ""),
            "start": self.request.GET.get("start", ""),
            "end": self.request.GET.get("end", ""),
        }
        context.update(self.build_filter_context(filters))
        context["filters"] = filters
        context["filters_query"] = urlencode({k: v for k, v in filters.items() if v})
        context["stats"] = {
            "total": full_queryset.count(),
            "sum": full_queryset.aggregate(total=Sum("cantidad"))["total"],
            "latest": full_queryset.first(),
        }
        return context


class PesoCreateView(TrackingFormViewMixin, CreateView):
    model = Peso
    form_class = PesoForm
    template_name = "tracking/registro_form.html"
    list_url_name = "tracking:peso-list"
    success_message = "Registro de peso creado correctamente."
    title = "Registrar peso"
    subtitle = "Captura nuevos datos de peso para tus animales."
    action_label = "Guardar registro"


class PesoUpdateView(TrackingFormViewMixin, UpdateView):
    model = Peso
    form_class = PesoForm
    template_name = "tracking/registro_form.html"
    list_url_name = "tracking:peso-list"
    success_message = "Registro de peso actualizado."
    title = "Editar registro de peso"
    subtitle = "Actualiza la información del registro seleccionado."
    action_label = "Actualizar registro"


class ProduccionCreateView(TrackingFormViewMixin, CreateView):
    model = Produccion
    form_class = ProduccionForm
    template_name = "tracking/registro_form.html"
    list_url_name = "tracking:produccion-list"
    success_message = "Registro de producción creado correctamente."
    title = "Registrar producción"
    subtitle = "Registra nueva producción asociada a tus animales."
    action_label = "Guardar registro"


class ProduccionUpdateView(TrackingFormViewMixin, UpdateView):
    model = Produccion
    form_class = ProduccionForm
    template_name = "tracking/registro_form.html"
    list_url_name = "tracking:produccion-list"
    success_message = "Registro de producción actualizado."
    title = "Editar registro de producción"
    subtitle = "Actualiza la información del registro seleccionado."
    action_label = "Actualizar registro"


class PesoDeleteView(TrackingDeleteViewMixin, DeleteView):
    model = Peso
    template_name = "tracking/registro_confirm_delete.html"
    context_object_name = "registro"
    list_url_name = "tracking:peso-list"
    success_message = "Registro de peso eliminado."
    entity_label = "registro de peso"


class ProduccionDeleteView(TrackingDeleteViewMixin, DeleteView):
    model = Produccion
    template_name = "tracking/registro_confirm_delete.html"
    context_object_name = "registro"
    list_url_name = "tracking:produccion-list"
    success_message = "Registro de producción eliminado."
    entity_label = "registro de producción"
