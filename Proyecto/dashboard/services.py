from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth

from animals.models import Animal
from batches.models import Batch
from costs.models import Cost
from tracking.models import Peso, Produccion

User = get_user_model()


@dataclass
class ChartData:
    labels: list[str]
    values: list[float | int]

    def to_dict(self) -> dict[str, Any]:
        return {"labels": self.labels, "values": self.values}


class DashboardStatsService:
    def __init__(self, user: User) -> None:
        self.user = user

    def get_lotes_animales_stats(
        self,
        lote_id: str | None = None,
        especie: str | None = None,
        orden: str | None = None,
    ) -> dict[str, Any]:
        batches = Batch.objects.by_user(self.user)
        animals = Animal.objects.filter(batch__usuario=self.user)

        if lote_id:
            animals = animals.filter(batch_id=lote_id)

        if especie:
            animals = animals.filter(especie__icontains=especie)

        total_lotes = batches.count()
        total_animales = animals.count()

        animales_por_lote = list(
            animals.values("batch__nombre")
            .annotate(total=Count("id"))
            .order_by("-total" if orden == "desc" else "batch__nombre")
        )

        animales_por_especie = list(
            animals.values("especie")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        animales_por_sexo = list(
            animals.values("sexo")
            .annotate(total=Count("id"))
            .order_by("-total")
        )

        chart_por_lote = ChartData(
            labels=[item["batch__nombre"] or "Sin lote" for item in animales_por_lote],
            values=[item["total"] for item in animales_por_lote],
        )

        chart_por_especie = ChartData(
            labels=[item["especie"] or "Sin especie" for item in animales_por_especie],
            values=[item["total"] for item in animales_por_especie],
        )

        chart_por_sexo = ChartData(
            labels=[self._get_sexo_label(item["sexo"]) for item in animales_por_sexo],
            values=[item["total"] for item in animales_por_sexo],
        )

        return {
            "kpis": {
                "total_lotes": total_lotes,
                "total_animales": total_animales,
                "promedio_por_lote": round(total_animales / total_lotes, 1) if total_lotes else 0,
            },
            "charts": {
                "por_lote": chart_por_lote.to_dict(),
                "por_especie": chart_por_especie.to_dict(),
                "por_sexo": chart_por_sexo.to_dict(),
            },
            "lotes_disponibles": list(batches.values("id", "nombre")),
        }

    def get_tracking_stats(
        self,
        lote_id: str | None = None,
        animal_id: str | None = None,
        tipo_produccion: str | None = None,
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
    ) -> dict[str, Any]:
        pesos = Peso.objects.filter(animal__batch__usuario=self.user)
        producciones = Produccion.objects.filter(animal__batch__usuario=self.user)

        if lote_id:
            pesos = pesos.filter(animal__batch_id=lote_id)
            producciones = producciones.filter(animal__batch_id=lote_id)

        if animal_id:
            pesos = pesos.filter(animal_id=animal_id)
            producciones = producciones.filter(animal_id=animal_id)

        if tipo_produccion:
            producciones = producciones.filter(tipo__icontains=tipo_produccion)

        if fecha_inicio:
            pesos = pesos.filter(fecha__gte=fecha_inicio)
            producciones = producciones.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            pesos = pesos.filter(fecha__lte=fecha_fin)
            producciones = producciones.filter(fecha__lte=fecha_fin)

        total_pesos = pesos.count()
        total_producciones = producciones.count()
        peso_promedio = pesos.aggregate(avg=Avg("peso"))["avg"] or 0
        produccion_total = producciones.aggregate(sum=Sum("cantidad"))["sum"] or 0

        pesos_mensuales = list(
            pesos.annotate(mes=TruncMonth("fecha"))
            .values("mes")
            .annotate(promedio=Avg("peso"))
            .order_by("mes")
        )

        producciones_mensuales = list(
            producciones.annotate(mes=TruncMonth("fecha"))
            .values("mes")
            .annotate(total=Sum("cantidad"))
            .order_by("mes")
        )

        chart_pesos = ChartData(
            labels=[item["mes"].strftime("%b %Y") if item["mes"] else "" for item in pesos_mensuales],
            values=[round(float(item["promedio"]), 2) for item in pesos_mensuales],
        )

        chart_producciones = ChartData(
            labels=[item["mes"].strftime("%b %Y") if item["mes"] else "" for item in producciones_mensuales],
            values=[round(float(item["total"]), 2) for item in producciones_mensuales],
        )

        return {
            "kpis": {
                "total_pesos": total_pesos,
                "total_producciones": total_producciones,
                "peso_promedio": round(float(peso_promedio), 2),
                "produccion_total": round(float(produccion_total), 2),
            },
            "charts": {
                "pesos_mensuales": chart_pesos.to_dict(),
                "producciones_mensuales": chart_producciones.to_dict(),
            },
            "lotes_disponibles": list(Batch.objects.by_user(self.user).values("id", "nombre")),
            "animales_disponibles": list(
                Animal.objects.filter(batch__usuario=self.user)
                .values("id", "codigo", "especie", "batch__nombre")
            ),
        }

    def get_costos_stats(
        self,
        lote_id: str | None = None,
        tipo_costo: str | None = None,
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
    ) -> dict[str, Any]:
        costos = Cost.objects.for_user(self.user)

        if lote_id:
            costos = costos.filter(batch_id=lote_id)

        if tipo_costo:
            costos = costos.filter(tipo=tipo_costo)

        if fecha_inicio:
            costos = costos.filter(fecha__gte=fecha_inicio)

        if fecha_fin:
            costos = costos.filter(fecha__lte=fecha_fin)

        total_registros = costos.count()
        gasto_total = costos.aggregate(sum=Sum("monto"))["sum"] or 0

        costos_por_tipo = list(
            costos.values("tipo")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        costos_por_lote = list(
            costos.values("batch__nombre")
            .annotate(total=Sum("monto"))
            .order_by("-total")
        )

        costos_mensuales = list(
            costos.annotate(mes=TruncMonth("fecha"))
            .values("mes")
            .annotate(total=Sum("monto"))
            .order_by("mes")
        )

        chart_por_tipo = ChartData(
            labels=[self._get_tipo_costo_label(item["tipo"]) for item in costos_por_tipo],
            values=[round(float(item["total"]), 2) for item in costos_por_tipo],
        )

        chart_por_lote = ChartData(
            labels=[item["batch__nombre"] or "Sin lote" for item in costos_por_lote],
            values=[round(float(item["total"]), 2) for item in costos_por_lote],
        )

        chart_mensual = ChartData(
            labels=[item["mes"].strftime("%b %Y") if item["mes"] else "" for item in costos_mensuales],
            values=[round(float(item["total"]), 2) for item in costos_mensuales],
        )

        return {
            "kpis": {
                "total_registros": total_registros,
                "gasto_total": round(float(gasto_total), 2),
                "promedio_por_registro": round(float(gasto_total) / total_registros, 2) if total_registros else 0,
            },
            "charts": {
                "por_tipo": chart_por_tipo.to_dict(),
                "por_lote": chart_por_lote.to_dict(),
                "mensual": chart_mensual.to_dict(),
            },
            "lotes_disponibles": list(Batch.objects.by_user(self.user).values("id", "nombre")),
            "tipos_disponibles": [(str(value), str(label)) for value, label in Cost.CostType.choices],
        }

    @staticmethod
    def _get_sexo_label(sexo: str | None) -> str:
        labels = {"M": "Macho", "F": "Hembra"}
        return labels.get(sexo, "No especificado")

    @staticmethod
    def _get_tipo_costo_label(tipo: str | None) -> str:
        tipo_map = {str(k): str(v) for k, v in Cost.CostType.choices}
        return tipo_map.get(tipo, str(tipo) if tipo else "Otro")