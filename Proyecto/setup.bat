@echo off
setlocal enabledelayedexpansion
set "PROJECT_ROOT=%~dp0"
pushd "%PROJECT_ROOT%"
where python >nul 2>nul || (echo Python 3 es requerido en el PATH. & exit /b 1)
if not exist "%PROJECT_ROOT%\.venv" (
  python -m venv "%PROJECT_ROOT%\.venv"
)
call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py test
popd
endlocal
