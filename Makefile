
sources:
	python setup.py sdist
	cp dist/*.tar.gz .
rpm: sources
	rpmbuild -ba --define "_sourcedir ${PWD}" poem.spec