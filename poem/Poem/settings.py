# Django settings
from os import path as os_path
from ConfigParser import RawConfigParser, NoSectionError
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

    SERVICETYPE_URL = config.get('SYNC', 'servicetype')
    VO_URL = config.get('SYNC', 'vo')

    SECRET_KEY = config.get('SECURITY','SecretKey')
    ALLOWED_HOSTS = config.get('SECURITY', 'AllowedHosts')
    HOST_CERT = config.get('SECURITY', 'HostCert')
    HOST_KEY = config.get('SECURITY', 'HostKey')

    DEBUG = bool(config.get('GENERAL','debug'))
    POEM_NAMESPACE = config.get('GENERAL', 'namespace')
    TIME_ZONE = config.get('GENERAL', 'timezone')

except NoSectionError as e:
    print e
    raise SystemExit(1)

except ImproperlyConfigured as e:
    print e
    raise SystemExit(1)


URL_DEBUG = True

if ',' in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(',')]
else:
    ALLOWED_HOSTS = [ALLOWED_HOSTS]

TEMPLATE_DEBUG = DEBUG

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
#USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_URL = ''
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = '/'
STATIC_ROOT = '/usr/share/poem/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gjrm%pqd!)3l^)x%5)nb1r%x6_2c1lo@j#)1*sh9hwwzfji8dw'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        'django.template.loaders.eggs.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'Poem.poem.context_processors.admin_settings',
)

MIDDLEWARE_CLASSES = (
    'reversion.middleware.RevisionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#   'Poem.auth_backend.ssl.middleware.SSLMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'Poem.auth_backend.cust.backends.CustModelBackend',
    'Poem.auth_backend.saml2.backends.SAML2Backend',
#   'Poem.auth_backend.ssl.backends.SSLBackend',
)

SSL_USERNAME = 'SSL_CLIENT_S_DN_CN'
SSL_DN = 'SSL_CLIENT_S_DN'
SSL_CREATE_ACTIVE = True
SSL_CREATE_STAFF = True
SSL_SERIAL = 'SSL_CLIENT_M_SERIAL'


AUTH_USER_MODEL = 'poem.CustUser'
ROOT_URLCONF = 'Poem.urls'

TEMPLATE_DIRS = (
    os_path.join(APP_PATH, 'poem/templates'),
)

APPEND_SLASH=True

INSTALLED_APPS = (
    'flat',
    'reversion',
    'reversion_compare',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'ajax_select',
    'Poem.poem',
    'south',
    'djangosaml2'
)

AJAX_LOOKUP_CHANNELS = {
    'hintsvo' : ('Poem.poem.lookups', 'VOLookup'),
    'hintstags' : ('Poem.poem.lookups', 'TLookup'),
    'hintsprobes' : ('Poem.poem.lookups', 'PLookup'),
    'hintsmetricsfilt' : ('Poem.poem.lookups', 'MFiltLookup'),
    'hintsmetricsall' : ('Poem.poem.lookups', 'MAllLookup'),
    'hintsmetricinstances' : ('Poem.poem.lookups', 'MILookup'),
    'hintsserviceflavours' : ('Poem.poem.lookups', 'SFLookup'),
}

# load SAML settings
try:
    if os_path.exists(SAML_CONFIG_FILE):
        buf = open(SAML_CONFIG_FILE).readlines()
        buf = ''.join(buf)
        exec buf
    else:
        print '%s does not exist' % SAML_CONFIG_FILE
        raise SystemExit(1)

except Exception as e:
    print e
    raise SystemExit(1)
