# Django settings for mddb_web project.
from settings import *

# Specify your custom test runner to use
TEST_RUNNER = 'poem.tests.test_coverage.run_tests'
 
# List of modules to enable for code coverage
COVERAGE_MODULES = ['poem', 'poem_api']

try:
    DATABASES = {
        'default': {
            'NAME': config.get('database', 'DATABASE_NAME'),
            'ENGINE': config.get('database', 'DATABASE_ENGINE'),
            'USER': config.get('database', 'DATABASE_USER'),
            'PASSWORD': config.get('database', 'DATABASE_PASSWORD'),
            'HOST': config.get('database', 'DATABASE_HOST'),
            'PORT': config.get('database', 'DATABASE_PORT'),
            'TEST_NAME': config.get('others','TEST_DATABASE_NAME'),
            'TEST_USER': config.get('others','TEST_DATABASE_USER'),
            'TEST_PASSWD':  config.get('others','TEST_DATABASE_PASSWD'),
            'TEST_CREATE': config.get('others','TEST_DATABASE_CREATE'),
            'TEST_USER_CREATE': config.get('others', 'TEST_USER_CREATE')
        }
    }
except NoSectionError, e:
    pass
except NoOptionError, e:
    pass

