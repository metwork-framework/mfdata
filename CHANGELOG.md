<a name="unreleased"></a>
## [Unreleased]

<a name="v0.5.3"></a>
## [v0.5.3] - 2019-01-31

<a name="v0.5.2"></a>
## [v0.5.2] - 2019-01-31

<a name="v0.5.1"></a>
## [v0.5.1] - 2019-01-29

<a name="v0.5.0"></a>
## [v0.5.0] - 2019-01-29
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

