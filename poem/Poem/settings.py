# Django settings for mddb_web project.
from os import path as os_path
from ConfigParser import RawConfigParser, NoSectionError

from django.core.exceptions import ImproperlyConfigured

PROJECT_NAME = 'poem'
APP_PATH = os_path.abspath(os_path.split(__file__)[0])
PROJECT_PATH = os_path.abspath(os_path.join(APP_PATH, '..'))
CONFIG_FILE = '/etc/poem/poem.ini'

config = RawConfigParser()
if not config.read([CONFIG_FILE]):
    raise ImproperlyConfigured('Unable to parse config file %s' % CONFIG_FILE)

try:
    # General
    ADMIN_NAME = config.get('general','ADMIN_NAME')
    ADMIN_EMAIL = config.get('general','ADMIN_EMAIL')
    # Database
    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    DATABASES = {
        'default': {
            'NAME': config.get('database', 'DATABASE_PATH'),
            'ENGINE': 'django.db.backends.sqlite3',
        }
    }
    # Others
    # Make these unique, and don't share it with anybody.
    POEM_NAMESPACE = config.get('others', 'POEM_NAMESPACE')
    LOG_CONFIG = config.get('log', 'LOG_CONFIG')
    SECRET_KEY = config.get('others','SECRET_KEY')
    DEBUG = bool(config.get('others','DEBUG') == 'True')
    GOCDB_SERVICETYPE_URL = config.get('others', 'GOCDB_SERVICETYPE_URL')
    CIC_VO_URL = config.get('others', 'CIC_VO_URL')
    HOST_CERT = config.get('others', 'HOST_CERT')
    HOST_KEY = config.get('others', 'HOST_KEY')
    ATP_URL = config.get('others', 'ATP_URL')
    POEM_URL_PREFIX = config.get('others', 'POEM_URL_PREFIX')
    TIME_ZONE = config.get('others', 'TIME_ZONE')

except NoSectionError, e:
    raise ImproperlyConfigured(e)

if DEBUG:
    PISTON_DISPLAY_ERRORS = True
else:
    PISTON_DISPLAY_ERRORS = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}

TEMPLATE_DEBUG = DEBUG
ADMINS = (
    (ADMIN_NAME, ADMIN_EMAIL),
)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#TIME_ZONE = 'Europe/Zagreb'

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
if DEBUG:
    MEDIA_ROOT = os_path.join(APP_PATH, 'media')
else:
    MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
# MEDIA_URL = '/poem_media/'
STATIC_URL = '/poem_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/poem_media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'gjrm%pqd!)3l^)x%5)nb1r%x6_2c1lo@j#)1*sh9hwwzfji8dw'

CACHE_BACKEND = 'locmem://?timeout=3600&max_entries=400'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'Poem.ssl_auth.middleware.SSLMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'Poem.ssl_auth.backends.SSLBackend',
)

SSL_USERNAME = 'SSL_CLIENT_S_DN_CN'
SSL_DN = 'SSL_CLIENT_S_DN'
SSL_CREATE_ACTIVE = True
SSL_CREATE_STAFF = True
SSL_SERIAL = 'SSL_CLIENT_M_SERIAL'

AUTH_PROFILE_MODULE = 'poem.UserProfile'

ROOT_URLCONF = 'Poem.urls'

TEMPLATE_DIRS = (
    #os_path.join(os_path.dirname(__file__), 'templates').replace('\\','/'),
    os_path.join(APP_PATH, 'poem/templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
	'sslserver',
    'Poem.poem',
)
