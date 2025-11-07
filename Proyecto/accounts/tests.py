from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import EmailAuthenticationForm, SignUpForm

User = get_user_model()


class UserModelTests(TestCase):
    def test_user_creation_with_email(self):
        user = User.objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="testpass123"
        )
        
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_user_string_representation(self):
        user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="pass123"
        )
        
        self.assertEqual(str(user), "user@example.com")


class EmailAuthenticationFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="correctpass"
        )

    def test_valid_login(self):
        form = EmailAuthenticationForm(data={
            "email": "test@example.com",
            "password": "correctpass"
        })
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_case_insensitive_email(self):
        form = EmailAuthenticationForm(data={
            "email": "TEST@EXAMPLE.COM",
            "password": "correctpass"
        })
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_invalid_email(self):
        form = EmailAuthenticationForm(data={
            "email": "nonexistent@example.com",
            "password": "somepass"
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("Correo o contraseña no válidos.", form.non_field_errors())

    def test_invalid_password(self):
        form = EmailAuthenticationForm(data={
            "email": "test@example.com",
            "password": "wrongpass"
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("Correo o contraseña no válidos.", form.non_field_errors())

    def test_empty_fields(self):
        form = EmailAuthenticationForm(data={
            "email": "",
            "password": ""
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("password", form.errors)


class SignUpFormTests(TestCase):
    def test_valid_signup(self):
        form = SignUpForm(data={
            "email": "newuser@example.com",
            "password1": "securepass123",
            "password2": "securepass123"
        })
        
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("securepass123"))

    def test_duplicate_email(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="pass123"
        )
        
        form = SignUpForm(data={
            "email": "existing@example.com",
            "password1": "newpass123",
            "password2": "newpass123"
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("Este correo ya está registrado.", form.errors["email"])

    def test_case_insensitive_duplicate_email(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="pass123"
        )
        
        form = SignUpForm(data={
            "email": "EXISTING@EXAMPLE.COM",
            "password1": "newpass123",
            "password2": "newpass123"
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("Este correo ya está registrado.", form.errors["email"])

    def test_password_mismatch(self):
        form = SignUpForm(data={
            "email": "user@example.com",
            "password1": "password123",
            "password2": "different123"
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("Las contraseñas no coinciden.", form.non_field_errors())

    def test_empty_password(self):
        form = SignUpForm(data={
            "email": "user@example.com",
            "password1": "",
            "password2": ""
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)
        self.assertIn("password2", form.errors)


class LoginViewTests(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123"
        )

    def test_login_page_loads(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_successful_login(self):
        response = self.client.post(self.url, {
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        self.assertRedirects(response, reverse("dashboard:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_redirect_to_next(self):
        next_url = reverse("dashboard:home")
        response = self.client.post(f"{self.url}?next={next_url}", {
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        self.assertRedirects(response, next_url)

    def test_failed_login(self):
        response = self.client.post(self.url, {
            "email": "test@example.com",
            "password": "wrongpass"
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class SignUpViewTests(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_signup_page_loads(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_successful_signup(self):
        response = self.client.post(self.url, {
            "email": "newuser@example.com",
            "password1": "securepass123",
            "password2": "securepass123"
        })
        
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_signup_duplicate_email(self):
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="pass123"
        )
        
        response = self.client.post(self.url, {
            "email": "existing@example.com",
            "password1": "newpass123",
            "password2": "newpass123"
        })
        
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertIn("Este correo ya está registrado.", form.errors["email"])


class LogoutViewTests(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        self.user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="testpass123"
        )

    def test_logout_redirects_to_login(self):
        self.client.login(username="test@example.com", password="testpass123")
        response = self.client.post(self.url)
        
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
