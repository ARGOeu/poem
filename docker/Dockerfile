FROM centos:7
MAINTAINER dvrcic@srce.hr 
COPY EGI-trustanchors.repo /etc/yum.repos.d/
RUN yum -y makecache; yum -y update; yum clean all
RUN yum -y install epel-release && \
    yum -y install \
      ca-certificates \
      git \
      unzip \
      psmisc \
      which
RUN yum -y install \
      centos-release-scl \
      cronie \
      crontabs \
      scl-utils \
      xmlsec1 \
      xmlsec1-openssl
RUN yum -y makecache && yum -y install \
      rh-python36-python-pip \
			rh-python36-mod_wsgi \
      httpd24-mod_ssl
RUN scl enable rh-python36 'pip install -U pip' && \
    scl enable rh-python36 'pip3 install virtualenv virtualenvwrapper'
COPY venv_poem.sh /etc/profile.d/
RUN scl enable rh-python36 'source /etc/profile.d/venv_poem.sh; \
    mkdir -p $WORKON_HOME; \
    mkvirtualenv poem'      
ADD https://github.com/vrdel/poem/archive/devel.zip poem-devel.zip
RUN unzip poem-devel.zip
WORKDIR poem-devel
RUN source /etc/profile.d/venv_poem.sh; \
    workon poem; \
    python setup.py egg_info --tag-date sdist bdist_wheel; \
    pip3 install dist/*; \
    pip3 install -r requirements_ext.txt 
RUN yum -y install ca-policy-egi-core 
ADD hostcert.pem hostkey.pem /etc/grid-security/
COPY DigiCertCA.crt /etc/pki/tls/certs/
WORKDIR /root
COPY poem.conf ./ 
COPY *.sh ./
RUN ./setup.sh
