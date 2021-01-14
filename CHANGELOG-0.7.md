# release_0.7 CHANGELOG

## v0.7.4 (2019-09-05)

### New Features

- first version with only one integration test
- provide a default value for summary key during plugins bootstrap
- Changes in management of layer dependencies and metapackage names
- execute integration tests directly from mfdata module
- add integration test (plugin create, install, desinstall)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- fix #65 and introduce new configuration options around
- add drop-tags option to move step (and keep-tags* options also)
- remove circus_autostart and autostart plugins in circus config
- add an integration test with injection of a thousand files
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata
- add optional mqtt 3.1.1 incoming messages support
- use envtpl new option --reduce-multi-blank-lines
- use template inheritance for mfdata plugins (inspired by mfserv)
- add optional amqp 0.9.1 incoming messages support
- introduce a bunzip2 plugin
- increase default file size limit for plugins
- allow "-" and "." in http receiver
- change the behavior of hardlinks methods to provide atomicity

### Bug Fixes

- add a strong timeout to avoid to block in some cases
- don't start plugins during installation or uninstallation
- fix missing configuration for no_match policy in switch plugin
- fix issues with xattrfile move_or_copy/hardlink_or_copy when source
- fix magic identification at plugin level override
- Fix loss of files between plugin switch and plugin ungzip or other
- fix exception function errors when the parameter is an exception object
- both #53 and #61
- dump tags on errors (when in debug mode)
- fix move_or_copy feature when src and dst are not on the same FS
- fix intermittent fails of mfdata integration tests
- fix an integration test
- add garbage_collector.sh call in crontab
- catch some magic exception with some exotic files
- don't clean nginx upload tmp directory
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)
- create a missing directory during hot reload after a new plugin install
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking

## v0.7.3 (2019-08-29)

### New Features

- first version with only one integration test
- provide a default value for summary key during plugins bootstrap
- Changes in management of layer dependencies and metapackage names
- execute integration tests directly from mfdata module
- add integration test (plugin create, install, desinstall)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- fix #65 and introduce new configuration options around
- add drop-tags option to move step (and keep-tags* options also)
- remove circus_autostart and autostart plugins in circus config
- add an integration test with injection of a thousand files
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata
- add optional mqtt 3.1.1 incoming messages support
- use envtpl new option --reduce-multi-blank-lines
- use template inheritance for mfdata plugins (inspired by mfserv)
- add optional amqp 0.9.1 incoming messages support
- introduce a bunzip2 plugin
- increase default file size limit for plugins
- allow "-" and "." in http receiver
- change the behavior of hardlinks methods to provide atomicity

### Bug Fixes

- add a strong timeout to avoid to block in some cases
- don't start plugins during installation or uninstallation
- fix missing configuration for no_match policy in switch plugin
- fix issues with xattrfile move_or_copy/hardlink_or_copy when source
- fix magic identification at plugin level override
- Fix loss of files between plugin switch and plugin ungzip or other
- fix exception function errors when the parameter is an exception object
- both #53 and #61
- dump tags on errors (when in debug mode)
- fix move_or_copy feature when src and dst are not on the same FS
- fix intermittent fails of mfdata integration tests
- fix an integration test
- add garbage_collector.sh call in crontab
- catch some magic exception with some exotic files
- don't clean nginx upload tmp directory
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)
- create a missing directory during hot reload after a new plugin install
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking

## v0.7.2 (2019-06-13)

### New Features

- first version with only one integration test
- provide a default value for summary key during plugins bootstrap
- Changes in management of layer dependencies and metapackage names
- execute integration tests directly from mfdata module
- add integration test (plugin create, install, desinstall)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- fix #65 and introduce new configuration options around
- add drop-tags option to move step (and keep-tags* options also)
- remove circus_autostart and autostart plugins in circus config
- add an integration test with injection of a thousand files
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata
- add optional mqtt 3.1.1 incoming messages support
- use envtpl new option --reduce-multi-blank-lines
- use template inheritance for mfdata plugins (inspired by mfserv)
- add optional amqp 0.9.1 incoming messages support
- introduce a bunzip2 plugin
- increase default file size limit for plugins
- allow "-" and "." in http receiver
- change the behavior of hardlinks methods to provide atomicity

### Bug Fixes

