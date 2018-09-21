include ../adm/root.mk
include $(MFEXT_HOME)/share/subdir_root.mk

SUBDIRS=$(shell ls -d layer*)
TESTDIRS=layer1_python3/0200_xattrfile layer1_python3/0300_acquisition

all::
	@for SUBDIR in $(SUBDIRS); do OLDPWD=`pwd`; cd $$SUBDIR || exit 1; $(MAKE) all || exit 1; cd $${OLDPWD}; done

clean::
	@for SUBDIR in $(SUBDIRS); do OLDPWD=`pwd`; cd $$SUBDIR || exit 1; $(MAKE) clean || exit 1; cd $${OLDPWD}; done

test::
	echo $(SUBDIRS)
	echo $(TESTDIRS)
	@for SUBDIR in $(TESTDIRS); do OLDPWD=`pwd`; cd $$SUBDIR || exit 1; $(MAKE) test || exit 1; cd $${OLDPWD}; done

coverage::
	@for SUBDIR in $(TESTDIRS); do OLDPWD=`pwd`; cd $$SUBDIR || exit 1; $(MAKE) coverage || exit 1; cd $${OLDPWD}; done

doc:
	@for SUBDIR in $(SUBDIRS); do OLDPWD=`pwd`; cd $$SUBDIR || exit 1; $(MAKE) doc || exit 1; cd $${OLDPWD}; done
