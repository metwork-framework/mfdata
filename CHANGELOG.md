# CHANGELOG


## [Unreleased]

### New Features


### Bug Fixes
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo





## v0.6.1 (2019-04-26)

### New Features
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata


### Bug Fixes
- don't clean nginx upload tmp directory





## v0.6.0 (2019-04-01)

### New Features
- add integration test (plugin create, install, desinstall)
- fix #65 and introduce new configuration options around
- add drop-tags option to move step (and keep-tags* options also)
- remove circus_autostart and autostart plugins in circus config
- add an integration test with injection of a thousand files


### Bug Fixes
- Fix loss of files between plugin switch and plugin ungzip or other
- fix exception function errors when the parameter is an exception object
- both #53 and #61
- dump tags on errors (when in debug mode)
- fix move_or_copy feature when src and dst are not on the same FS
- fix intermittent fails of mfdata integration tests
- fix an integration test
- add garbage_collector.sh call in crontab
- catch some magic exception with some exotic files





