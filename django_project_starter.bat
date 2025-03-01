python -m venv env

env\Scripts\activate

python -m pip install --upgrade pip
pip install django django-environ

@REM "core" is the project name
django-admin startproject core

cd core

pip freeze > requirements.txt

@REM "app" is the app name inside "core"
python manage.py startapp app

@REM edit core/settings.py
@REM add 'environ' to INSTALLED_APPS and configure environment variables, template paths, static file paths, etc.

@REM then you can now run the following commands to testrun the basic setup
python manage.py makemigrations
python manage.py migrate

python manage.py runserver

