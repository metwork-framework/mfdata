# release_0.6 CHANGELOG



## v0.6.1 (2019-04-26)

### New Features


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





