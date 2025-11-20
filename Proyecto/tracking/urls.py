from django.urls import path

from . import views

app_name = "tracking"

urlpatterns = [
    path("pesos/", views.PesoListView.as_view(), name="peso-list"),
    path("pesos/nuevo/", views.PesoCreateView.as_view(), name="peso-create"),
    path("pesos/<int:pk>/editar/", views.PesoUpdateView.as_view(), name="peso-update"),
    path("pesos/<int:pk>/eliminar/", views.PesoDeleteView.as_view(), name="peso-delete"),
    path("producciones/", views.ProduccionListView.as_view(), name="produccion-list"),
    path("producciones/nuevo/", views.ProduccionCreateView.as_view(), name="produccion-create"),
    path("producciones/<int:pk>/editar/", views.ProduccionUpdateView.as_view(), name="produccion-update"),
    path("producciones/<int:pk>/eliminar/", views.ProduccionDeleteView.as_view(), name="produccion-delete"),
]