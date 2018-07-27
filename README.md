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
% yum -y install ca-certificates \
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
% yum -y install centos-release-scl
% yum -y install scl-utils
% yum -y install rh-python36 rh-python36-python-pip rh-python36-python-devel
```

Once the Python 3.6 is installed, it needs to be used to create a new virtual environment named _poem_:

```sh
% scl enable rh-python36 'pip install -U pip'
% scl enable rh-python36 'pip3 install virtualenv virtualenvwrapper'
% scl enable rh-python36 'export VIRTUALENVWRAPPER_PYTHON=/opt/rh/rh-python36/root/bin/python3.6; source /opt/rh/rh-python36/root/usr/bin/virtualenvwrapper.sh; export WORKON_HOME=/home/pyvenv; mkdir -p $WORKON_HOME; mkvirtualenv poem'
```

> **Notice** how the location of virtual environment is controlled with `WORKON_HOME` variable. Created virtual environment directory will be `$WORKON_HOME/poem`. It needs to be aligned with `VENV` variable in service configuration. 


Afterward, the context of virtual environment can be started:

```sh
% workon poem
```

As virtual environment is tied to Python 3.6 versions, it's *advisable* to put `helpers/venv_poem.sh` into `/etc/profile.d` as it will configure login shell automatically.

### Installing the service

Creation and installation of wheel package is done in the context of virtual environment which needs to be loaded prior.

```sh
% workon poem
% (poem) python setup.py sdist bdist_wheel
% (poem) pip3 install dist/*
% (poem) pip3 install -r requirements_ext.txt
```
> Installation could take awhile as `mod-wsgi` needs to be compiled and linked against Python 3.6. That is also the reason why some development packages needs to be installed prior like `gcc`, `httpd-devel` and `make`.

wheel package ships cron jobs and Apache configuration and as it is installed in virtual environment, it can **not** actually layout files outside of it meaning that system-wide files should be placed manually:

```sh
% (poem) ln -f -s $VIRTUAL_ENV/etc/cron.d/poem-clearsessions /etc/cron.d/
% (poem) ln -f -s $VIRTUAL_ENV/etc/cron.d/poem-syncvosf /etc/cron.d/
% (poem) ln -f -s $VIRTUAL_ENV/etc/httpd/conf.d/poem.conf /etc/httpd/conf.d/
```

Next, the correct permission needs to be set on virtual environment directory:

```sh
% (poem) chown -R apache:apache $VIRTUAL_ENV
```

## Configuration

Configuration is centered around one file `VENV/etc/poem/poem.conf` that is splitted into several sections, `[DEFAULT]`, `[GENERAL]`, `[SUPERUSER]`, `[SYNC]`, `[SECURITY]`.

### DEFAULT

	[DEFAULT]
	VENV = /home/pyvenv/poem/

* `VENV` defines the location of virtual environment directory. Value will be interpolated into the other options.

### GENERAL

	[GENERAL]
	Namespace = hr.cro-ngi.TEST
	Debug = False
	TimeZone = Europe/Zagreb
	SamlLoginString = Log in using EGI CHECK-IN

* `Namespace` defines the identifiter that will prepended to every Profile
* `Debug` serves for the debugging purposes and tells Django to be verbosive and list the stack calls in case of errors
* `Timezone` timezone
* `SamlLoginString` define the text presented on the SAML2 button of login page

### SUPERUSER

Initial superuser credentials that can be used to sign in to POEM with username and password.

	[SUPERUSER]
	Name = test 
	Password = test
	Email = test@foo.baar

> It **important** to note that these options should be specified with correct values **before** trying to create database. 

### SYNC

These control options are used by sync scripts that fetch all available services types from GOCDB-like service and Virtual organizations from Operations portal. Additionally, if GOCDB-like service supports only Basic HTTP Authentication, it should be enabled by setting `UsePlainHttpAuth` and specifying credentials in `HttpUser` and `HttpPass`. 

	[SYNC]
	UsePlainHttpAuth = False 
	HttpUser = xxxx
	HttpPass = xxxx
	ServiceType = https://goc.egi.eu/gocdbpi/private/?method=get_service_types 
	VO = http://operations-portal.egi.eu/xml/voIDCard/public/all/true

### SECURITY

	[SECURITY]
	AllowedHosts = FQDN1, FQDN2
	CAFile = /etc/pki/tls/certs/DigiCertCA.crt
	CAPath = /etc/grid-security/certificates/
	HostCert = /etc/grid-security/hostcert.pem
	HostKey = /etc/grid-security/hostkey.pem
	SecretKeyPath = %(VENV)s/etc/poem/secret_key

* `AllowedHosts` should have FQDN name of hosts that will be running POEM service. It can be provided as comma separated list of valid FQDNs and it is used as prevention of HTTP Host Header attacks. FQDNs listed here will be matched against request's Host header exactly.
* `CAFile`, `CAPath` are used by sync scripts to authenticate the server certificate
* `HostCert`, `HostKey` are public and private part of client certificate
* `SecretKeyPath` is the location of file containing Django SECRET_KEY that is used for cryptographic signing
	* `poem-genseckey` provided tool can generate unique and unpredictable value and write it into the file
```sh
% workon poem
% poem-genseckey -f $VIRTUAL_ENV/etc/poem/secret_key
```

### Creating database and starting the service

Prerequisites for creating the empty database are:
1) `[SUPERUSER]` section is set with desired credentials
2) `SECRET_KEY` is generated and placed in `$VIRTUAL_ENV/etc/poem/secret_key`
3) `$VIRTUAL_ENV` has permissions set to `apache:apache`
4) `poem.conf` Apache configuration is presented in `/etc/httpd/conf.d/`

Once all is set, database can be created with provided tool `poem-db`:

```sh
% workon poem
% poem-db -c
Operations to perform:
	Apply all migrations: admin, auth, contenttypes, poem, reversion, sessions
Running migrations:
	Applying contenttypes.0001_initial... OK
	Applying contenttypes.0002_remove_content_type_name... OK
	Applying auth.0001_initial... OK
	Applying auth.0002_alter_permission_name_max_length... OK
	Applying auth.0003_alter_user_email_max_length... OK
	Applying auth.0004_alter_user_username_opts... OK
	Applying auth.0005_alter_user_last_login_null... OK
	Applying auth.0006_require_contenttypes_0002... OK
	Applying auth.0007_alter_validators_add_error_messages... OK
	Applying auth.0008_alter_user_username_max_length... OK
	Applying auth.0009_alter_user_last_name_max_length... OK
	Applying poem.0001_initial... OK
	Applying admin.0001_initial... OK
	Applying admin.0002_logentry_remove_auto_add... OK
	Applying reversion.0001_squashed_0004_auto_20160611_1202... OK
	Applying poem.0002_extrev_add... OK
	Applying reversion.0003_reversion_updates... OK
	Applying poem.0004_reversion_dbfill... OK
	Applying sessions.0001_initial... OK
Superuser created successfully.
Installed 3 object(s) from 1 fixture(s)
```

Afterward, Apache server needs to be started:
```sh
% systemctl start httpd.service
```

POEM web application should be now served at https://fqdn/poem
