from io import BytesIO
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from PIL import Image

from .models import Batch
from .forms import BatchForm

User = get_user_model()


class BatchModelTests(TestCase):
    def setUp(self):
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

    def test_batch_creation(self):
        batch = Batch.objects.create(
            nombre="Lote Test",
            direccion="Calle Test 123",
            usuario=self.user
        )
        
        self.assertEqual(batch.nombre, "Lote Test")
        self.assertEqual(batch.direccion, "Calle Test 123")
        self.assertEqual(batch.usuario, self.user)
        self.assertTrue(batch.is_active)

    def test_batch_str_representation(self):
        batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user
        )
        
        self.assertEqual(str(batch), "Lote Test")

    def test_batch_manager_by_user(self):
        batch1 = Batch.objects.create(nombre="Lote 1", usuario=self.user)
        batch2 = Batch.objects.create(nombre="Lote 2", usuario=self.user)
        batch3 = Batch.objects.create(nombre="Lote 3", usuario=self.other_user)
        
        user_batches = Batch.objects.by_user(self.user)
        
        self.assertEqual(user_batches.count(), 2)
        self.assertIn(batch1, user_batches)
        self.assertIn(batch2, user_batches)
        self.assertNotIn(batch3, user_batches)

    def test_batch_ordering(self):
        batch1 = Batch.objects.create(nombre="B Lote", usuario=self.user)
        batch2 = Batch.objects.create(nombre="A Lote", usuario=self.user)
        
        batches = Batch.objects.filter(usuario=self.user)
        
        self.assertEqual(batches[0], batch2)
        self.assertEqual(batches[1], batch1)


class BatchFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_valid_form(self):
        form_data = {
            "nombre": "Lote Test",
            "direccion": "Calle Test 123"
        }
        form = BatchForm(data=form_data)
        
        self.assertTrue(form.is_valid())

    def test_form_without_nombre(self):
        form_data = {
            "direccion": "Calle Test 123"
        }
        form = BatchForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("nombre", form.errors)

    def test_form_nombre_too_long(self):
        form_data = {
            "nombre": "A" * 201,
            "direccion": "Calle Test 123"
        }
        form = BatchForm(data=form_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("nombre", form.errors)

    def test_form_with_valid_image(self):
        image = BytesIO()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image, "PNG")
        image.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test.png",
            image.getvalue(),
            content_type="image/png"
        )
        
        form_data = {"nombre": "Lote Test"}
        form = BatchForm(data=form_data, files={"imagen": uploaded_file})
        
        self.assertTrue(form.is_valid())

    def test_form_clean_nombre_strips_whitespace(self):
        form_data = {
            "nombre": "  Lote Test  ",
            "direccion": "Calle Test"
        }
        form = BatchForm(data=form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["nombre"], "Lote Test")


