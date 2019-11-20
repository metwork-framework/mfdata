CONFIGS=config.ini directory_observer.ini redis.conf nginx.conf content_by_lua.lua mflog_override.conf redis_plugin_xxx.conf

include ../adm/root.mk
include $(MFEXT_HOME)/share/subdir_root.mk
include $(MFEXT_HOME)/share/config_subdir.mk

test:
	layer_wrapper --layers=devtools@mfext noutf8.sh

all:: $(MFMODULE_HOME)/config/circus.ini $(MFMODULE_HOME)/config/telegraf.conf $(MFMODULE_HOME)/config/content_by_lua.lua

$(MFMODULE_HOME)/config/content_by_lua.lua: content_by_lua.lua
	layer_wrapper --layers=devtools@mfext -- test_globals_in_lua.sh $<
	cp -f $< $@
