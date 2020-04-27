include ../adm/root.mk

# FIXME: amqp_listener mqtt_listener httpsend ftpsend
PLUGINS=ungzip unbzip2 switch move guess_file_type delete copy archive fork

all:: $(MFDATA_HOME)/share/plugins/.done

$(MFDATA_HOME)/share/plugins/.done:
	mkdir -p $(MFDATA_HOME)/share/plugins
	for PLUGIN in $(PLUGINS); do cd $${PLUGIN} && export MFMODULE_VERSION=`guess_version.sh` && rm -f *.plugin && layer_wrapper --layers=python3@mfext -- make release install || exit 1 && cd ..; done
	touch $@

clean::
	for PLUGIN in $(PLUGINS); do cd $${PLUGIN} && layer_wrapper --layers=python3@mfext -- make clean && cd ..; done

superclean: clean
	rm -Rf $(MFDATA_HOME)/share/plugins
