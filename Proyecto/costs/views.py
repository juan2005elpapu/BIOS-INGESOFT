from __future__ import annotations

from datetime import datetime, date
from typing import Any
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from animals.models import Animal
from batches.models import Batch

from .forms import CostForm
from .models import Cost


class CostQuerysetMixin(LoginRequiredMixin):
    select_related_fields: tuple[str, ...] = ("batch", "animal")

    def get_queryset(self):
        queryset = Cost.objects.for_user(self.request.user)
        return queryset.select_related(*self.select_related_fields)

    def get_user_batches(self):
        return Batch.objects.by_user(self.request.user).order_by("nombre")

    def get_user_animals(self):
        return (
            Animal.objects.filter(batch__usuario=self.request.user)
            .select_related("batch")
            .order_by("codigo", "especie")
        )


class CostListView(CostQuerysetMixin, ListView):
    model = Cost
    template_name = "costs/cost_list.html"
    context_object_name = "costs"
    paginate_by = 12

    @staticmethod
    def _parse_date(value: str | None) -> date | None:
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def get_queryset(self):
        queryset = super().get_queryset()
        search = (self.request.GET.get("search") or "").strip()
        if search:
            queryset = queryset.filter(Q(concepto__icontains=search) | Q(notas__icontains=search))

        batch_id = self.request.GET.get("batch")
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)

        animal_id = self.request.GET.get("animal")
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)

        cost_type = (self.request.GET.get("tipo") or "").strip()
        if cost_type:
            queryset = queryset.filter(tipo=cost_type)

        start_date = self._parse_date(self.request.GET.get("start"))
        if start_date:
            queryset = queryset.filter(fecha__gte=start_date)

        end_date = self._parse_date(self.request.GET.get("end"))
        if end_date:
            queryset = queryset.filter(fecha__lte=end_date)

        return queryset.order_by("-fecha", "-id")

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        filters = {
            "search": self.request.GET.get("search", ""),
            "batch": self.request.GET.get("batch", ""),
            "animal": self.request.GET.get("animal", ""),
            "tipo": self.request.GET.get("tipo", ""),
            "start": self.request.GET.get("start", ""),
            "end": self.request.GET.get("end", ""),
        }
        stats_queryset = self.object_list
        context.update(
            {
                "filters": filters,
                "filters_query": urlencode({k: v for k, v in filters.items() if v}),
                "batches": self.get_user_batches(),
                "animals": self.get_user_animals(),
                "cost_types": Cost.CostType.choices,
                "stats": {
                    "total": stats_queryset.count(),
                    "sum": stats_queryset.aggregate(total=Sum("monto"))["total"],
                },
            }
        )
        return context


class CostFormMixin(CostQuerysetMixin):
    form_class = CostForm
    template_name = "costs/cost_form.html"
    success_url = reverse_lazy("costs:list")
    success_message: str = ""
    title: str = ""
    subtitle: str = ""
    action_label: str = "Guardar"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los campos antes de guardar.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["subtitle"] = self.subtitle
        context["action_label"] = self.action_label
        context["cancel_url"] = self.success_url
        return context


class CostCreateView(CostFormMixin, CreateView):
    model = Cost
    title = "Registrar costo"
    subtitle = "Agrega un nuevo gasto asociado a tus lotes o animales."
    action_label = "Guardar costo"
    success_message = "Costo registrado correctamente."


class CostUpdateView(CostFormMixin, UpdateView):
    model = Cost
    title = "Editar costo"
    subtitle = "Actualiza la información del costo seleccionado."
    action_label = "Actualizar costo"
    success_message = "Costo actualizado correctamente."

    def get_queryset(self):
        return super().get_queryset()


class CostDeleteView(CostQuerysetMixin, View):
    def post(self, request, pk):
        costo = get_object_or_404(self.get_queryset(), pk=pk)
        concepto = costo.concepto
        costo.delete()
        messages.success(request, f'Costo "{concepto}" eliminado.')
        return redirect("costs:list")
