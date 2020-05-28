PWD=$(shell pwd)
PLUGIN_NAME=$(shell basename $(PWD))

precustom:: config.ini .layerapi2_label .layerapi2_dependencies .releaseignore .plugin_format_version .gitignore .autorestart_includes .autorestart_excludes

templates/config.ini: ../../adm/templates/plugins/_common/config.ini
	@if ! test -d templates; then mkdir -p templates; fi
	cat $< |sed 's/cookiecutter\.//g' >$@

config.ini: config.ini.custom templates/config.ini
	export one_line_summary="$(SUMMARY)" ; export PLUGIN_NAME="$(PLUGIN_NAME)" ; cat $< |envtpl --reduce-multi-blank-lines --search-paths=.,.. >$@ || ( rm -f $@ ; exit 1 )

.layerapi2_label:
	echo "plugin_$(PLUGIN_NAME)@mfdata" >$@

.layerapi2_dependencies: ../../adm/templates/plugins/python3/{{cookiecutter.name}}/.layerapi2_dependencies
	cp -f $< $@

.releaseignore: ../../adm/templates/plugins/_common/.releaseignore
	cp -f $< $@
	echo "config.ini.custom" >>$@
	echo "templates" >>$@

.gitignore:
	echo "config.ini" >$@
	echo "templates" >>$@
	echo ".layerapi2_label" >>$@
	echo ".releaseignore" >>$@
	echo ".plugin_format_version" >>$@
	echo ".autorestart_includes" >>$@
	echo ".autorestart_excludes" >>$@
	echo "python3_virtualenv_sources/src" >>$@
	echo "python2_virtualenv_sources/src" >>$@
	echo "local" >>$@

.autorestart_includes: ../../adm/templates/plugins/_common/autorestart_includes
	cp -f $< $@

.autorestart_excludes: ../../adm/templates/plugins/_common/autorestart_excludes
	cp -f $< $@

clean::
	rm -Rf templates
	rm -f config.ini
	rm -f .layerapi2_label
	rm -f .releaseignore
	rm -f .plugin_format_version
	rm -f .autorestart_includes
	rm -f .autorestart_excludes

deploy: clean release install
	P=`ls -rt *.plugin |tail -1`; if test "$${P}" != ""; then if test -f "$${P}"; then plugins.install --force "$${P}"; fi; fi

install:
	@mkdir -p "$(MFDATA_HOME)/share/plugins"
	cp -f *.plugin "$(MFDATA_HOME)/share/plugins/"
