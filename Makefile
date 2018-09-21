MODULE=MFDATA
MODULE_LOWERCASE=mfdata

-include adm/root.mk
-include $(MFEXT_HOME)/share/main_root.mk

DIRS=config bin opt/python2/lib/python$(PYTHON2_SHORT_VERSION)/site-packages opt/python3/lib/python$(PYTHON3_SHORT_VERSION)/site-packages share

all:: directories
	echo "root@mfcom" >$(MFDATA_HOME)/.layerapi2_dependencies
	echo "openresty@mfext" >>$(MFDATA_HOME)/.layerapi2_dependencies
	cd adm && $(MAKE)
	cd config && $(MAKE)
	cd layers && $(MAKE)
	cd plugins && $(MAKE)

clean::
	cd config && $(MAKE) clean
	cd adm && $(MAKE) clean
	cd plugins && $(MAKE) clean
	cd layers && $(MAKE) clean

directories:
	@for DIR in $(DIRS); do mkdir -p $(MFDATA_HOME)/$$DIR; done

test::
	cd layers && $(MAKE) test
	cd config && $(MAKE) test

coverage::
	cd layers && $(MAKE) coverage
