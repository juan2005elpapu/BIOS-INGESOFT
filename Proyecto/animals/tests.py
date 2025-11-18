from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from batches.models import Batch

from .forms import AnimalForm
from .models import Animal

User = get_user_model()


class AnimalModelTests(TestCase):
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

    def test_animal_creation_with_all_fields(self):
        animal = Animal.objects.create(
            batch=self.batch,
            codigo="TEST-001",
            especie="Vaca",
            raza="Holstein",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 15)
        )

        self.assertEqual(animal.codigo, "TEST-001")
        self.assertEqual(animal.especie, "Vaca")
        self.assertEqual(animal.raza, "Holstein")
        self.assertEqual(animal.sexo, "M")
        self.assertEqual(animal.fecha_de_nacimiento, date(2020, 1, 15))
        self.assertEqual(animal.batch, self.batch)

    def test_animal_creation_minimal_fields(self):
        animal = Animal.objects.create(
            batch=self.batch,
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2021, 5, 20)
        )

        self.assertEqual(animal.especie, "Cerdo")
        self.assertEqual(animal.sexo, "F")
        self.assertIsNone(animal.codigo)
        self.assertTrue(animal.raza is None or animal.raza == "")

    def test_animal_str_representation_with_codigo(self):
        animal = Animal.objects.create(
            batch=self.batch,
            codigo="TEST-001",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 15)
        )

        self.assertEqual(str(animal), "TEST-001 - Vaca")

    def test_animal_str_representation_without_codigo(self):
        animal = Animal.objects.create(
            batch=self.batch,
            especie="Caballo",
            sexo="M",
            fecha_de_nacimiento=date(2019, 3, 10)
        )

        self.assertEqual(str(animal), "Caballo")

    def test_animal_sexo_macho(self):
        animal = Animal.objects.create(
            batch=self.batch,
            codigo="SEXO-M",
            especie="Toro",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )

        self.assertEqual(animal.sexo, "M")
        self.assertEqual(animal.get_sexo_display(), "Macho")

    def test_animal_sexo_hembra(self):
        animal = Animal.objects.create(
            batch=self.batch,
            codigo="SEXO-F",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 1)
        )

        self.assertEqual(animal.sexo, "F")
        self.assertEqual(animal.get_sexo_display(), "Hembra")

    def test_animal_codigo_max_length(self):
        codigo_valido = "A" * 50
        animal = Animal.objects.create(
            batch=self.batch,
            codigo=codigo_valido,
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )

        self.assertEqual(len(animal.codigo), 50)

    def test_animals_ordered_by_birthdate_descending(self):
        animal1 = Animal.objects.create(
            batch=self.batch,
            codigo="ORD-001",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        animal2 = Animal.objects.create(
            batch=self.batch,
            codigo="ORD-002",
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2022, 6, 15)
        )
        animal3 = Animal.objects.create(
            batch=self.batch,
            codigo="ORD-003",
            especie="Caballo",
            sexo="M",
            fecha_de_nacimiento=date(2019, 3, 10)
        )

        ordered = list(Animal.objects.all())

        self.assertEqual(ordered[0], animal2)
        self.assertEqual(ordered[1], animal1)
        self.assertEqual(ordered[2], animal3)

    def test_animal_age_calculation(self):
        birth_date = date.today() - timedelta(days=365 * 3 + 10)
        animal = Animal.objects.create(
            batch=self.batch,
            codigo="AGE-TEST",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=birth_date
        )

        age_days = (date.today() - animal.fecha_de_nacimiento).days

        self.assertGreaterEqual(age_days, 365 * 3)

    def test_animal_newborn_today(self):
        animal = Animal.objects.create(
            batch=self.batch,
            codigo="NEWBORN",
            especie="Ternero",
            sexo="M",
            fecha_de_nacimiento=date.today()
        )

        age_days = (date.today() - animal.fecha_de_nacimiento).days

        self.assertEqual(age_days, 0)


