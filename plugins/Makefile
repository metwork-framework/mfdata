include ../adm/root.mk

PLUGINS=ungzip unbzip2 switch move guess_file_type delete copy archive fork httpsend sftpsend ftpsend mqttlistener amqplistener

all:: $(MFDATA_HOME)/share/plugins/.done

$(MFDATA_HOME)/share/plugins/.done:
	mkdir -p $(MFDATA_HOME)/share/plugins
	for PLUGIN in $(PLUGINS); do cd $${PLUGIN} && export MFMODULE_VERSION=`guess_version.sh` && rm -f *.plugin && $(MFMODULE_HOME)/bin/mfdata_wrapper make release install || exit 1 && cd ..; done
	touch $@

clean::
	for PLUGIN in $(PLUGINS); do cd $${PLUGIN} && $(MFMODULE_HOME)/bin/mfdata_wrapper make clean && cd ..; done

superclean: clean
	rm -Rf $(MFDATA_HOME)/share/plugins
