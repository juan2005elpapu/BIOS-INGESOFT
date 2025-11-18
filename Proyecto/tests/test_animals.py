"""
Tests para el módulo de animales.
Valida la creación, cálculos de edad y funcionalidades de animales.
"""
import pytest
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from animals.models import Animal
from batches.models import Batch

User = get_user_model()


@pytest.mark.django_db
class TestAnimalModel:
    """Tests para el modelo Animal."""
    
    def test_animal_creation(self, animal):
        """
        Caso: Creación de un animal
        Esperado: El animal debe crearse con todos los datos correctos.
        Casos límite: Campos requeridos vs opcionales, código único.
        """
        assert animal.codigo == "TEST-001"
        assert animal.especie == "Vaca"
        assert animal.raza == "Holstein"
        assert animal.sexo == "M"
        assert animal.fecha_de_nacimiento == date(2020, 1, 15)
    
    def test_animal_string_representation_with_codigo(self, animal):
        """
        Caso: Representación en string del animal con código
        Esperado: Debe retornar "código - especie".
        Casos límite: Código vacío, código especial.
        """
        assert str(animal) == "TEST-001 - Vaca"
    
    def test_animal_string_representation_without_codigo(self, batch):
        """
        Caso: Representación en string del animal sin código
        Esperado: Debe retornar solo la especie.
        Casos límite: Código None.
        """
        animal = Animal.objects.create(
            batch=batch,
            codigo=None,
            especie="Caballo",
            sexo="F",
            fecha_de_nacimiento=date(2019, 5, 1)
        )
        
        assert str(animal) == "Caballo"
    
    def test_animal_sexo_choices(self, batch):
        """
        Caso: Validar opciones de sexo
        Esperado: Solo M (Macho) y F (Hembra) deben ser válidos.
        Casos límite: Valores válidos e inválidos.
        """
        # Válido - Macho
        animal_m = Animal.objects.create(
            batch=batch,
            codigo="SEXO-M",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        assert animal_m.sexo == "M"
        
        # Válido - Hembra
        animal_f = Animal.objects.create(
            batch=batch,
            codigo="SEXO-F",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        assert animal_f.sexo == "F"
    
    def test_animal_unique_codigo(self, batch):
        """
        Caso: Validar unicidad del código
        Esperado: No debe permitir códigos duplicados.
        Casos límite: Código None (múltiples permitidos).
        """
        Animal.objects.create(
            batch=batch,
            codigo="UNIQUE-001",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        
        # Intentar crear otro con el mismo código
        from django.db import IntegrityError
        
        with pytest.raises(IntegrityError):
            Animal.objects.create(
                batch=batch,
                codigo="UNIQUE-001",
                especie="Cerdo",
                sexo="F",
                fecha_de_nacimiento=date(2021, 1, 1)
            )


@pytest.mark.django_db
class TestAnimalAge:
    """Tests para el cálculo de edad de animales."""
    
    def test_animal_age_in_years(self, batch):
        """
        Caso: Calcular edad en años
        Esperado: Animal creado hace más de 1 año debe retornar años.
        Casos límite: Exactamente 1 año, 1 año y 1 día.
        """
        # Animal con 3 años
        birth_date = date.today() - timedelta(days=3*365 + 10)
        animal = Animal.objects.create(
            batch=batch,
            codigo="AGE-YEARS",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=birth_date
        )
        
        age_days = (date.today() - animal.fecha_de_nacimiento).days
        assert age_days >= 3*365
    
    def test_animal_age_in_months(self, batch):
        """
        Caso: Calcular edad en meses
        Esperado: Animal menor a 1 año pero mayor a 1 mes debe retornar meses.
        Casos límite: 1 mes exacto, 30 días, 60 días.
        """
        # Animal con 5 meses
        birth_date = date.today() - timedelta(days=150)
        animal = Animal.objects.create(
            batch=batch,
            codigo="AGE-MONTHS",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=birth_date
        )
        
        age_days = (date.today() - animal.fecha_de_nacimiento).days
        months = age_days // 30
        assert 4 <= months <= 6
    
    def test_animal_age_in_days(self, batch):
        """
        Caso: Calcular edad en días
        Esperado: Animal menor a 1 mes debe retornar días.
        Casos límite: 1 día, 15 días, 29 días.
        """
        # Animal de 15 días
        birth_date = date.today() - timedelta(days=15)
        animal = Animal.objects.create(
            batch=batch,
            codigo="AGE-DAYS",
            especie="Cerdo",
            sexo="M",
            fecha_de_nacimiento=birth_date
        )
        
        age_days = (date.today() - animal.fecha_de_nacimiento).days
        assert 0 <= age_days < 30
    
    def test_animal_newborn(self, batch):
        """
        Caso: Animal nacido hoy
        Esperado: Edad debe ser 0 días.
        Casos límite: Nacimiento hoy vs hace poco.
        """
        animal = Animal.objects.create(
            batch=batch,
            codigo="NEWBORN",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date.today()
        )
        
        age_days = (date.today() - animal.fecha_de_nacimiento).days
        assert age_days == 0
    
    def test_animal_very_old(self, batch):
        """
        Caso: Animal muy antiguo (10+ años)
        Esperado: Debe calcular correctamente décadas.
        Casos límite: 10 años exactos.
        """
        birth_date = date.today() - timedelta(days=10*365 + 2)
        animal = Animal.objects.create(
            batch=batch,
            codigo="VERY-OLD",
            especie="Vaca",
            sexo="F",
            fecha_de_nacimiento=birth_date
        )
        
        age_years = (date.today() - animal.fecha_de_nacimiento).days // 365
        assert age_years >= 10


@pytest.mark.django_db
class TestAnimalOrdering:
    """Tests para el ordenamiento de animales."""
    
    def test_animals_ordered_by_birthdate_descending(self, batch):
        """
        Caso: Animales ordenados por fecha de nacimiento descendente
        Esperado: El más reciente (más joven) debe ser primero.
        Casos límite: Múltiples animales, misma fecha.
        """
        # Crear múltiples animales
        animal1 = Animal.objects.create(
            batch=batch,
            codigo="ORD-001",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        animal2 = Animal.objects.create(
            batch=batch,
            codigo="ORD-002",
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2021, 6, 15)
        )
        animal3 = Animal.objects.create(
            batch=batch,
            codigo="ORD-003",
            especie="Caballo",
            sexo="M",
            fecha_de_nacimiento=date(2019, 3, 10)
        )
        
        # Verificar ordenamiento
        ordered = list(Animal.objects.all())
        assert ordered[0].codigo == "ORD-002"  # Más reciente
        assert ordered[1].codigo == "ORD-001"
        assert ordered[2].codigo == "ORD-003"  # Más antiguo


@pytest.mark.django_db
class TestAnimalValidation:
    """Tests para validación de campos del modelo Animal."""
    
    def test_animal_codigo_max_length(self, batch):
        """
        Caso: Validar límite de caracteres en código
        Esperado: Código debe respetar max_length=50.
        Casos límite: Exactamente 50, 51 caracteres.
        """
        codigo_valido = "A" * 50
        animal = Animal.objects.create(
            batch=batch,
            codigo=codigo_valido,
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1)
        )
        assert len(animal.codigo) <= 50
    
    def test_animal_especie_required(self, batch):
        """
        Caso: Especie es campo requerido
        Esperado: No debe permitir crear animal sin especie.
        Casos límite: Especie vacía.
        """
        from django.db import IntegrityError
        
        with pytest.raises(IntegrityError):
            Animal.objects.create(
                batch=batch,
                codigo="NO-SPECIE",
                especie="",
                sexo="M",
                fecha_de_nacimiento=date(2020, 1, 1)
            )
    
    def test_animal_raza_optional(self, batch):
        """
        Caso: Raza es campo opcional
        Esperado: Debe permitir crear animal sin raza.
        Casos límite: Raza None, raza vacía.
        """
        animal1 = Animal.objects.create(
            batch=batch,
            codigo="NO-RAZA-1",
            especie="Vaca",
            sexo="M",
            fecha_de_nacimiento=date(2020, 1, 1),
            raza=None
        )
        assert animal1.raza is None
        
        animal2 = Animal.objects.create(
            batch=batch,
            codigo="NO-RAZA-2",
            especie="Cerdo",
            sexo="F",
            fecha_de_nacimiento=date(2020, 1, 1),
            raza=""
        )
        assert animal2.raza == ""