<a name="unreleased"></a>
## [Unreleased]

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

