import os
import logging
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "apps.users",
    "apps.risk",
    "apps.transactions",
    "apps.system",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.users.middleware.UserLanguageMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://backend-production-b894.up.railway.app"
]
ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
if DATABASE_URL.startswith("sqlite:///"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # For PostgreSQL or other databases
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User Model
AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

CORS_ALLOW_ALL_ORIGINS = True

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'apikey')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'abassi.loay23@gmail.com')

# Site configuration
SITE_BASE_URL = os.getenv('SITE_BASE_URL', 'http://localhost:3000')
EMAIL_TOKEN_TTL_HOURS = int(os.getenv('EMAIL_TOKEN_TTL_HOURS', '24'))

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{asctime}] [{levelname}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_CONSOLE', 'INFO'),
        },
        'auth_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'auth' / 'auth.log',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_AUTH', 'INFO'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
        'ai_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'ai' / 'ai.log',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_AI', 'INFO'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
        'rules_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'rules' / 'rules.log',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_RULES', 'INFO'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
        'transactions_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'transactions' / 'transactions.log',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_TRANSACTIONS', 'INFO'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
        'system_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'system' / 'system.log',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_SYSTEM', 'INFO'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
        'error_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'errors' / 'errors.log',
            'formatter': 'detailed',
            'level': 'ERROR',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
        'email_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'email' / 'email.log',
            'formatter': 'detailed',
            'level': os.getenv('LOG_LEVEL_EMAIL', 'INFO'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8',
            'delay': True,  # Windows compatibility: delay file opening
        },
    },
    'loggers': {
        # Django framework logging
        'django': {
            'handlers': ['console', 'system_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_DJANGO', 'INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'system_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_DJANGO_REQUEST', 'WARNING'),
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'system_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_DJANGO_SECURITY', 'WARNING'),
            'propagate': False,
        },
        
        # Authentication logging
        'auth': {
            'handlers': ['console', 'auth_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_AUTH', 'INFO'),
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['console', 'auth_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_AUTH', 'INFO'),
            'propagate': False,
        },
        
        # AI/ML logging
        'ai': {
            'handlers': ['console', 'ai_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_AI', 'INFO'),
            'propagate': False,
        },
        'apps.risk.ml': {
            'handlers': ['console', 'ai_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_AI', 'INFO'),
            'propagate': False,
        },
        'fraud_detection': {
            'handlers': ['console', 'ai_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_AI', 'INFO'),
            'propagate': False,
        },
        
        # Rules engine logging
        'rules': {
            'handlers': ['console', 'rules_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_RULES', 'INFO'),
            'propagate': False,
        },
        'apps.risk.engine': {
            'handlers': ['console', 'rules_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_RULES', 'INFO'),
            'propagate': False,
        },
        
        # Transaction logging
        'transactions': {
            'handlers': ['console', 'transactions_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_TRANSACTIONS', 'INFO'),
            'propagate': False,
        },
        'apps.transactions': {
            'handlers': ['console', 'transactions_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_TRANSACTIONS', 'INFO'),
            'propagate': False,
        },
        
        # Email service logging
        'email_service': {
            'handlers': ['console', 'email_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_EMAIL', 'INFO'),
            'propagate': False,
        },
        
        # System logging
        'system': {
            'handlers': ['console', 'system_file', 'error_file'],
            'level': os.getenv('LOG_LEVEL_SYSTEM', 'INFO'),
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'system_file', 'error_file'],
        'level': os.getenv('LOG_LEVEL_ROOT', 'WARNING'),
    },
}

# Create organized logs directory structure and log files if they don't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Create subdirectories for organized logging
log_categories = ['auth', 'ai', 'rules', 'transactions', 'system', 'errors', 'email']
for category in log_categories:
    category_dir = LOGS_DIR / category
    category_dir.mkdir(exist_ok=True)
    
    # Create the main log file for each category
    log_file = category_dir / f'{category}.log'
    if not log_file.exists():
        log_file.touch()

# Legacy: Also ensure the main logs directory has the files for backwards compatibility
legacy_log_files = [
    'auth.log', 'ai.log', 'rules.log', 'transactions.log', 
    'system.log', 'errors.log'
]

for log_file in legacy_log_files:
    log_path = LOGS_DIR / log_file
    if not log_path.exists():
        log_path.touch()

