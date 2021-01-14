# release_0.8 CHANGELOG

## v0.8.6 (2019-10-25)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)

## v0.8.5 (2019-10-22)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)

## v0.8.4 (2019-09-22)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)

## v0.8.3 (2019-09-05)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)

## v0.8.2 (2019-08-29)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)

## v0.8.1 (2019-08-26)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)

## v0.8.0 (2019-08-14)

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
- add some optional dependencies for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- increase default file size limit for plugins
- introduce better error reporting
- add new options for switch plugin
- build mfdata without mfcom (mfcom layers are now included in mfext)
- refactor around #154 issue
- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- improve debug logs for switch plugin
- add a keep_original_basename in copy/move_to_plugin_step

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
- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking
- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix decorators with failure policy (#378)


