from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import LoginView, SignUpView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("logout/", LogoutView.as_view(next_page="accounts:login"), name="logout"),
]