from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Correo", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean(self) -> dict:
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if not email or not password:
            return cleaned_data

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            raise forms.ValidationError("Correo o contraseña no válidos.")

        authenticated = authenticate(username=user.username, password=password)
        if not authenticated:
            raise forms.ValidationError("Correo o contraseña no válidos.")

        self._user = authenticated
        return cleaned_data

    def get_user(self):
        return getattr(self, "_user", None)


class SignUpForm(forms.Form):
    email = forms.EmailField(label="Correo", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_email(self) -> str:
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email

    def clean(self) -> dict:
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get("password1")
        pwd2 = cleaned_data.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        return User.objects.create_user(username=email, email=email, password=password)