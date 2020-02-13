# CHANGELOG


## [Unreleased]

### New Features
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
- remove rlimit_core (because of `ulimit -c 0` in mfext)
- fix get_original_basename/dirname behaviour in debug mode
- fix failure_policy_move_keep_tags configuration key
- fix default value for step_name
- fix issues with hardlinking when incoming files come with another uid