class BatchViewTests(TestCase):
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

    def test_batch_list_requires_login(self):
        response = self.client.get(reverse("batches:list"))
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_batch_list_shows_user_batches(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("batches:list"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lote Test")
        self.assertTemplateUsed(response, "batches/batch_list.html")

    def test_batch_list_filters_by_user(self):
        Batch.objects.create(
            nombre="Lote Otro",
            usuario=self.other_user
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse("batches:list"))
        
        self.assertContains(response, "Lote Test")
        self.assertNotContains(response, "Lote Otro")

    def test_batch_list_search_functionality(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("batches:list") + "?search=Test")
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lote Test")

    def test_batch_list_ordering(self):
        Batch.objects.create(
            nombre="A Lote",
            usuario=self.user
        )
        
        self.client.force_login(self.user)
        response = self.client.get(reverse("batches:list") + "?order=nombre")
        
        self.assertEqual(response.status_code, 200)
        batches = list(response.context["batches"])
        self.assertEqual(batches[0].nombre, "A Lote")

    def test_batch_create_requires_login(self):
        response = self.client.get(reverse("batches:create"))
        
        self.assertEqual(response.status_code, 302)

    def test_batch_create_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("batches:create"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "batches/batch_form.html")
        self.assertIsInstance(response.context["form"], BatchForm)

    def test_batch_create_view_post_valid(self):
        self.client.force_login(self.user)
        
        data = {
            "nombre": "Nuevo Lote",
            "direccion": "Nueva Direccion"
        }
        response = self.client.post(reverse("batches:create"), data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Batch.objects.filter(nombre="Nuevo Lote").exists())
        
        new_batch = Batch.objects.get(nombre="Nuevo Lote")
        self.assertEqual(new_batch.usuario, self.user)

    def test_batch_create_view_post_invalid(self):
        self.client.force_login(self.user)
        
        data = {"direccion": "Sin nombre"}
        response = self.client.post(reverse("batches:create"), data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Batch.objects.filter(direccion="Sin nombre").exists())

    def test_batch_update_requires_login(self):
        response = self.client.get(reverse("batches:update", args=[self.batch.pk]))
        
        self.assertEqual(response.status_code, 302)

    def test_batch_update_view_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("batches:update", args=[self.batch.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "batches/batch_form.html")
        self.assertEqual(response.context["object"], self.batch)

    def test_batch_update_view_post_valid(self):
        self.client.force_login(self.user)
        
        data = {
            "nombre": "Lote Actualizado",
            "direccion": "Nueva Direccion"
        }
        response = self.client.post(
            reverse("batches:update", args=[self.batch.pk]), 
            data
        )
        
        self.assertEqual(response.status_code, 302)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.nombre, "Lote Actualizado")

    def test_batch_update_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("batches:update", args=[self.batch.pk]))
        
        self.assertEqual(response.status_code, 404)

    def test_batch_delete_requires_login(self):
        response = self.client.post(reverse("batches:delete", args=[self.batch.pk]))
        
        self.assertEqual(response.status_code, 302)

    def test_batch_delete_view(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("batches:delete", args=[self.batch.pk]))
        
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Batch.objects.filter(pk=self.batch.pk).exists())

    def test_batch_delete_prevents_other_user_access(self):
        self.client.force_login(self.other_user)
        response = self.client.post(reverse("batches:delete", args=[self.batch.pk]))
        
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Batch.objects.filter(pk=self.batch.pk).exists())


class BatchSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def create_test_image(self, filename="test.png"):
        image = BytesIO()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image, "PNG")
        image.seek(0)
        
        return SimpleUploadedFile(
            filename,
            image.getvalue(),
            content_type="image/png"
        )

    def test_image_deleted_on_batch_delete(self):
        image_file = self.create_test_image("delete_test.png")
        batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user,
            imagen=image_file
        )
        
        image_path = batch.imagen.name
        storage = batch.imagen.storage
        
        self.assertTrue(storage.exists(image_path))
        
        batch.delete()
        
        self.assertFalse(storage.exists(image_path))

    def test_old_image_deleted_on_update(self):
        old_image = self.create_test_image("old_image.png")
        batch = Batch.objects.create(
            nombre="Lote Test",
            usuario=self.user,
            imagen=old_image
        )
        
        old_image_path = batch.imagen.name
        storage = batch.imagen.storage
        
        self.assertTrue(storage.exists(old_image_path))
        
        new_image = self.create_test_image("new_image.png")
        batch.imagen = new_image
        batch.save()
        
        self.assertFalse(storage.exists(old_image_path))
        self.assertTrue(storage.exists(batch.imagen.name))
        self.assertNotEqual(old_image_path, batch.imagen.name)

    def test_no_error_when_deleting_batch_without_image(self):
        batch = Batch.objects.create(
            nombre="Lote Sin Imagen",
            usuario=self.user
        )
        
        try:
            batch.delete()
        except Exception as e:
            self.fail(f"Deleting batch without image raised an exception: {e}")
