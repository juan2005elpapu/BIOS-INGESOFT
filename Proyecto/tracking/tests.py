from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from animals.models import Animal
from batches.models import Batch

from .forms import PesoForm, ProduccionForm
from .models import Peso, Produccion

User = get_user_model()


class PesoModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="PESO-001",
            especie="Vaca",
            raza="Holstein",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 15)
        )

    def test_peso_creation_with_all_fields(self):
        fecha = timezone.make_aware(timezone.datetime(2024, 1, 15, 10, 30))
        peso = Peso.objects.create(
            animal=self.animal,
            fecha=fecha,
            peso=Decimal("450.50"),
            notas="Animal en buen estado"
        )

        self.assertEqual(peso.animal, self.animal)
        self.assertEqual(peso.fecha, fecha)
        self.assertEqual(peso.peso, Decimal("450.50"))
        self.assertEqual(peso.notas, "Animal en buen estado")

    def test_peso_creation_minimal_fields(self):
        fecha = timezone.make_aware(timezone.datetime(2024, 1, 15, 10, 30))
        peso = Peso.objects.create(
            animal=self.animal,
            fecha=fecha,
            peso=Decimal("450.50"),
            notas=""
        )

        self.assertEqual(peso.animal, self.animal)
        self.assertEqual(peso.peso, Decimal("450.50"))
        self.assertEqual(peso.notas, "")

    def test_peso_str_representation(self):
        fecha = timezone.make_aware(timezone.datetime(2024, 1, 15, 10, 30))
        peso = Peso.objects.create(
            animal=self.animal,
            fecha=fecha,
            peso=Decimal("450.50"),
            notas=""
        )

        expected = f"{self.animal} - 450.50 kg (2024-01-15)"
        self.assertEqual(str(peso), expected)

    def test_peso_ordering_by_fecha_descending(self):
        peso1 = Peso.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 10, 8, 0)),
            peso=Decimal("440.00")
        )
        peso2 = Peso.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 20, 8, 0)),
            peso=Decimal("450.00")
        )
        peso3 = Peso.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 15, 8, 0)),
            peso=Decimal("445.00")
        )

        ordered = list(Peso.objects.all())

        self.assertEqual(ordered[0], peso2)
        self.assertEqual(ordered[1], peso3)
        self.assertEqual(ordered[2], peso1)

    def test_peso_decimal_precision(self):
        peso = Peso.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            peso=Decimal("123.45")
        )

        self.assertEqual(peso.peso, Decimal("123.45"))

    def test_peso_related_name(self):
        Peso.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            peso=Decimal("400.00")
        )
        Peso.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            peso=Decimal("410.00")
        )

        self.assertEqual(self.animal.registros_peso.count(), 2)

    def test_peso_cascade_delete(self):
        peso = Peso.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            peso=Decimal("450.00")
        )

        animal_id = self.animal.id
        self.animal.delete()

        self.assertFalse(Peso.objects.filter(animal_id=animal_id).exists())


class ProduccionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="PROD-001",
            especie="Vaca",
            raza="Holstein",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 15)
        )

    def test_produccion_creation_with_all_fields(self):
        fecha = timezone.make_aware(timezone.datetime(2024, 1, 15, 8, 0))
        produccion = Produccion.objects.create(
            animal=self.animal,
            fecha=fecha,
            tipo="Leche",
            cantidad=Decimal("25.50")
        )

        self.assertEqual(produccion.animal, self.animal)
        self.assertEqual(produccion.fecha, fecha)
        self.assertEqual(produccion.tipo, "Leche")
        self.assertEqual(produccion.cantidad, Decimal("25.50"))

    def test_produccion_str_representation(self):
        produccion = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            tipo="Huevos",
            cantidad=Decimal("12.00")
        )

        expected = f"{self.animal} - Huevos: 12.00"
        self.assertEqual(str(produccion), expected)

    def test_produccion_ordering_by_fecha_descending(self):
        prod1 = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 10, 6, 0)),
            tipo="Leche",
            cantidad=Decimal("20.00")
        )
        prod2 = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 20, 6, 0)),
            tipo="Leche",
            cantidad=Decimal("25.00")
        )
        prod3 = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 15, 6, 0)),
            tipo="Leche",
            cantidad=Decimal("22.00")
        )

        ordered = list(Produccion.objects.all())

        self.assertEqual(ordered[0], prod2)
        self.assertEqual(ordered[1], prod3)
        self.assertEqual(ordered[2], prod1)

    def test_produccion_decimal_precision(self):
        produccion = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            tipo="Lana",
            cantidad=Decimal("5.75")
        )

        self.assertEqual(produccion.cantidad, Decimal("5.75"))

    def test_produccion_related_name(self):
        Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            tipo="Leche",
            cantidad=Decimal("20.00")
        )
        Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            tipo="Leche",
            cantidad=Decimal("22.00")
        )

        self.assertEqual(self.animal.registros_produccion.count(), 2)

    def test_produccion_cascade_delete(self):
        produccion = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            tipo="Leche",
            cantidad=Decimal("20.00")
        )

        animal_id = self.animal.id
        self.animal.delete()

        self.assertFalse(Produccion.objects.filter(animal_id=animal_id).exists())

    def test_produccion_tipo_max_length(self):
        tipo_valido = "A" * 30
        produccion = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.now(),
            tipo=tipo_valido,
            cantidad=Decimal("10.00")
        )

        self.assertEqual(len(produccion.tipo), 30)


class PesoFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        self.other_batch = Batch.objects.create(
            nombre="Otro Lote",
            usuario=self.other_user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="FORM-001",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 15)
        )
        self.other_animal = Animal.objects.create(
            batch=self.other_batch,
            codigo="OTHER-001",
            especie="Cerdo",
            sexo="M",
            fecha_de_nacimiento=date(2021, 3, 10)
        )

    def test_peso_form_valid_data(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "450.50",
            "notas": "Registro de prueba"
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())

    def test_peso_form_saves_correctly(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "450.50",
            "notas": "Registro de prueba"
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())
        peso = form.save()
        self.assertEqual(peso.peso, Decimal("450.50"))
        self.assertEqual(peso.notas, "Registro de prueba")

    def test_peso_form_invalid_peso_zero(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "0",
            "notas": ""
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("peso", form.errors)

    def test_peso_form_invalid_peso_negative(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "-10.50",
            "notas": ""
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("peso", form.errors)

    def test_peso_form_animal_queryset_filtered_by_user(self):
        form = PesoForm(user=self.user)

        animal_ids = list(form.fields["animal"].queryset.values_list("id", flat=True))
        self.assertIn(self.animal.id, animal_ids)
        self.assertNotIn(self.other_animal.id, animal_ids)

    def test_peso_form_unauthorized_animal(self):
        form_data = {
            "animal": self.other_animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "450.50",
            "notas": ""
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("animal", form.errors)

    def test_peso_form_without_user(self):
        form = PesoForm(user=None)

        self.assertEqual(form.fields["animal"].queryset.count(), 0)

    def test_peso_form_missing_required_fields(self):
        form_data = {
            "animal": self.animal.id,
            "notas": ""
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("fecha", form.errors)
        self.assertIn("peso", form.errors)

    def test_peso_form_notas_optional(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "450.50",
            "notas": ""
        }
        form = PesoForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())


class ProduccionFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        self.other_batch = Batch.objects.create(
            nombre="Otro Lote",
            usuario=self.other_user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="PROD-001",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 15)
        )
        self.other_animal = Animal.objects.create(
            batch=self.other_batch,
            codigo="OTHER-001",
            especie="Cerdo",
            sexo="M",
            fecha_de_nacimiento=date(2021, 3, 10)
        )

    def test_produccion_form_valid_data(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "Leche",
            "cantidad": "25.50"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())

    def test_produccion_form_saves_correctly(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "Leche",
            "cantidad": "25.50"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())
        produccion = form.save()
        self.assertEqual(produccion.tipo, "Leche")
        self.assertEqual(produccion.cantidad, Decimal("25.50"))

    def test_produccion_form_invalid_cantidad_zero(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "Leche",
            "cantidad": "0"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("cantidad", form.errors)

    def test_produccion_form_invalid_cantidad_negative(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "Leche",
            "cantidad": "-5.00"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("cantidad", form.errors)

    def test_produccion_form_empty_tipo(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "",
            "cantidad": "25.50"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("tipo", form.errors)

    def test_produccion_form_tipo_whitespace_only(self):
        form_data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "   ",
            "cantidad": "25.50"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("tipo", form.errors)

    def test_produccion_form_animal_queryset_filtered_by_user(self):
        form = ProduccionForm(user=self.user)

        animal_ids = list(form.fields["animal"].queryset.values_list("id", flat=True))
        self.assertIn(self.animal.id, animal_ids)
        self.assertNotIn(self.other_animal.id, animal_ids)

    def test_produccion_form_unauthorized_animal(self):
        form_data = {
            "animal": self.other_animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "Leche",
            "cantidad": "25.50"
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("animal", form.errors)

    def test_produccion_form_without_user(self):
        form = ProduccionForm(user=None)

        self.assertEqual(form.fields["animal"].queryset.count(), 0)

    def test_produccion_form_missing_required_fields(self):
        form_data = {
            "animal": self.animal.id
        }
        form = ProduccionForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("fecha", form.errors)
        self.assertIn("tipo", form.errors)
        self.assertIn("cantidad", form.errors)


class PesoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        self.other_batch = Batch.objects.create(
            nombre="Otro Lote",
            usuario=self.other_user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="VIEW-001",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 15)
        )
        self.other_animal = Animal.objects.create(
            batch=self.other_batch,
            codigo="OTHER-001",
            especie="Cerdo",
            sexo="M",
            fecha_de_nacimiento=date(2021, 3, 10)
        )
        self.peso = Peso.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 15, 10, 30)),
            peso=Decimal("450.00"),
            notas="Registro inicial"
        )

    def test_peso_list_requires_login(self):
        response = self.client.get(reverse("tracking:peso-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_peso_list_shows_user_registros(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:peso-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "450.00")
        self.assertTemplateUsed(response, "tracking/peso_list.html")

    def test_peso_list_filters_by_user_animals(self):
        Peso.objects.create(
            animal=self.other_animal,
            fecha=timezone.now(),
            peso=Decimal("300.00")
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:peso-list"))

        self.assertContains(response, "450.00")
        self.assertNotContains(response, "300.00")

    def test_peso_create_requires_login(self):
        response = self.client.get(reverse("tracking:peso-create"))

        self.assertEqual(response.status_code, 302)

    def test_peso_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:peso-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/registro_form.html")
        self.assertIsInstance(response.context["form"], PesoForm)

    def test_peso_create_view_post_valid(self):
        self.client.force_login(self.user)

        data = {
            "animal": self.animal.id,
            "fecha": "2024-01-20T14:30",
            "peso": "460.00",
            "notas": "Nuevo registro"
        }
        response = self.client.post(reverse("tracking:peso-create"), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Peso.objects.filter(peso=Decimal("460.00")).exists())

    def test_peso_create_view_post_invalid(self):
        self.client.force_login(self.user)

        data = {
            "animal": self.animal.id,
            "fecha": "2024-01-20T14:30",
            "peso": "0"
        }
        response = self.client.post(reverse("tracking:peso-create"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Peso.objects.filter(peso=Decimal("0")).exists())

    def test_peso_update_requires_login(self):
        response = self.client.get(
            reverse("tracking:peso-update", args=[self.peso.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_peso_update_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:peso-update", args=[self.peso.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/registro_form.html")
        self.assertEqual(response.context["object"], self.peso)

    def test_peso_update_view_post_valid(self):
        self.client.force_login(self.user)

        data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T10:30",
            "peso": "455.00",
            "notas": "Registro actualizado"
        }
        response = self.client.post(
            reverse("tracking:peso-update", args=[self.peso.pk]),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.peso.refresh_from_db()
        self.assertEqual(self.peso.peso, Decimal("455.00"))
        self.assertEqual(self.peso.notas, "Registro actualizado")

    def test_peso_update_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("tracking:peso-update", args=[self.peso.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_peso_delete_requires_login(self):
        response = self.client.post(
            reverse("tracking:peso-delete", args=[self.peso.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_peso_delete_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("tracking:peso-delete", args=[self.peso.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Peso.objects.filter(pk=self.peso.pk).exists())

    def test_peso_delete_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("tracking:peso-delete", args=[self.peso.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Peso.objects.filter(pk=self.peso.pk).exists())


class ProduccionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="otherpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        self.other_batch = Batch.objects.create(
            nombre="Otro Lote",
            usuario=self.other_user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="PROD-001",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 15)
        )
        self.other_animal = Animal.objects.create(
            batch=self.other_batch,
            codigo="OTHER-001",
            especie="Cerdo",
            sexo="M",
            fecha_de_nacimiento=date(2021, 3, 10)
        )
        self.produccion = Produccion.objects.create(
            animal=self.animal,
            fecha=timezone.make_aware(timezone.datetime(2024, 1, 15, 8, 0)),
            tipo="Leche",
            cantidad=Decimal("25.00")
        )

    def test_produccion_list_requires_login(self):
        response = self.client.get(reverse("tracking:produccion-list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_produccion_list_shows_user_registros(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:produccion-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leche")
        self.assertContains(response, "25.00")
        self.assertTemplateUsed(response, "tracking/produccion_list.html")

    def test_produccion_list_filters_by_user_animals(self):
        Produccion.objects.create(
            animal=self.other_animal,
            fecha=timezone.now(),
            tipo="Carne",
            cantidad=Decimal("50.00")
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:produccion-list"))

        self.assertContains(response, "Leche")
        self.assertNotContains(response, "Carne")

    def test_produccion_create_requires_login(self):
        response = self.client.get(reverse("tracking:produccion-create"))

        self.assertEqual(response.status_code, 302)

    def test_produccion_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("tracking:produccion-create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/registro_form.html")
        self.assertIsInstance(response.context["form"], ProduccionForm)

    def test_produccion_create_view_post_valid(self):
        self.client.force_login(self.user)

        data = {
            "animal": self.animal.id,
            "fecha": "2024-01-20T08:00",
            "tipo": "Leche",
            "cantidad": "30.00"
        }
        response = self.client.post(reverse("tracking:produccion-create"), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Produccion.objects.filter(
                tipo="Leche",
                cantidad=Decimal("30.00")
            ).exists()
        )

    def test_produccion_create_view_post_invalid(self):
        self.client.force_login(self.user)

        data = {
            "animal": self.animal.id,
            "fecha": "2024-01-20T08:00",
            "tipo": "",
            "cantidad": "30.00"
        }
        response = self.client.post(reverse("tracking:produccion-create"), data)

        self.assertEqual(response.status_code, 200)

    def test_produccion_update_requires_login(self):
        response = self.client.get(
            reverse("tracking:produccion-update", args=[self.produccion.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_produccion_update_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("tracking:produccion-update", args=[self.produccion.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tracking/registro_form.html")
        self.assertEqual(response.context["object"], self.produccion)

    def test_produccion_update_view_post_valid(self):
        self.client.force_login(self.user)

        data = {
            "animal": self.animal.id,
            "fecha": "2024-01-15T08:00",
            "tipo": "Leche",
            "cantidad": "28.00"
        }
        response = self.client.post(
            reverse("tracking:produccion-update", args=[self.produccion.pk]),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.produccion.refresh_from_db()
        self.assertEqual(self.produccion.cantidad, Decimal("28.00"))

    def test_produccion_update_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("tracking:produccion-update", args=[self.produccion.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_produccion_delete_requires_login(self):
        response = self.client.post(
            reverse("tracking:produccion-delete", args=[self.produccion.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_produccion_delete_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("tracking:produccion-delete", args=[self.produccion.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Produccion.objects.filter(pk=self.produccion.pk).exists()
        )

    def test_produccion_delete_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("tracking:produccion-delete", args=[self.produccion.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Produccion.objects.filter(pk=self.produccion.pk).exists()
        )
