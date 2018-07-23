
from setuptools import setup
import os, sys

NAME='poem'

def get_files(install_prefix, directory):
    files = []
    for root, _, filenames in os.walk(directory):
        subdir_files = []
        for filename in filenames:
            if 'svn' not in root:
                subdir_files.append(os.path.join(root, filename))
        if filenames and subdir_files:
            files.append((os.path.join(install_prefix, root), subdir_files))
    return files

poem_media_files = get_files("/usr/share", "poem/media") + get_files("/usr/share/", "poem/static")

setup(name=NAME,
    version='2.0.0-rc1',
    description='Profile, Probes and Metric configuration Management (POEM) for ARGO Monitoring framework.',
    author='SRCE',
    author_email='dvrcic@srce.hr',
    license='Apache License 2.0',
    long_description="""
                    POEM service is a light web application used in ARGO framework that holds list
                    of services, metrics and probes used within EGI infrastructure. Services and
                    associated metrics are grouped into POEM profiles that instruct monitoring
                    instances what kind of tests to execute for given service. Additionally, it is
                    a register of probes and Nagios metric configurations exposed to monitoring
                    instances via REST API.

                    It is based on Django web framework, specifically extension of its admin
                    interface and several Django modules. EGI users are allowed to sign-in through
                    EGI CheckIn federated authentication mechanism. Application is served with
                    Apache web server and all its information is stored in light SQLite database.

                    Devel instance: https://poem-devel.argo.grnet.gr/

                    Production instance: https://poem.egi.eu/

                    More info: http://argoeu.github.io/guides/poem
                    """,
    url='https://github.com/ARGOeu/poem',
    classifiers=(
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: Linux",
      ),
    scripts = ['bin/poem-syncvo', 'bin/poem-syncservtype',
               'bin/poem-db', 'bin/poem-importprofiles',
               'bin/poem-exportprofiles', 'bin/poem-genseckey'],
    data_files = [
        ('/etc/poem', ['etc/poem.conf', 'etc/poem_logging.conf', 'etc/saml2.conf']),
        ('/etc/cron.d/', ['cron/poem-syncvosf', 'cron/poem-clearsessions']),
        ('/etc/httpd/conf.d', ['poem/apache/poem.conf']),
        ('/usr/share/poem/apache', ['poem/apache/poem.wsgi']),
    ] + poem_media_files,
    package_dir = {'Poem': 'poem/Poem'},
    packages = ['Poem', 'Poem.auth_backend', 'Poem.poem', 'Poem.poem.management', 'Poem.poem.dbmodels', 'Poem.poem.management.commands',
                'Poem.auth_backend.saml2', 'Poem.sync', 'Poem.auth_backend.cust',
                'Poem.poem.admin_interface', 'Poem.poem.migrations'],
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

