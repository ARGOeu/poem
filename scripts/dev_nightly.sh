#!/usr/bin/env bash

# poem
#
# SVN nightly build
#

SVN_PATH=http://svn.cern.ch/guest/sam/trunk/poem
BUILD_PATH=/tmp

# Activate virtualenv 
# build will fail if you have your app in site-packages due to 
# pythonpath problem
#source /opt/django_1.1_py24/bin/activate

cd ${BUILD_PATH}
svn co $SVN_PATH || exit 1

# disable custom SQL 
rm -f $BUILD_PATH/poem/poem/Poem/poem/sql/profile.sql || exit 1
rm -f $BUILD_PATH/poem/poem_sync/Poem_sync/poem_sync/sql/schema_details.sql || exit 1


nightly_build () {

	if [ -a /etc/poem_test/poem.ini ]; then
		rm -f /etc/poem_test/poem.ini
	fi

	ln -s /etc/poem_test/poem_mysql.ini /etc/poem_test/poem.ini

	cd ${APP_PATH}

	/bin/sed -i "s|CONFIG_FILE = '.*'|CONFIG_FILE = '/etc/poem_test/poem.ini'|g" settings.py
	# remove once UP-22 metric mapping workaround is no longer needed
	/bin/sed -i "s|'Poem.poem',|'Poem.poem','Poem_sync.poem_sync',|g" settings.py


	python manage.py test --verbosity=2 $APP_NAME 2>/tmp/test.log

	if [ $? -ne 0 ]; then
	   mail -v -s 'poem nightly build test' marian.babik@cern.ch < /tmp/test.log
	   rm -rf /tmp/poem
	   exit 1
	fi

	if [ -a /etc/poem_test/poem.ini ]; then
		rm -f /etc/poem_test/poem.ini
	fi

	ln -s /etc/poem_test/poem_oracle.ini /etc/poem_test/poem.ini

	cd ${APP_PATH}

	python manage.py test --settings=settings_dev --verbosity=2 $APP_NAME 2>/tmp/test.log
	if [ $? -ne 0 ]; then
	   mail -v -s 'poem nightly build test' marian.babik@cern.ch < /tmp/test.log
	   mail -v -s 'poem nightly build test' vaibhav.kumar@cern.ch < /tmp/test.log
	   rm -rf /tmp/poem
	   exit 1
	fi

	figleaf2html  /tmp/figleaf -d /tmp/coverage_$APP_NAME

}

APP_PATH=${BUILD_PATH}/poem/poem/Poem/
APP_NAME=poem
# POEM depends on POEM-SYNC to read Metric Mappings (UP-22 only)
export PYTHONPATH=${BUILD_PATH}/poem/poem:${BUILD_PATH}/poem/poem_sync

nightly_build

APP_PATH=${BUILD_PATH}/poem/poem_sync/Poem_sync/
APP_NAME=poem_sync
export PYTHONPATH=${BUILD_PATH}/poem/poem_sync

nightly_build

# cleanup
rm -rf /tmp/poem
