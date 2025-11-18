"""
Tests para el módulo de cuentas (autenticación y registro).
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from accounts.forms import EmailAuthenticationForm, SignUpForm

User = get_user_model()


@pytest.mark.django_db
class TestEmailAuthenticationForm:
    """Tests para validar la autenticación por email."""
    
    def test_valid_login_with_correct_credentials(self, user):
        """
        Caso: Login con credenciales válidas
        Esperado: El formulario debe ser válido y retornar el usuario autenticado.
        Casos límite: Email exacto pero con diferentes mayúsculas.
        """
        # Crear usuario con contraseña conocida
        password = "TestPassword123!"
        test_user = User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password=password
        )
        
        form = EmailAuthenticationForm(data={
            "email": "test@example.com",
            "password": password
        })
        
        assert form.is_valid()
        assert form.get_user() == test_user
    
    def test_login_with_case_insensitive_email(self):
        """
        Caso: Login con email en diferentes casos (mayúsculas/minúsculas)
        Esperado: El login debe funcionar independientemente del caso del email.
        Casos límite: Email con mayúsculas, minúsculas, mixto.
        """
        password = "TestPassword123!"
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password=password
        )
        
        # Probar con mayúsculas
        form = EmailAuthenticationForm(data={
            "email": "TEST@EXAMPLE.COM",
            "password": password
        })
        assert form.is_valid()
        
        # Probar con mixto
        form = EmailAuthenticationForm(data={
            "email": "TeSt@ExAmPlE.cOm",
            "password": password
        })
        assert form.is_valid()
    
    def test_login_with_wrong_password(self):
        """
        Caso: Intento de login con contraseña incorrecta
        Esperado: El formulario debe ser inválido con mensaje de error.
        Casos límite: Contraseña vacía, contraseña incorrecta.
        """
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="CorrectPassword123!"
        )
        
        form = EmailAuthenticationForm(data={
            "email": "test@example.com",
            "password": "WrongPassword123!"
        })
        
        assert not form.is_valid()
        assert "Correo o contraseña no válidos" in str(form.errors)
    
    def test_login_with_nonexistent_email(self):
        """
        Caso: Intento de login con email que no existe
        Esperado: El formulario debe ser inválido.
        Casos límite: Email válido pero no registrado, email vacío.
        """
        form = EmailAuthenticationForm(data={
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        })
        
        assert not form.is_valid()
        assert "Correo o contraseña no válidos" in str(form.errors)
    
    def test_login_with_empty_fields(self):
        """
        Caso: Intento de login con campos vacíos
        Esperado: El formulario debe ser inválido.
        Casos límite: Solo email vacío, solo contraseña vacía, ambos vacíos.
        """
        form = EmailAuthenticationForm(data={
            "email": "",
            "password": ""
        })
        
        assert not form.is_valid()


@pytest.mark.django_db
class TestSignUpForm:
    """Tests para validar el registro de nuevos usuarios."""
    
    def test_successful_signup_with_valid_data(self):
        """
        Caso: Registro exitoso con datos válidos
        Esperado: El usuario debe ser creado correctamente en la BD.
        Casos límite: Email único, contraseñas coinciden.
        """
        form = SignUpForm(data={
            "email": "newuser@example.com",
            "password1": "NewPassword123!",
            "password2": "NewPassword123!"
        })
        
        assert form.is_valid()
        user = form.save()
        
        assert User.objects.filter(email="newuser@example.com").exists()
        assert user.username == "newuser@example.com"
    
    def test_signup_with_duplicate_email(self):
        """
        Caso: Intento de registro con email ya registrado
        Esperado: El formulario debe ser inválido con mensaje de error.
        Casos límite: Email duplicado (mayúsculas/minúsculas), email vacío.
        """
        User.objects.create_user(
            username="existing@example.com",
            email="existing@example.com",
            password="ExistingPassword123!"
        )
        
        form = SignUpForm(data={
            "email": "existing@example.com",
            "password1": "NewPassword123!",
            "password2": "NewPassword123!"
        })
        
        assert not form.is_valid()
        assert "Este correo ya está registrado" in str(form.errors)
    
    def test_signup_with_duplicate_email_case_insensitive(self):
        """
        Caso: Intento de registro con email duplicado en diferentes casos
        Esperado: El registro debe rechazarse (búsqueda case-insensitive).
        Casos límite: Email con mayúsculas cuando existe en minúsculas.
        """
        User.objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="Password123!"
        )
        
        form = SignUpForm(data={
            "email": "TEST@EXAMPLE.COM",
            "password1": "NewPassword123!",
            "password2": "NewPassword123!"
        })
        
        assert not form.is_valid()
    
    def test_signup_with_mismatched_passwords(self):
        """
        Caso: Registro con contraseñas que no coinciden
        Esperado: El formulario debe ser inválido.
        Casos límite: Pequeña diferencia en caracteres, una vacía.
        """
        form = SignUpForm(data={
            "email": "newuser@example.com",
            "password1": "Password123!",
            "password2": "Password124!"
        })
        
        assert not form.is_valid()
        assert "Las contraseñas no coinciden" in str(form.errors)
    
    def test_signup_with_empty_passwords(self):
        """
        Caso: Registro con contraseñas vacías
        Esperado: El formulario debe ser inválido.
        Casos límite: Ambas vacías, solo una vacía.
        """
        form = SignUpForm(data={
            "email": "newuser@example.com",
            "password1": "",
            "password2": ""
        })
        
        assert not form.is_valid()
    
    def test_signup_with_invalid_email_format(self):
        """
        Caso: Registro con formato de email inválido
        Esperado: El formulario debe ser inválido.
        Casos límite: Sin @, sin dominio, caracteres especiales inválidos.
        """
        form = SignUpForm(data={
            "email": "invalid-email",
            "password1": "Password123!",
            "password2": "Password123!"
        })
        
        assert not form.is_valid()