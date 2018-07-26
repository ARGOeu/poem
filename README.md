# POEM service for ARGO framework

## Description

POEM service is a web application used in ARGO monitoring framework that holds list of services, metrics, metric configurations and Nagios probes used within EGI infrastructure. Services and associated metrics are grouped into POEM profiles that instruct monitoring instances what kind of tests to execute for given service. Additionally, it is a register of probes and Nagios metric configurations exposed to Nagios monitoring instances via REST API and with such integration, it helps in speeding up of testing and deployment of probes.

It is based on Django web framework, specifically extension of its admin interface and several Django packages. EGI users are allowed to sign-in through EGI CheckIn federated authentication mechanism. Application is served with Apache web server and all its data is stored in light SQLite database.

POEM service is based on Django 2.x framework and following Django packages from [PyPI](https://pypi.org/):
* `django-reversion` - provides the basic versioning for Probes and Metric configurations 
* `django-reversion-compare` - provides the diff view for Probes and Metric configuration progress 
* `django-modelclone` - simplify deriving of Profiles and Metric configuration from existing data 
* `django-ajax-selects` - ease the creation of auto-complete fields
* `djangosaml2` - enable SAML2 login feature
* `mod-wsgi`, `mod-wsgi-httpd` - WSGI interface that will be automatically build and linked against needed Python 3.x version 

Devel instance: https://poem-devel.argo.grnet.gr/

Production instance: https://poem.egi.eu/

More info: http://argoeu.github.io/guides/poem

## Installation

POEM web service is meant to be running with Django 2.x driven by Python 3.x on CentOS 7 and served by system-wide installation of Apache from base repository. Setting up Python virtual environment based on Python 3.x is prerequisite. Once the virtual environment is set up, installation of the service simply narrows down to creating and installing wheel package that will also pull and install all needed dependencies. Beside wheel dependencies, service also needs some packages to be installed from CentOS 7 repositories as it will be served by default Apache installation:

```sh
yum -y install \
	ca-certificates \
	gcc git make which \
	xmlsec1 xmlsec1-openssl \
	httpd httpd-devel \
	mod_ssl
```

Layout of POEM web service files on the filesystem depends on the location of virtual environment. By the default, service assumes it is:

```sh
VENV = /home/pyvenv/poem/
```

| File Types								   | Destination                                         |
|------------------------------|-----------------------------------------------------|
| Configuration - General		   | `VENV/etc/poem/poem.conf`                           |
| Configuration - Logging		   | `VENV/etc/poem/poem_logging.conf`                   |
| Configuration - Apache		   | `/etc/httpd/conf.d/poem.conf`                       |
| Configuration - SAML2			   | `VENV/etc/poem/saml2.conf`                          |
| Cron jobs									   | `/etc/cron.d/poem-clearsessions, poem-syncvosf`     |
| Database handler					   | `VENV/bin/poem-db`                                  |
| Sync (VO, Service types)	   | `VENV/bin/poem-syncservtype, poem-syncvo`           |
| Profiles handlers					   | `VENV/bin/poem-exportprofiles, poem-importprofiles` |
| Static data served by Apache | `VENV/usr/share/poem/`                              |
| Main application code        | `VENV/lib/python3.6/site-packages/Poem/`            |
| Log file                     | `VENV/var/log/poem`                                 |
| Path of SQLite database      | `VENV/var/lib/poem/poemserv.db`                     |

If the default location of virtual environment is inappropriate and needs to be changed, change of it should be reflected by adapting `VENV` configuration variable in `etc/poem/poem.conf`, `etc/poem/poem_logging.conf`, `/etc/httpd/conf.d/poem.conf` and `site-packages/Poem/settings.py`.

### Setting up virtual environment based on Python 3.6

CentOS 7 operating system delivers Python 3.6 through [Software Collections service](https://www.softwarecollections.org/en/scls/rhscl/rh-python36/) that is installed with the following instructions:

```sh
yum -y install centos-release-scl
yum -y install scl-utils
yum -y install rh-python36 rh-python36-python-pip rh-python36-python-devel
```

Once the Python 3.6 is installed, it needs to be used to create a new virtual environment named _poem_:

```sh
scl enable rh-python36 'pip install -U pip'
scl enable rh-python36 'pip3 install virtualenv virtualenvwrapper'
export VIRTUALENVWRAPPER_PYTHON=/opt/rh/rh-python36/root/bin/python3.6
source /opt/rh/rh-python36/root/usr/bin/virtualenvwrapper.sh
export WORKON_HOME=/home/pyvenv
mkdir -p $WORKON_HOME
mkvirtualenv poem
```

> **Notice** how the location of virtual environment is controlled with `WORKON_HOME` variable. It needs to be aligned with `VENV` variable in service configuration. 

Afterward, the context of virtual environment can be started:

```sh
workon poem
```

As virtual environment is tied to Python 3.6 versions, it's *advisable* to put `helpers/venv_poem.sh` into `/etc/profile.d` as it will configure login shell automatically.

### Installing the service

Creation and installation of wheel package is done in the context of virtual environment which needs to be loaded prior.

```sh
workon poem
(poem) python setup.py sdist bdist_wheel
(poem) pip3 install dist/*
(poem) pip3 install -r requirements_ext.txt
```
> Installation could take awhile as `mod-wsgi` needs to be compiled and linked against Python 3.6. That is also the reason why some development packages needs to be installed prior like `gcc`, `httpd-devel` and `make`.

wheel package ships cron jobs and Apache configuration and as it is installed in virtual environment, it can **not** actually layout files outside of it meaning that system-wide files should be placed manually:

```sh
(poem) ln -f -s $VIRTUAL_ENV/etc/cron.d/poem-clearsessions /etc/cron.d/
(poem) ln -f -s $VIRTUAL_ENV/etc/cron.d/poem-syncvosf /etc/cron.d/
(poem) ln -f -s $VIRTUAL_ENV/etc/httpd/conf.d/poem.conf /etc/httpd/conf.d/
```

Next, the correct permission needs to be set on virtual environment directory:

```sh
(poem) chown -R apache:apache $VIRTUAL_ENV
```





		



