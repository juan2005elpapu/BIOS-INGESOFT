from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import EmailAuthenticationForm, SignUpForm


class LoginView(FormView):
    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        return next_url or super().get_success_url()


class SignUpView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