- add a strong timeout to avoid to block in some cases
- don't start plugins during installation or uninstallation
- fix missing configuration for no_match policy in switch plugin
- fix issues with xattrfile move_or_copy/hardlink_or_copy when source
- fix magic identification at plugin level override
- Fix loss of files between plugin switch and plugin ungzip or other
- fix exception function errors when the parameter is an exception object
- both #53 and #61
- dump tags on errors (when in debug mode)
- fix move_or_copy feature when src and dst are not on the same FS
- fix intermittent fails of mfdata integration tests
- fix an integration test
- add garbage_collector.sh call in crontab
- catch some magic exception with some exotic files
- don't clean nginx upload tmp directory
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)
- create a missing directory during hot reload after a new plugin install
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking

## v0.7.1 (2019-06-12)

### New Features

- first version with only one integration test
- provide a default value for summary key during plugins bootstrap
- Changes in management of layer dependencies and metapackage names
- execute integration tests directly from mfdata module
- add integration test (plugin create, install, desinstall)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- fix #65 and introduce new configuration options around
- add drop-tags option to move step (and keep-tags* options also)
- remove circus_autostart and autostart plugins in circus config
- add an integration test with injection of a thousand files
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata
- add optional mqtt 3.1.1 incoming messages support
- use envtpl new option --reduce-multi-blank-lines
- use template inheritance for mfdata plugins (inspired by mfserv)
- add optional amqp 0.9.1 incoming messages support
- introduce a bunzip2 plugin
- increase default file size limit for plugins
- allow "-" and "." in http receiver
- change the behavior of hardlinks methods to provide atomicity

### Bug Fixes

- add a strong timeout to avoid to block in some cases
- don't start plugins during installation or uninstallation
- fix missing configuration for no_match policy in switch plugin
- fix issues with xattrfile move_or_copy/hardlink_or_copy when source
- fix magic identification at plugin level override
- Fix loss of files between plugin switch and plugin ungzip or other
- fix exception function errors when the parameter is an exception object
- both #53 and #61
- dump tags on errors (when in debug mode)
- fix move_or_copy feature when src and dst are not on the same FS
- fix intermittent fails of mfdata integration tests
- fix an integration test
- add garbage_collector.sh call in crontab
- catch some magic exception with some exotic files
- don't clean nginx upload tmp directory
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)
- create a missing directory during hot reload after a new plugin install
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking

## v0.7.0 (2019-05-24)

### New Features

- first version with only one integration test
- provide a default value for summary key during plugins bootstrap
- Changes in management of layer dependencies and metapackage names
- execute integration tests directly from mfdata module
- add integration test (plugin create, install, desinstall)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- add integration test with png.gz data (test plugins switch, ungzip and bootstrapped archive type plugin)
- fix #65 and introduce new configuration options around
- add drop-tags option to move step (and keep-tags* options also)
- remove circus_autostart and autostart plugins in circus config
- add an integration test with injection of a thousand files
- introduce log management with mfadmin
- add keep-tags and keep-tags-suffix when failure-policy is move
- port redis_service feature of mfserv to mfdata
- add missing initialization and description of some atributes
- incase of failure during failure policy, delete file and tags
- port "extra_daemon" feature from mfserv to mfdata
- add optional mqtt 3.1.1 incoming messages support
- use envtpl new option --reduce-multi-blank-lines
- use template inheritance for mfdata plugins (inspired by mfserv)
- add optional amqp 0.9.1 incoming messages support
- introduce a bunzip2 plugin
- increase default file size limit for plugins
- allow "-" and "." in http receiver
- change the behavior of hardlinks methods to provide atomicity

### Bug Fixes

- add a strong timeout to avoid to block in some cases
- don't start plugins during installation or uninstallation
- fix missing configuration for no_match policy in switch plugin
- fix issues with xattrfile move_or_copy/hardlink_or_copy when source
- fix magic identification at plugin level override
- Fix loss of files between plugin switch and plugin ungzip or other
- fix exception function errors when the parameter is an exception object
- both #53 and #61
- dump tags on errors (when in debug mode)
- fix move_or_copy feature when src and dst are not on the same FS
- fix intermittent fails of mfdata integration tests
- fix an integration test
- add garbage_collector.sh call in crontab
- catch some magic exception with some exotic files
- don't clean nginx upload tmp directory
- fix building issues with proxy
- fix issue 'bad magic file in a plugin can break the switch plugin'
- fix typo
- fix bug CHANGELOGS not generated when CHANGELOGS.md doesn't exist (for the first time)
- create a missing directory during hot reload after a new plugin install
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking


