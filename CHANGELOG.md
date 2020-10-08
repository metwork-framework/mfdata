# CHANGELOG


## [Unreleased]

### New Features
- load the pythonX_scientific_core layer by default in plugins (if the layer is installed) (#331)
- support multiple switch instances (and doc)
- add psycopg2 usability (by loading of optional layer python3_scientific_core@mfext)
- remove directory_observer (now in a dedicated repository)
- remove acquisition (now in a specific repository)
- preparing issue227
- add python switch rule
- allow binary packages with pip by default for plugins
- new plugin system
- remove xattrfile (moved in a dedicated repo)
- remove all references to MFCOM or mfcom, including backward compatibility stuff
- add strftime placeholders for httpsend plugin
- The number of processes of the switch plugin is now configurable (default is 1)
- add a keep_original_basename in copy/move_to_plugin_step
- add httpsend plugin template
- allow empty nginx uploads
- remove absolute log paths from log_proxy usages (LOGPROXY_LOG_DIRECTORY env variable is used by default)
- use safe_eval from mfutil to evaluate conditions in switch plugin
- improve debug logs for switch plugin
- log refactoring
- adaptation to removal of layer misc@mfext
- allow ,;: in directorie/filenames
- add metrics to reinject step
- add getuid() method and better getsite() error reporting
- change the behavior of hardlinks methods to provide atomicity
- introduce acquisition decorators for gunzip and bunzip2
- allow "-" and "." in http receiver


### Bug Fixes
- remove old parameters about AMQP/MQTT from the module configuration file (#336)
- typo in .releaseignore file
- fix syslog nginx conf
- fix bug in amqp topic mode
- fix typo in configuration key for amqp (topic mode)
- remove rlimit_core (because of `ulimit -c 0` in mfext)
- fix get_original_basename/dirname behaviour in debug mode
- fix failure_policy_move_keep_tags configuration key
- fix default value for step_name
- fix issues with hardlinking when incoming files come with another uid





