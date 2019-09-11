SPHINXOPTS    =
SPHINXBUILD   = $(MFEXT_HOME)/opt/devtools/bin/sphinx_wrapper
SPHINXPROJ    = mfext
SOURCEDIR     = .
BUILDDIR      = _build

RST_FILES=$(shell ls *.md 2>/dev/null |grep -v tempo.md |sed 's/\.md$$/\.rst/g')
COMMON_DOCFILES=$(shell cd ../.metwork-framework && ls configure_a_metwork_package.md README.md installation_guide.md components.md 2>/dev/null |sed 's/\.md$$/\.rst/g')
CHANGELOGS_FILES=$(shell cd .. && ls CHANGELOG.md 2>/dev/null |sed 's/\.md$$/\.rst/g' && ls -r CHANGELOG-*.md 2>/dev/null |sed 's/\.md$$/\.rst/g')
CHANGELOGS_RST_TMPL=changelogs.tmpl
CHANGELOGS_RST_FILE=changelogs.rst

.PHONY: help clean html before_html

plop:
	echo $(CHANGELOGS_FILES)

help:
	@echo "ERROR: use 'make doc' in the parent directory or"
	@echo "       (if you know what your are doing) 'make html' here"

layer_root_custom.rst: layer_root_custom.md
	true

%.rst: %.md
	rm -f tempo.md
	echo ".. GENERATED FILE, DO NOT EDIT (edit $< instead)" >tempo.md
	echo ":original_file: $<" >>tempo.md
	echo >>tempo.md
	cat $< |envtpl --reduce-multi-blank-lines >>tempo.md
	layer_wrapper --layers=python3_devtools@mfext -- m2r --overwrite tempo.md
	cat tempo.rst >$@
	rm -f tempo.md

html:: $(CHANGELOGS_FILES) $(COMMON_DOCFILES) $(RST_FILES) before_html
	rm -f tempo.*
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

before_html:
	@true

clean::
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	rm -f tempo.*
	rm -f components.*
	rm -f layer_*.rst
	rm -f tempo.*
	rm -f *.mdtemp
	rm -f /tmp/layer_root_custom.md
	cp -f layer_root_custom.md /tmp 2>/dev/null || true
	rm -f layer_*.md
	cp /tmp/layer_root_custom.md . 2>/dev/null || true
	rm -f layer_*.rst
	rm -f configure_a_metwork_package*
	rm -f installation_guide*
	rm -f CHANGELOG*.{md,rst}
	rm -f changelogs.rst
	rm -f layerapi2.rst
	rm -f layers.md
	rm -f README.{md,rst}

README.md: ../.metwork-framework/README.md
	cp -f $< $@

configure_a_metwork_package.md: ../.metwork-framework/configure_a_metwork_package.md
	cp -f $< $@

installation_guide.md: ../.metwork-framework/installation_guide.md
	cp -f $< $@

components.md:
	echo "# Full list of components" >$@
	layer_wrapper --layers=python3_devtools@mfext -- _yaml_to_md.py ALL >>$@

CHANGELOG-%.md: ../CHANGELOG-%.md
	cp -f $< $@
	echo "   $(shell echo "$<" |awk -F '/' '{print $$2;}' |sed 's/\.md$$//g')" >>$(CHANGELOGS_RST_FILE)

CHANGELOG.md: ../CHANGELOG.md
	cp -f $< $@
	cat ${CHANGELOGS_RST_TMPL} >$(CHANGELOGS_RST_FILE)
	echo "   $(shell echo "$<" |awk -F '/' '{print $$2;}' |sed 's/\.md$$//g')" >>$(CHANGELOGS_RST_FILE)
