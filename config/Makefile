CONFIGS=config.ini directory_observer.ini redis.conf nginx.conf content_by_lua.lua mflog_override.conf

include ../adm/root.mk
include $(MFEXT_HOME)/share/subdir_root.mk
include $(MFCOM_HOME)/share/config_subdir.mk

test:
	layer_wrapper --layers=devtools@mfext noutf8.sh

all:: $(MODULE_HOME)/config/circus.ini $(MODULE_HOME)/config/telegraf.conf $(MODULE_HOME)/config/content_by_lua.lua

$(MODULE_HOME)/config/content_by_lua.lua: content_by_lua.lua
	layer_wrapper --layers=devtools@mfext -- test_globals_in_lua.sh $<
	cp -f $< $@
