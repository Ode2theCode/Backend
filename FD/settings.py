from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'drf_spectacular',
    # 'rest_framework_simplejwt.token_blacklist',
    
    'corsheaders',
    'storages',
    
    'authentication',
    'groups',
    'home',
    'chat',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
  
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'FD.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'FD.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

AUTH_USER_MODEL = 'authentication.User'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 1
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'FD API',
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

LIARA_ENDPOINT    = os.getenv("LIARA_ENDPOINT")
LIARA_BUCKET_NAME = os.getenv("LIARA_BUCKET_NAME")
LIARA_ACCESS_KEY  = os.getenv("LIARA_ACCESS_KEY")
LIARA_SECRET_KEY  = os.getenv("LIARA_SECRET_KEY")

AWS_ACCESS_KEY_ID       = LIARA_ACCESS_KEY
AWS_SECRET_ACCESS_KEY   = LIARA_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = LIARA_BUCKET_NAME
AWS_S3_ENDPOINT_URL     = LIARA_ENDPOINT
AWS_S3_REGION_NAME      = 'us-east-1'  

STORAGES = {
  "default": {
      "BACKEND": "storages.backends.s3.S3Storage",
  },
  "staticfiles": {
      "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
  },
}
