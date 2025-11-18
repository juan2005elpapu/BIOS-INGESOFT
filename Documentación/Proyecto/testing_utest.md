# Testing Unitario — Proyecto BIOS-INGESOFT

Autor del documento: <Nombre del equipo / responsable>  
Ruta final requerida (PDF): Documentación/Proyecto/testing_utest.pdf

---

## 1. Propósito
Documentar las pruebas unitarias implementadas por los integrantes del grupo. Cada integrante debe aportar un mínimo de 3 pruebas unitarias orientadas a funcionalidades centrales, incluyendo sus casos límite y la forma de ejecutarlas desde el entorno del proyecto.

## 2. Herramientas y dependencias
- Framework de testing sugerido: pytest
- Dependencias recomendadas (development): pytest, pytest-cov, requests-mock (si aplica)
- Comandos básicos:
  - Crear entorno: `python -m venv .venv`
  - Activar (Linux/macOS): `source .venv/bin/activate`  
    Windows (PowerShell): `.venv\Scripts\Activate.ps1`
  - Instalar dev deps: `pip install -r requirements-dev.txt` (o `pip install pytest pytest-cov`)

## 3. Estructura de tests recomendada
- tests/
  - conftest.py
  - unit/
  - integration/  (si aplica)
- Convención: archivos `test_*.py`, funciones `test_*` o clases `Test*`.

## 4. Cómo ejecutar pruebas
- Ejecutar todos: `pytest -q`
- Ejecutar con cobertura: `pytest --cov=myapp --cov-report=term-missing`
- Ejecutar un test concreto: `pytest tests/unit/test_mi_modulo.py::test_caso_especifico -q`

---

## 5. Plantilla para documentar cada prueba
Para cada prueba incluir:
- Archivo: (ruta del test)
- Nombre de la prueba (función): 
- Autor:
- Objetivo: (qué comportamiento valida y por qué es esencial)
- Entradas: (valores exactos; incluir casos límite)
- Resultado esperado: (valor, excepción o side-effect)
- Setup/fixtures: (fixtures pytest o mocks necesarios)
- Comando para ejecutar: (ej. `pytest ...`)
- Observaciones: (tiempos, dependencias externas, si requiere DB en memoria)

---

## 6. Listado de pruebas por integrante (ejemplos)
### Integrante: Juan Pérez
- Test 1
  - Archivo: tests/unit/test_grades.py
  - Función: test_calculate_final_grade_basic
  - Objetivo: validar cálculo de promedio ponderado
  - Entradas: [10,9,8] | [0,0,0] | [10,10,0]
  - Resultado esperado: 9.0 | 0.0 | aproximadamente 6.6667
  - Caso límite: lista vacía -> ValueError
  - Comando: `pytest tests/unit/test_grades.py::test_calculate_final_grade_basic -q`
- Test 2
  - ...
- Test 3
  - ...

### Integrante: María Gómez
- (listas de pruebas con la misma plantilla)

> Repite la sección por cada integrante. Asegúrate de que cada persona tenga al menos 3 pruebas registradas.

---

## 7. Casos límite recomendados (por tipo)
- Funciones numéricas: 0, máximos, negativos, NaN (si aplica), overflow.
- Validaciones: strings vacíos, None, tipos inesperados.
- I/O / APIs: respuestas 200, 400, 500; timeouts; payloads vacíos.
- Concurrencia: llamadas simultáneas (si aplica), locks.
- Persistencia: transacciones exitosas y rollback en fallos.

---

## 8. Recomendaciones para CI (GitHub Actions)
Ejemplo de job: instalar dependencias y ejecutar pytest.
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest -q --cov=myapp
```

---

## 9. Cómo dejar evidencia en el documento (logs / capturas)
- Incluye recortes de salida de pytest (stdout), o un archivo `tests/reports/*.txt` y añádelo como anexo.
- Para capturas: guarda imágenes en `Documentación/Proyecto/evidencia/` y refiérelas en el PDF.

---

## 10. Política para comprobar "≥ 3 pruebas por integrante"
Opciones razonables:
- Registro obligatorio: cada autor añade su nombre y pruebas en este documento.
- Revisión de PR: plantilla de PR obliga a listar tests añadidos.
- (Opcional, automatizable) Script que cuente tests nuevos por autor en la rama; por simplicidad y rapidez, preferimos el registro manual en este documento.

---

## 11. Anexos
- Comandos útiles:
  - Contar tests en el repo: `pytest --collect-only -q | wc -l`
  - Ejecutar un solo archivo: `pytest tests/unit/test_x.py -q`
- Recursos: enlaces a pytest docs, pandoc, wkhtmltopdf.
