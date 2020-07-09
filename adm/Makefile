BINS=before_start_directory_observer garbage_collector.sh _make_directory_observer_conf _make_circus_conf _make_and_write_switch_confs before_start_step.switch.main mfdata_conf_monitor.py redis_metwork.py telegraf_collector_var_in_files_count.py _directory_observer.stop _switch.stop _make_nginx_conf generate_random_files.py _check_circus_conf _plugins.postinstall _install_or_update_configured_plugins.py

include root.mk
include $(MFEXT_HOME)/share/subdir_root.mk
include $(MFEXT_HOME)/share/startup_scripts_profiles.mk

TEMPLATES=$(shell find templates ! -type d)
TARGET_TEMPLATES:=$(addprefix $(PREFIX)/share/,$(TEMPLATES))

all:: profiles $(PREFIX)/bin/cronwrap.sh $(PREFIX)/bin/mfdata.status $(PREFIX)/bin/mfdata.start $(PREFIX)/bin/mfdata.stop $(PREFIX)/bin/mfdata.init $(TARGET_TEMPLATES) load_env noutf8_check $(PREFIX)/bin/mfdata.autorestart $(PREFIX)/lib/mfdata/__init__.py $(PREFIX)/lib/mfdata/plugins.py

noutf8_check:
	cd templates && layer_wrapper --layers=devtools@mfext noutf8.sh

$(PREFIX)/lib/mfdata/__init__.py:
	mkdir -p $(PREFIX)/lib/mfdata
	touch $@

$(PREFIX)/lib/mfdata/plugins.py: plugins.py
	cp -f $< $@
