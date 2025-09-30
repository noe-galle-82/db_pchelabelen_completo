from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-q=kffe!2f1m^_-bxq-c2r=c*l1d_vwrp@atclh_ji67&jfl86%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clientes',
    'ventas',
    'compras',
    'detalles_venta',
    'detalles_compra',
    'lotes',
    'marcas',
    'movimientos_caja',
    'productos',
    'proveedores',
    'tipo_movimientos',
    'tipo_pago',
    'core',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    # 1. Seguridad (Debe ser lo primero)
    'django.middleware.security.SecurityMiddleware',
    # 2. CORS (Se mueve a una posición segura después de Security)
    'corsheaders.middleware.CorsMiddleware',
    # 3. Sesiones (Debe estar ANTES de Authentication)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 4. Autenticación (Debe estar DESPUÉS de Session)
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 5. Mensajes (Debe estar DESPUÉS de Authentication)
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pchelabelen_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                # CORRECCIÓN DE ERROR 500 ANTERIOR
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pchelabelen_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Indica que usaremos MySQL
        'NAME': 'db2pchelabelen',             # Nombre de la DB que creaste
        'USER': 'root',           # Tu usuario de MySQL (e.g., 'root' o 'user_django')
        'PASSWORD': '291003',     # Tu contraseña de MySQL
        'HOST': 'localhost',                   # Dirección donde corre MySQL
        'PORT': '3306',                        # Puerto estándar de MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}
#DATABASES = {
    #   'default': {
    #      'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
#}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ]
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# =========================
# CONFIGURACIÓN DE SEGURIDAD
# =========================

# URL a la que redirigir al usuario si intenta acceder a una vista protegida sin iniciar sesión.
LOGIN_URL = 'login'       

# URL a la que redirigir al usuario después de un inicio de sesión exitoso.
LOGIN_REDIRECT_URL = '/'  

# URL a la que redirigir al usuario después de cerrar sesión.
LOGOUT_REDIRECT_URL = '/'