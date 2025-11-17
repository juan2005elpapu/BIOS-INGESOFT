from django.urls import path

from . import views

app_name = "batches"

urlpatterns = [
    path("", views.BatchListView.as_view(), name="list"),
    path("crear/", views.BatchCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.BatchUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", views.BatchDeleteView.as_view(), name="delete"),
]
