include ../../../adm/root.mk
include $(MFEXT_HOME)/share/subdir_root.mk

EGG_P3=directory_observer-0.0.1-py$(PYTHON3_SHORT_VERSION).egg

clean:: pythonclean

all:: $(PREFIX)/opt/python3/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/$(EGG_P3)

$(PREFIX)/opt/python3/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/$(EGG_P3):
	python3 setup.py install --prefix=$(PREFIX)/opt/python3

test:
	@echo "***** PYTHON3 TESTS *****"
	flake83.sh --exclude=build .

fab:
	layer_wrapper --debug --layers=python3@mfdata -- date

