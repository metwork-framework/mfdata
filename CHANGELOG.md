<a name="unreleased"></a>
## [Unreleased]

### Docs
- Update MFDATA documentation
- Update MFDATA documentation + add "Edit on GitHub"

### Fix
- catch some magic exception with some exotic files

<a name="v0.6.0"></a>
## [v0.6.0] - 2019-04-01
### Docs
- update MFDATA documentation
- update MFDATA tutorials
- we prefer to keep a specific list of what we copy to doc

### Feat
- add an integration test with injection of a thousand files
- add drop-tags option to move step (and keep-tags* options also)
- add integration test (plugin create, install, desinstall)
- fix [#65](https://github.com/metwork-framework//issues/65) and introduce new configuration options around
- remove circus_autostart and autostart plugins in circus config

### Fix
- Fix loss of files between plugin switch and plugin ungzip or other mfdata plugins The test test_14_move_or_copy2 is broken, we temporarily skip it
- add garbage_collector.sh call in crontab
- both [#53](https://github.com/metwork-framework//issues/53) and [#61](https://github.com/metwork-framework//issues/61)
- catch some magic exception with some exotic files
- dump tags on errors (when in debug mode)
- fix an integration test
- fix exception function errors when the parameter is an exception object rather than a string
- fix intermittent fails of mfdata integration tests
- fix move_or_copy feature when src and dst are not on the same FS

<a name="v0.5.8"></a>
## [v0.5.8] - 2019-03-22
### Fix
- fix move_or_copy feature when src and dst are not on the same FS

<a name="v0.5.7"></a>
## [v0.5.7] - 2019-03-15
### Feat
- add drop-tags option to move step (and keep-tags* options also)

### Fix
- Fix loss of files between plugin switch and plugin ungzip or other mfdata plugins The test test_14_move_or_copy2 is broken, we temporarily skip it
- both [#53](https://github.com/metwork-framework//issues/53) and [#61](https://github.com/metwork-framework//issues/61)

<a name="tag_doc"></a>
## [tag_doc] - 2019-03-12
### Feat
- add integration test (plugin create, install, desinstall)
- fix [#65](https://github.com/metwork-framework//issues/65) and introduce new configuration options around

### Fix
- Fix loss of files between plugin switch and plugin ungzip or other mfdata plugins The test test_14_move_or_copy2 is broken, we temporarily skip it
- both [#53](https://github.com/metwork-framework//issues/53) and [#61](https://github.com/metwork-framework//issues/61)
- dump tags on errors (when in debug mode)
- fix exception function errors when the parameter is an exception object rather than a string
- fix move_or_copy feature when src and dst are not on the same FS

<a name="v0.5.6"></a>
## [v0.5.6] - 2019-03-04
### Fix
- both [#53](https://github.com/metwork-framework//issues/53) and [#61](https://github.com/metwork-framework//issues/61)

<a name="v0.5.5"></a>
## [v0.5.5] - 2019-02-15
### Fix
- Fix loss of files between plugin switch and plugin ungzip or other mfdata plugins The test test_14_move_or_copy2 is broken, we temporarily skip it

<a name="v0.5.4"></a>
## [v0.5.4] - 2019-02-06

<a name="v0.5.3"></a>
## [v0.5.3] - 2019-01-31

<a name="v0.5.2"></a>
## [v0.5.2] - 2019-01-31

<a name="v0.5.0"></a>
## [v0.5.0] - 2019-01-29

<a name="v0.5.1"></a>
## [v0.5.1] - 2019-01-29
### Feat
- Changes in management of layer dependencies and metapackage names (only minimal and full) Associated with changes in mfext _metwork.spec, this reduces the number of layers installed by default when installing mfdata (only necessary mfext layers are installed) Metapackage metwork-mfdata-minimal only installs the necessary layers for mfdata to work properly Metapackage metwork-mfdata or metwork-mfserv-full installs all mfdata layers
- execute integration tests directly from mfdata module and lauch them on a pull request on the module
- provide a default value for summary key during plugins bootstrap

<a name="v0.4.1"></a>
## [v0.4.1] - 2019-01-09

<a name="v0.4.0"></a>
## [v0.4.0] - 2019-01-08
### Feat
- change default configuration
- first version with only one integration test (mfdata.start/status/stop is working)

### Fix
- add a strong timeout to avoid to block in some cases
- don't start plugins during installation or uninstallation
- fix issues with xattrfile move_or_copy/hardlink_or_copy when source and destination are not in the same FS
- fix magic identification at plugin level override
- fix missing configuration for no_match policy in switch plugin

### BREAKING CHANGE

no admin module configured by default

