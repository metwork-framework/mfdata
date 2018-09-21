include ../../../adm/root.mk
include $(MFEXT_HOME)/share/subdir_root.mk

EGG=acquisition-0.0.0-py$(PYTHON_SHORT_VERSION).egg

clean:: pythonclean

all:: $(PREFIX)/opt/python$(METWORK_PYTHON_MODE)/lib/python$(PYTHON_SHORT_VERSION)/site-packages/$(EGG)/acquisition/__init__.py

$(PREFIX)/opt/python$(METWORK_PYTHON_MODE)/lib/python$(PYTHON_SHORT_VERSION)/site-packages/$(EGG)/acquisition/__init__.py:
	python setup.py install --prefix=$(PREFIX)/opt/python$(METWORK_PYTHON_MODE)

test::
	@echo "***** PYTHON TESTS *****"
	flake8.sh --exclude=build .
	find . -name "*.py" ! -path './build/*' -print0 |xargs -0 pylint.sh --errors-only
	cd tests && nosetests$(METWORK_PYTHON_MODE).sh .

coverage::
	cd tests && nosetests.sh --with-coverage --cover-package=acquisition --cover-erase --cover-html --cover-html-dir=coverage .

plop:
	echo $(MFDATA_HOME) $(PREFIX)
