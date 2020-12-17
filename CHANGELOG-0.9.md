# release_0.9 CHANGELOG

## v0.9.11 (2020-03-05)

- No interesting change

## v0.9.10 (2020-03-04)

### New Features

- add a keep_original_basename in copy/move_to_plugin_step

### Bug Fixes

- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode

## v0.9.9 (2020-01-28)

- No interesting change

## v0.9.8 (2020-01-27)

### New Features

- improve debug logs for switch plugin

## v0.9.7 (2020-01-03)

- No interesting change

## v0.9.6 (2019-12-12)

- No interesting change

## v0.9.5 (2019-11-07)

### New Features

- allow ,;: in directorie/filenames

### Bug Fixes

- fix get_original_basename/dirname behaviour in debug mode

## v0.9.4 (2019-10-30)

- No interesting change

## v0.9.3 (2019-10-29)

### Bug Fixes

- fix failure_policy_move_keep_tags configuration key

## v0.9.2 (2019-10-24)

### New Features

- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step

### Bug Fixes

- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name

## v0.9.1 (2019-10-23)

- No interesting change

## v0.9.0 (2019-10-23)

### New Features

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

### Bug Fixes

- fix logging issue with mqtt_listener in some cases
- fix amqp listener plugin configuration
- important fix about failure_policy_move_keep_tags
- fix some warnings on switch plugin with hardlinking


