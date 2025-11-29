from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .services import DashboardStatsService


class DashboardBaseView(LoginRequiredMixin, TemplateView):
    """Clase base para las vistas del dashboard."""

    template_name = "dashboard/home.html"
    active_tab: str = ""

    def get_service(self) -> DashboardStatsService:
        return DashboardStatsService(self.request.user)

    def parse_date(self, date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["active_tab"] = self.active_tab
        return context


class DashboardLotesView(DashboardBaseView):
    """Vista para la pestaña de Lotes y Animales."""

    active_tab = "lotes"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        service = self.get_service()

        filters = {
            "lote_id": self.request.GET.get("lote", ""),
            "especie": self.request.GET.get("especie", ""),
            "orden": self.request.GET.get("orden", ""),
        }

        stats = service.get_lotes_animales_stats(
            lote_id=filters["lote_id"] or None,
            especie=filters["especie"] or None,
            orden=filters["orden"] or None,
        )

        context.update({
            "filters": filters,
            "kpis": stats["kpis"],
            "charts_json": json.dumps(stats["charts"]),
            "lotes_disponibles": stats["lotes_disponibles"],
        })
        return context


class DashboardTrackingView(DashboardBaseView):
    """Vista para la pestaña de Tracking."""

    active_tab = "tracking"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        service = self.get_service()

        filters = {
            "lote_id": self.request.GET.get("lote", ""),
            "animal_id": self.request.GET.get("animal", ""),
            "tipo_produccion": self.request.GET.get("tipo", ""),
            "fecha_inicio": self.request.GET.get("start", ""),
            "fecha_fin": self.request.GET.get("end", ""),
        }

        stats = service.get_tracking_stats(
            lote_id=filters["lote_id"] or None,
            animal_id=filters["animal_id"] or None,
            tipo_produccion=filters["tipo_produccion"] or None,
            fecha_inicio=self.parse_date(filters["fecha_inicio"]),
            fecha_fin=self.parse_date(filters["fecha_fin"]),
        )

        context.update({
            "filters": filters,
            "kpis": stats["kpis"],
            "charts_json": json.dumps(stats["charts"]),
            "lotes_disponibles": stats["lotes_disponibles"],
            "animales_disponibles": stats["animales_disponibles"],
        })
        return context


class DashboardCostosView(DashboardBaseView):
    """Vista para la pestaña de Costos."""

    active_tab = "costos"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        service = self.get_service()

        filters = {
            "lote_id": self.request.GET.get("lote", ""),
            "tipo_costo": self.request.GET.get("tipo", ""),
            "fecha_inicio": self.request.GET.get("start", ""),
            "fecha_fin": self.request.GET.get("end", ""),
        }

        stats = service.get_costos_stats(
            lote_id=filters["lote_id"] or None,
            tipo_costo=filters["tipo_costo"] or None,
            fecha_inicio=self.parse_date(filters["fecha_inicio"]),
            fecha_fin=self.parse_date(filters["fecha_fin"]),
        )

        context.update({
            "filters": filters,
            "kpis": stats["kpis"],
            "charts_json": json.dumps(stats["charts"]),
            "lotes_disponibles": stats["lotes_disponibles"],
            "tipos_disponibles": stats["tipos_disponibles"],
        })
        return context
