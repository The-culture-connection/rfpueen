"""Django settings for rfpueen project."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-please-change-me",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() in {"1", "true", "yes"}

ALLOWED_HOSTS: list[str] = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "opportunities",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "rfpueen.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "opportunities.context_processors.profile_context",
            ],
        },
    },
]


WSGI_APPLICATION = "rfpueen.wsgi.application"
ASGI_APPLICATION = "rfpueen.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "UTC")

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]


LOGIN_REDIRECT_URL = "opportunities:dashboard"
LOGOUT_REDIRECT_URL = "login"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Firebase integrations
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "therfpqueen-f11fd")
FIREBASE_OPPORTUNITIES_COLLECTION = os.environ.get(
    "FIREBASE_OPPORTUNITIES_COLLECTION", "opportunities"
)
FIREBASE_PROFILES_COLLECTION = os.environ.get(
    "FIREBASE_PROFILES_COLLECTION", "profiles"
)


# Matching defaults
MATCHING_DEFAULT_BUCKET = os.environ.get("MATCHING_DEFAULT_BUCKET", "general")
MATCHING_MAX_RESULTS = int(os.environ.get("MATCHING_MAX_RESULTS", "20"))
