
from distutils.core import setup
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

def get_ver():
    try:
        for line in open(NAME+'.spec'):
            if "Version:" in line:
                return line.split()[1]
    except IOError:
        print "Make sure that %s is in directory"  % (NAME+'.spec')
        sys.exit(1)

poem_media_files = get_files("/usr/share", "poem/media")

setup(name=NAME,
    version=get_ver(),
    description='Profile Management (POEM) for ARGO.',
    author='CERN',
    author_email='tom-developers@cern.ch',
    license='GPL',
    long_description='''The Profile Management (POEM) system couples metrics
                        and services and enables profile-based configuration of SAM/Nagios.''',
    url='https://tomtools.cern.ch/confluence/display/SAM/POEM',
    scripts = ['bin/poem-syncvo', 'bin/poem-syncservtype',
               'bin/poem-createdb', 'bin/poem-importprofiles'],
    data_files = [
        ('/etc/poem', ['etc/poem.ini', 'etc/poem_logging.ini']),
        ('/etc/cron.d/', ['cron/poem-syncvosf']),
        ('/etc/httpd/conf.d', ['poem/apache/poem.conf']),
        ('/usr/share/poem/apache', ['poem/apache/poem.wsgi']),
    ] + poem_media_files,
    package_dir = {'Poem': 'poem/Poem'},
    packages = ['Poem', 'Poem.poem', 'Poem.poem.management',
                'Poem.poem.management.commands', 'Poem.ssl_auth', 'Poem.sync',
                'Poem.poem.templatetags'],
    package_data = {'Poem' : ['poem/templates/admin/*.html', 'poem/templates/poem/*.html',
                              'poem/templates/admin/poem/profile/*.html', 'poem/templates/hints_*',
                              'poem/templates/metrics_in_profiles', 'poem/templates/profiles',
                              'poem/templates/admin/edit_inline/*.html']
                    },
)

