"""
Django settings for docval project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-pj)i)sori*#ajic3lh2yr%n%*%x7c6u=rs*oito+gup9h*vazt'
DEBUG = True

ALLOWED_HOSTS = [
    'sna-2-0-3.onrender.com',
    '.onrender.com',
    '127.0.0.1',
    'localhost'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ para servir estáticos en Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'docval.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'docval.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sna_db_80w3',
        'USER': 'sna_user',
        'PASSWORD': 'ZfPo3nRNTmi5VkmS4siPgmlnCBE37Rmy',
        'HOST': 'dpg-d91fmnhkh4rs73a8au30-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es'   # ✅ mejor en español si tu app es para SENA
TIME_ZONE = 'America/Bogota'  # ✅ ajustado a Colombia
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# URL del backend FastAPI
BACKEND_URL = os.getenv("BACKEND_URL", "https://documentacion-sena-ia-01.onrender.com")

# ✅ Configuración de autenticación personalizada
LOGIN_URL = '/login/'                # Redirección cuando no está autenticado
LOGIN_REDIRECT_URL = '/cargar_documentos/'
 # Página después de iniciar sesión
LOGOUT_REDIRECT_URL = '/login/'      # Página después de cerrar sesión
