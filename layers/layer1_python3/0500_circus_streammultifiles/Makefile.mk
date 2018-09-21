include ../../../adm/root.mk
include $(MFEXT_HOME)/share/subdir_root.mk

EGG_P3=circus_streammultifiles-0.0.0-py$(PYTHON3_SHORT_VERSION).egg

clean:: pythonclean

all:: $(PREFIX)/opt/python3/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/$(EGG_P3)

$(PREFIX)/opt/python3/lib/python$(PYTHON3_SHORT_VERSION)/site-packages/$(EGG_P3):
	python3 setup.py install --prefix=$(PREFIX)/opt/python3

test:
	@echo "***** PYTHON3 TESTS *****"
	layer_wrapper --layers=python3_circus@mfext -- flake83.sh --exclude=build .
	find . -name "*.py" ! -path './build/*' -print0 |xargs -0 layer_wrapper --layers=python3_circus@mfext -- pylint3.sh --errors-only
