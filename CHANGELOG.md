# release_0.9 CHANGELOG



## v0.9.2 (2019-10-24)

### New Features
- change the behavior of hardlinks methods to provide atomicity
- add metrics to reinject step
- add getuid() method and better getsite() error reporting


### Bug Fixes
- fix default value for step_name
- fix issues with hardlinking when incoming files come with another uid





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





