from django.urls import path

from . import views

app_name = "costs"

urlpatterns = [
    path("", views.CostListView.as_view(), name="list"),
    path("add/", views.CostCreateView.as_view(), name="add"),
    path("<int:pk>/edit/", views.CostUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.CostDeleteView.as_view(), name="delete"),
]
