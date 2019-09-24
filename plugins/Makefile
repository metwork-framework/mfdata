include ../adm/root.mk
PLUGINS=ungzip switch debug mqtt_listener amqp_listener unbzip2

all:: $(MFDATA_HOME)/share/plugins

$(MFDATA_HOME)/share/plugins:
	/bin/rm -rf $(MFDATA_HOME)/share/plugins
	mkdir $(MFDATA_HOME)/share/plugins
	for PLUGIN in $(PLUGINS); do cd $${PLUGIN} && export MFMODULE_VERSION=`guess_version.sh` && rm -f *.plugin && make release || exit 1 && mv *.plugin $${MFDATA_HOME}/share/plugins && cd ..; done

clean::
	/bin/rm -rf $(MFDATA_HOME)/share/plugins
	for PLUGIN in $(PLUGINS); do cd $${PLUGIN} && make clean && cd ..; done

