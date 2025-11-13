from django.urls import path
from .views import AnimalListView, AnimalCreateView

app_name = "animals"

urlpatterns = [
    path("", AnimalListView.as_view(), name="list"),
    path("add/", AnimalCreateView.as_view(), name="add"),
]