class AnimalFormTests(TestCase):
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

    def test_animal_form_valid_data_complete(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "FORM-001",
            "especie": "Vaca",
            "raza": "Holstein",
            "sexo": "M",
            "fecha_de_nacimiento": "2020-01-15"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())

    def test_animal_form_valid_data_minimal(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "",
            "especie": "Cerdo",
            "sexo": "F",
            "fecha_de_nacimiento": "2021-05-20"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertTrue(form.is_valid())

    def test_animal_form_missing_especie(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "",
            "sexo": "M",
            "fecha_de_nacimiento": "2020-01-01"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("especie", form.errors)

    def test_animal_form_missing_sexo(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "",
            "especie": "Vaca",
            "fecha_de_nacimiento": "2020-01-01"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("sexo", form.errors)

    def test_animal_form_missing_fecha_nacimiento(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "",
            "especie": "Vaca",
            "sexo": "M"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("fecha_de_nacimiento", form.errors)

    def test_animal_form_missing_batch(self):
        form_data = {
            "codigo": "",
            "especie": "Vaca",
            "sexo": "M",
            "fecha_de_nacimiento": "2020-01-01"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("batch", form.errors)

    def test_animal_form_invalid_sexo(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "",
            "especie": "Vaca",
            "sexo": "X",
            "fecha_de_nacimiento": "2020-01-01"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("sexo", form.errors)

    def test_animal_form_invalid_date_format(self):
        form_data = {
            "batch": self.batch.id,
            "codigo": "",
            "especie": "Vaca",
            "sexo": "M",
            "fecha_de_nacimiento": "01-15-2020"
        }
        form = AnimalForm(data=form_data, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("fecha_de_nacimiento", form.errors)


class AnimalViewTests(TestCase):
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
            password="testpass123"
        )
        self.batch = Batch.objects.create(
            nombre="Lote Test",
            direccion="Calle Test 123",
            usuario=self.user
        )
        self.other_batch = Batch.objects.create(
            nombre="Lote Otro",
            usuario=self.other_user
        )
        self.animal = Animal.objects.create(
            batch=self.batch,
            codigo="TEST-001",
            especie="Vaca",
            raza="Holstein",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 15)
        )

    def test_animal_list_requires_login(self):
        response = self.client.get(reverse("animals:list"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_animal_list_shows_user_animals(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animals:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST-001")
        self.assertTemplateUsed(response, "animals/animal_list.html")

    def test_animal_list_filters_by_user_batches(self):
        Animal.objects.create(
            batch=self.other_batch,
            codigo="OTHER-001",
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2021, 1, 1)
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("animals:list"))

        self.assertContains(response, "TEST-001")
        self.assertNotContains(response, "OTHER-001")

    def test_animal_list_search_by_codigo(self):
        Animal.objects.create(
            batch=self.batch,
            codigo="SEARCH-001",
            especie="Caballo",
            sexo="M",
            fecha_de_nacimiento=date(2019, 1, 1)
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("animals:list") + "?search=SEARCH")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SEARCH-001")

    def test_animal_list_search_by_especie(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animals:list") + "?search=Vaca")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST-001")

    def test_animal_create_requires_login(self):
        response = self.client.get(reverse("animals:add"))

        self.assertEqual(response.status_code, 302)

    def test_animal_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("animals:add"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "animals/animal_form.html")
        self.assertIsInstance(response.context["form"], AnimalForm)

    def test_animal_create_view_post_valid(self):
        self.client.force_login(self.user)

        data = {
            "batch": self.batch.id,
            "codigo": "CREATE-001",
            "especie": "Vaca",
            "raza": "Jersey",
            "sexo": "F",
            "fecha_de_nacimiento": "2021-06-15"
        }
        response = self.client.post(reverse("animals:add"), data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Animal.objects.filter(codigo="CREATE-001").exists())

        new_animal = Animal.objects.get(codigo="CREATE-001")
        self.assertEqual(new_animal.batch, self.batch)
        self.assertEqual(new_animal.especie, "Vaca")

    def test_animal_create_view_post_invalid(self):
        self.client.force_login(self.user)

        data = {
            "batch": self.batch.id,
            "especie": "Vaca"
        }
        response = self.client.post(reverse("animals:add"), data)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Animal.objects.filter(especie="Vaca", sexo="").exists())

    def test_animal_update_requires_login(self):
        response = self.client.get(
            reverse("animals:edit", args=[self.animal.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_animal_update_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("animals:edit", args=[self.animal.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "animals/animal_form.html")
        self.assertEqual(response.context["object"], self.animal)

    def test_animal_update_view_post_valid(self):
        self.client.force_login(self.user)

        data = {
            "batch": self.batch.id,
            "codigo": "UPDATED-001",
            "especie": "Toro",
            "raza": "Angus",
            "sexo": "M",
            "fecha_de_nacimiento": "2020-01-15"
        }
        response = self.client.post(
            reverse("animals:edit", args=[self.animal.pk]),
            data
        )

        self.assertEqual(response.status_code, 302)
        self.animal.refresh_from_db()
        self.assertEqual(self.animal.codigo, "UPDATED-001")
        self.assertEqual(self.animal.especie, "Toro")
        self.assertEqual(self.animal.raza, "Angus")

    def test_animal_update_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("animals:edit", args=[self.animal.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_animal_delete_requires_login(self):
        response = self.client.post(
            reverse("animals:delete", args=[self.animal.pk])
        )

        self.assertEqual(response.status_code, 302)

    def test_animal_delete_view_post(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("animals:delete", args=[self.animal.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Animal.objects.filter(pk=self.animal.pk).exists())

    def test_animal_delete_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.post(
            reverse("animals:delete", args=[self.animal.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Animal.objects.filter(pk=self.animal.pk).exists())

    def test_animal_list_empty_for_new_user(self):
        new_user = User.objects.create_user(
            username="newuser@example.com",
            email="newuser@example.com",
            password="newpass123"
        )

        self.client.force_login(new_user)
        response = self.client.get(reverse("animals:list"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "TEST-001")

    def test_animal_filter_by_batch(self):
        batch2 = Batch.objects.create(
            nombre="Lote Test 2",
            usuario=self.user
        )
        animal2 = Animal.objects.create(
            batch=batch2,
            codigo="BATCH2-001",
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2021, 1, 1)
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("animals:list") + f"?batch={self.batch.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST-001")
