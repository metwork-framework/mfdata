PWD=$(shell pwd)
PLUGIN_NAME=$(shell basename $(PWD))

precustom:: config.ini .layerapi2_label .layerapi2_dependencies .release_ignore .plugin_format_version .gitignore

templates/config.ini: ../../adm/templates/plugins/_common/config.ini
	@if ! test -d templates; then mkdir -p templates; fi
	cat $< |sed 's/cookiecutter\.//g' >$@


config.ini: config.ini.custom templates/config.ini
	export one_line_summary="$(SUMMARY)" ; export PLUGIN_NAME="$(PLUGIN_NAME)" ; cat $< |envtpl --reduce-multi-blank-lines --search-paths=.,.. >$@ || ( rm -f $@ ; exit 1 )

.layerapi2_label:
	echo "plugin_$(PLUGIN_NAME)@mfdata" >$@

.layerapi2_dependencies: ../../adm/templates/plugins/python3/{{cookiecutter.name}}/.layerapi2_dependencies
	cp -f $< $@

.release_ignore: ../../adm/templates/plugins/_common/.release_ignore
	cp -f $< $@
	echo "config.ini.custom" >>$@
	echo "templates" >>$@

.gitignore:
	echo "config.ini" >$@
	echo "templates" >>$@
	echo ".layerapi2_label" >>$@
	echo ".release_ignore" >>$@
	echo ".plugin_format_version" >>$@

clean::
	rm -Rf templates
	rm -f config.ini
	rm -f .layerapi2_label
	rm -f .release_ignore
	rm -f .plugin_format_version
