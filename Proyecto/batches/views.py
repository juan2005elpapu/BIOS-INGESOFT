from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import BatchForm
from .models import Batch


class BatchListView(LoginRequiredMixin, ListView):
    model = Batch
    template_name = "batches/batch_list.html"
    context_object_name = "batches"
    paginate_by = 10

    def get_queryset(self):
        queryset = Batch.objects.by_user(self.request.user)

        search = self.request.GET.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(direccion__icontains=search)
            )

        order_by = self.request.GET.get("order", "-created_at")
        valid_orders = ["nombre", "-nombre", "created_at", "-created_at", "direccion", "-direccion"]
        if order_by in valid_orders:
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["current_order"] = self.request.GET.get("order", "-created_at")
        return context


class BatchCreateView(LoginRequiredMixin, CreateView):
    model = Batch
    form_class = BatchForm
    template_name = "batches/batch_form.html"
    success_url = reverse_lazy("batches:list")

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, _("Lote creado exitosamente."))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Error al crear el lote. Verifica los datos."))
        return super().form_invalid(form)


class BatchUpdateView(LoginRequiredMixin, UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = "batches/batch_form.html"
    success_url = reverse_lazy("batches:list")

    def get_queryset(self):
        return Batch.objects.by_user(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _("Lote actualizado exitosamente."))
        return super().form_valid(form)


class BatchDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        batch = get_object_or_404(Batch, pk=pk, usuario=request.user)
        nombre_batch = batch.nombre
        batch.delete()
        messages.success(request, _('Lote "{}" eliminado exitosamente.').format(nombre_batch))
        return redirect("batches:list")
