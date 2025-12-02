from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from animals.models import Animal
from batches.models import Batch

from .forms import CostForm
from .models import Cost
from .views import CostListView

User = get_user_model()


class CostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="testpass")
        self.other_user = User.objects.create_user(username="intruder", password="testpass")
        self.batch = Batch.objects.create(usuario=self.user, nombre="Lote 1")
        self.other_batch = Batch.objects.create(usuario=self.other_user, nombre="Otro lote")
        self.animal = Animal.objects.create(
            batch=self.batch,
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 1)
        )

    def test_cost_str(self):
        cost = Cost.objects.create(
            batch=self.batch,
            animal=self.animal,
            tipo=Cost.CostType.FEED,
            concepto="Concentrado",
            monto=Decimal("120.50"),
            fecha=date.today(),
        )

        self.assertIn("Concentrado", str(cost))
        self.assertIn(self.batch.nombre, str(cost))

    def test_for_user_queryset_filters_by_owner(self):
        cost = Cost.objects.create(
            batch=self.batch,
            tipo=Cost.CostType.OTHER,
            concepto="Transporte",
            monto=Decimal("50.00"),
            fecha=date.today(),
        )
        Cost.objects.create(
            batch=self.other_batch,
            tipo=Cost.CostType.OTHER,
            concepto="Ajeno",
            monto=Decimal("75.00"),
            fecha=date.today(),
        )

        results = list(Cost.objects.for_user(self.user))
        self.assertEqual(results, [cost])


class CostFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="owner", password="testpass")
        self.batch = Batch.objects.create(usuario=self.user, nombre="Principal")
        self.animal = Animal.objects.create(
            batch=self.batch,
            especie="Toro",
            sexo="M",
            fecha_de_nacimiento=date(2019, 5, 20)
        )
        self.other_batch = Batch.objects.create(usuario=self.user, nombre="Secundario")
        self.other_animal = Animal.objects.create(
            batch=self.other_batch,
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2021, 6, 15)
        )

    def test_valid_form(self):
        form = CostForm(
            data={
                "batch": self.batch.id,
                "animal": self.animal.id,
                "tipo": Cost.CostType.FEED,
                "concepto": "Alimento",
                "monto": "200.00",
                "fecha": date.today(),
                "notas": "Compra mensual",
            },
            user=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_rejects_animal_from_other_batch(self):
        form = CostForm(
            data={
                "batch": self.batch.id,
                "animal": self.other_animal.id,
                "tipo": Cost.CostType.HEALTH,
                "concepto": "Vacuna",
                "monto": "30.00",
                "fecha": date.today(),
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_rejects_future_date(self):
        future_date = date.today() + timedelta(days=1)
        form = CostForm(
            data={
                "batch": self.batch.id,
                "tipo": Cost.CostType.MAINTENANCE,
                "concepto": "Reparación",
                "monto": "80.00",
                "fecha": future_date,
            },
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("fecha", form.errors)


class CostListViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="owner", password="testpass")
        self.other_user = User.objects.create_user(username="intruder", password="testpass")
        self.batch = Batch.objects.create(usuario=self.user, nombre="Lote 1")
        self.animal = Animal.objects.create(
            batch=self.batch,
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        self.cost = Cost.objects.create(
            batch=self.batch,
            animal=self.animal,
            tipo=Cost.CostType.FEED,
            concepto="Pasto",
            monto=Decimal("45.00"),
            fecha=date.today(),
        )
        other_batch = Batch.objects.create(usuario=self.other_user, nombre="Otro lote")
        Cost.objects.create(
            batch=other_batch,
            tipo=Cost.CostType.OTHER,
            concepto="Ajeno",
            monto=Decimal("99.00"),
            fecha=date.today(),
        )

    def test_queryset_filters_by_user_and_batch(self):
        request = self.factory.get("/", {"batch": self.batch.id})
        request.user = self.user

        view = CostListView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(list(queryset), [self.cost])

    def test_search_filter(self):
        request = self.factory.get("/", {"search": "Pasto"})
        request.user = self.user

        view = CostListView()
        view.request = request
        queryset = view.get_queryset()

        self.assertEqual(list(queryset), [self.cost])
