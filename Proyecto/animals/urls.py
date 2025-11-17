from django.urls import path

from . import views

app_name = "animals"

urlpatterns = [
    path("", views.AnimalListView.as_view(), name="list"),
    path("add/", views.AnimalCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.AnimalUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.AnimalDeleteView.as_view(), name="delete"),
]
