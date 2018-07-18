# Django settings
from os import path as os_path
from configparser import RawConfigParser, NoSectionError
from distutils.sysconfig import get_python_lib
from django.core.exceptions import ImproperlyConfigured
import saml2

PROJECT_NAME = 'poem'
APP_PATH = os_path.abspath(os_path.split(__file__)[0])
PROJECT_PATH = os_path.abspath(os_path.join(APP_PATH, '..'))
CONFIG_FILE = '/etc/poem/poem.conf'
LOG_CONFIG = '/etc/poem/poem_logging.conf'
SAML_CONFIG_FILE = '/etc/poem/saml2.conf'

try:
    config = RawConfigParser()

    if not config.read([CONFIG_FILE]):
        raise ImproperlyConfigured('Unable to parse config file %s' % CONFIG_FILE)

    # General
    DEBUG = bool(config.get('GENERAL','debug'))
    POEM_NAMESPACE = config.get('GENERAL', 'namespace')
    TIME_ZONE = config.get('GENERAL', 'timezone')
    SAMLLOGINSTRING = config.get('GENERAL', 'samlloginstring')

    SUPERUSER_NAME = config.get('SUPERUSER', 'name')
    SUPERUSER_PASS = config.get('SUPERUSER', 'password')
    SUPERUSER_EMAIL = config.get('SUPERUSER', 'email')

    if not all([SUPERUSER_EMAIL, SUPERUSER_NAME, SUPERUSER_PASS]):
        raise ImproperlyConfigured('Missing superuser value in config file %s' % CONFIG_FILE)


    DATABASES = {
        'default': {
            'NAME':  '/var/lib/poem/poemserv.db',
            'ENGINE': 'django.db.backends.sqlite3',
        }
    }
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'TIMEOUT': 7200,
            'OPTIONS': {
                'MAX_ENTRIES': 8192
            }
        }
    }

    HTTPAUTH = config.getboolean('SYNC', 'useplainhttpauth')
    HTTPUSER = config.get('SYNC', 'httpuser')
    HTTPPASS = config.get('SYNC', 'httppass')

    SERVICETYPE_URL = config.get('SYNC', 'servicetype')
    VO_URL = config.get('SYNC', 'vo')

    ALLOWED_HOSTS = config.get('SECURITY', 'AllowedHosts')
    CAFILE = config.get('SECURITY', 'CAFile')
    CAPATH = config.get('SECURITY', 'CAPath')
    HOST_CERT = config.get('SECURITY', 'HostCert')
    HOST_KEY = config.get('SECURITY', 'HostKey')
    SECRETKEY_PATH = config.get('SECURITY', 'SecretKeyPath')


except NoSectionError as e:
    print(e)
    raise SystemExit(1)

except ImproperlyConfigured as e:
    print(e)
    raise SystemExit(1)

if ',' in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(',')]
else:
    ALLOWED_HOSTS = [ALLOWED_HOSTS]

# Make this unique, and don't share it with anybody.
try:
    SECRET_KEY = open(SECRETKEY_PATH, 'r').read()
except Exception as e:
    print(SECRETKEY_PATH + ': %s' % repr(e))
    raise SystemExit(1)


AUTHENTICATION_BACKENDS = (
    'Poem.auth_backend.cust.backends.CustModelBackend',
    'Poem.auth_backend.saml2.backends.SAML2Backend',
)

AUTH_USER_MODEL = 'poem.CustUser'
ROOT_URLCONF = 'Poem.urls'

APPEND_SLASH = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.sessions',
    'ajax_select',
    'djangosaml2',
    'modelclone',
    'reversion',
    'reversion_compare',
    'Poem.poem',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['{}/poem/templates/'.format(APP_PATH)],
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

AJAX_LOOKUP_CHANNELS = {
    'hintsvo' : ('Poem.poem.lookups', 'VOLookup'),
    'hintstags' : ('Poem.poem.lookups', 'TLookup'),
    'hintsprobes' : ('Poem.poem.lookups', 'PLookup'),
    'hintsmetricsfilt' : ('Poem.poem.lookups', 'MFiltLookup'),
    'hintsmetricsall' : ('Poem.poem.lookups', 'MAllLookup'),
    'hintsmetricinstances' : ('Poem.poem.lookups', 'MILookup'),
    'hintsserviceflavours' : ('Poem.poem.lookups', 'SFLookup'),
}

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

SITE_ID = 1

USE_I18N = True
LANGUAGE_CODE = 'en-us'
USE_L10N = True

URL_DEBUG = True
TEMPLATE_DEBUG = DEBUG


# Django development server settings
# MEDIA_URL = '/poem_media/'
# MEDIA_ROOT = '/usr/share/poem/media/'
# STATIC_URL = '/static/'

# Apache settings
STATIC_URL = '/'
STATIC_ROOT = '/usr/share/poem/static/'

# load SAML settings
try:
    if os_path.exists(SAML_CONFIG_FILE):
        buf = open(SAML_CONFIG_FILE).readlines()
        buf = ''.join(buf)
        exec(buf)
    else:
        print('%s does not exist' % SAML_CONFIG_FILE)
        raise SystemExit(1)

except Exception as e:
    print(e)
    raise SystemExit(1)
