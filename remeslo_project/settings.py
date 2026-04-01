from pathlib import Path
from decouple import config, Csv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-38op+anok6d=x&x0y2q8h!1kjku9^kkyar(4z+55@+5i8=lz0f'
SECRET_KEY = config('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = config('DEBUG', default = False, cast = bool)
# ALLOWED_HOSTS = []
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default = '', cast = Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
    'telegram_bot',
]

MIDDLEWARE = [
    # Безопасность (HTTPS, XSS защита)
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # Работа с сессиями
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Общие вещи (редиректы, просмотры)
    'django.middleware.common.CommonMiddleware',
    # Защита от CSRF атак
    'django.middleware.csrf.CsrfViewMiddleware',
    # Аутентификация пользователя
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Система сообщений
    'django.contrib.messages.middleware.MessageMiddleware',
    # Защита от Clickjacking атак
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'remeslo_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'shop', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.cart_item_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'remeslo_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DATABASE_NAME'),
        'USER': config('DATABASE_USER'),
        'PASSWORD': config('DATABASE_PASSWORD'),
        'HOST': config('DATABASE_HOST'),
        'PORT': config('DATABASE_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Кэширование соединений
        'OPTIONS': {
            'sslmode': 'require',  # Обязательно для Railway
        },
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Куда перенаправлять при успешном входе
LOGIN_REDIRECT_URL = '/'
# Куда перенаправлять после выхода 
LOGOUT_REDIRECT_URL = '/'
# Страница входа, если пользователь не авторизован
LOGIN_URL = '/login/'

                        # Пароль или приложение пароль         

# Время жизни сессии 
SESSION_COOKIE_AGE = 1209600 # 2 недели

# Использование HTTPS для кук сессии (в продакшене True)
SESSION_COOKIE_SECURE = False

# Название кук сессии
SESSION_COOKIE_NAME = 'sessionid'

# Доверенные источники для CSRF
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default = '' , cast=Csv())

# TELEGRAM_BOT
# TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='')
# TELEGRAM_BOT_TOKEN = config('TELEGRAM_ADMIN_IDS', default='',cast=Csv())

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')  # правильно указываем сервер Gmail
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = 'craftremeslo@gmail.com'  # лучше делать также через config, если он секретный
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER