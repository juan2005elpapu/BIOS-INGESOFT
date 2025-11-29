from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardLotesView.as_view(), name="home"),
    path("lotes/", views.DashboardLotesView.as_view(), name="lotes"),
    path("tracking/", views.DashboardTrackingView.as_view(), name="tracking"),
    path("costos/", views.DashboardCostosView.as_view(), name="costos"),
]
