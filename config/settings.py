import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", os.environ.get("SESSION_SECRET", "local-dev-secret-key"))
DEBUG = True
ALLOWED_HOSTS = ["*"]

_replit_domains = os.environ.get("REPLIT_DOMAINS", "")
_replit_dev = os.environ.get("REPLIT_DEV_DOMAIN", "")

CSRF_TRUSTED_ORIGINS = (
    [f"https://{h}" for h in _replit_domains.split(",") if h]
    + ([f"https://{_replit_dev}"] if _replit_dev else [])
    + [
        "http://localhost",
        "http://127.0.0.1",
        "https://*.replit.dev",
        "https://*.picard.replit.dev",
        "https://*.riker.replit.dev",
        "https://*.kirk.replit.dev",
        "https://*.spock.replit.dev",
        "https://*.janeway.replit.dev",
        "https://*.repl.co",
        "https://*.replit.app",
        "https://*.replit.com",
    ]
)

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = "ALLOWALL"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.attendance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.attendance.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Lubumbashi"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/facial/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/facial/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth
LOGIN_URL = "/facial/login/"
LOGIN_REDIRECT_URL = "/facial/"
LOGOUT_REDIRECT_URL = "/facial/login/"
