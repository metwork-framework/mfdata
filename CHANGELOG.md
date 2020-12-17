# release_1.0 CHANGELOG

## v1.0.3 (2020-11-13)

### Bug Fixes

- fix missing file in listener template (bp #360) (#361)

## v1.0.2 (2020-11-03)

### Bug Fixes

- self._consumer.on_message is not set after exception (bp #338) (#340)
- remove old parameters about AMQP/MQTT from the module configuration file (bp #336) (#337)
- fix multiple steps targets with switch plugin (bp #352) (#353)

## v1.0.1 (2020-09-26)

### New Features

- load the pythonX_scientific_core layer by default in plugins (if the layer is installed) (bp #331) (#332)

## v1.0.0 (2020-09-19)

### New Features

- allow "-" and "." in http receiver
- introduce acquisition decorators for gunzip and bunzip2
- change the behavior of hardlinks methods to provide atomicity
- add getuid() method and better getsite() error reporting
- add metrics to reinject step
- allow ,;: in directorie/filenames
- adaptation to removal of layer misc@mfext
- log refactoring
- improve debug logs for switch plugin
- remove absolute log paths from log_proxy usages (LOGPROXY_LOG_DIRECTORY env variable is used by default)
- allow empty nginx uploads
- add httpsend plugin template
- add a keep_original_basename in copy/move_to_plugin_step
- The number of processes of the switch plugin is now configurable (default is 1)
- add strftime placeholders for httpsend plugin
- remove all references to MFCOM or mfcom, including backward compatibility stuff
- remove xattrfile (moved in a dedicated repo)
- new plugin system
- allow binary packages with pip by default for plugins
- add python switch rule
- preparing issue227
- remove acquisition (now in a specific repository)
- remove directory_observer (now in a dedicated repository)
- add psycopg2 usability (by loading of optional layer python3_scientific_core@mfext)
- support multiple switch instances (and doc)

### Bug Fixes

- fix issues with hardlinking when incoming files come with another uid
- fix default value for step_name
- fix failure_policy_move_keep_tags configuration key
- fix get_original_basename/dirname behaviour in debug mode
- remove rlimit_core (because of `ulimit -c 0` in mfext)
- fix typo in configuration key for amqp (topic mode)
- fix bug in amqp topic mode
- fix syslog nginx conf
- typo in .releaseignore file


