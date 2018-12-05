
from setuptools import setup
import os
import sys

NAME='poem'

def get_files(install_prefix, directory):
    files = []
    for root, _, filenames in os.walk(directory):
        subdir_files = []
        for filename in filenames:
            subdir_files.append(os.path.join(root, filename))
        if filenames and subdir_files:
            files.append((os.path.join(install_prefix, root), subdir_files))
    return files

poem_media_files = get_files("usr/share", "poem/media") + get_files("usr/share/", "poem/static")

setup(name=NAME,
    version='2.1.0',
    description='Profile, Probes and Metric Configuration Management (POEM) for ARGO Monitoring framework.',
    author='SRCE',
    author_email='dvrcic@srce.hr',
    license='Apache License 2.0',
    long_description=open('README.md').read(),
    long_description_content_type = 'text/markdown',
    install_requires=['django>=2.0,<2.1',
                      'django-ajax-selects',
                      'django-reversion',
                      'djangosaml2',
                      'unidecode'],
    url='https://github.com/ARGOeu/poem',
    classifiers=(
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: POSIX :: Linux",
      ),
    scripts = ['bin/poem-syncvo', 'bin/poem-syncservtype',
               'bin/poem-db', 'bin/poem-importprofiles',
               'bin/poem-exportprofiles', 'bin/poem-genseckey'],
    data_files = [
        ('etc/poem', ['etc/poem.conf', 'etc/poem_logging.conf', 'etc/saml2.conf']),
        ('etc/cron.d/', ['cron/poem-syncvosf', 'cron/poem-clearsessions']),
        ('etc/httpd/conf.d', ['poem/apache/poem.conf']),
        ('usr/share/poem/apache', ['poem/apache/poem.wsgi']),
        ('var/log/poem', ['helpers/empty']),
        ('var/lib/poem', ['helpers/empty']),
    ] + poem_media_files,
    package_dir = {'Poem': 'poem/Poem'},
    packages = ['Poem', 'Poem.auth_backend', 'Poem.poem', 'Poem.poem.management', 'Poem.poem.dbmodels', 'Poem.poem.management.commands',
                'Poem.auth_backend.saml2', 'Poem.sync', 'Poem.auth_backend.cust',
                'Poem.poem.admin_interface', 'Poem.poem.migrations', 'Poem.poem.templatetags'],
    package_data = {'Poem' : ['poem/templates/admin/*.html', 'poem/templates/poem/*.html',
                              'poem/templates/admin/poem/profile/*.html', 'poem/templates/hints_*',
                              'poem/templates/reversion/poem/metric/*.html', 'poem/templates/reversion/poem/probe/*.html',
                              'poem/templates/metrics_in_profiles', 'poem/templates/profiles',
                              'poem/templates/admin/edit_inline/*.html', 'poem/templates/admin/includes/*.html',
                              'poem/templates/admin/auth/user/*.html', 'poem/templates/admin/poem/custuser/*.html',
                              'poem/templates/admin/poem/groupofmetrics/*.html', 'poem/templates/admin/poem/groupofprobes/*.html',
                              'poem/templates/admin/poem/groupofprofiles/*.html', 'poem/templates/admin/poem/metric/*.html',
                              'poem/templates/admin/poem/probe/*.html', 'poem/templates/admin/poem/profile/*.html',
                              'poem/fixtures/*.json',
                              'poem/migrations/*',
                              ]
                    },
)
