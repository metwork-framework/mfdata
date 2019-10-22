# release_0.9 CHANGELOG


## [Unreleased]

### New Features
- allow "-" and "." in http receiver
- refactor around #154 issue
- build mfdata without mfcom (mfcom layers are now included in mfext)
- add new options for switch plugin
- introduce better error reporting
- increase default file size limit for plugins
- replace MODULE* environment variables names by MFMODULE* (MODULE_HOME becomes MFMODULE_HOME and so on)
- add some optional dependencies for plugins
- introduce a bunzip2 plugin


### Bug Fixes
- fix some warnings on switch plugin with hardlinking
- important fix about failure_policy_move_keep_tags
- fix amqp listener plugin configuration
- fix logging issue with mqtt_listener in some cases





