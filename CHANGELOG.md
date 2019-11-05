# CHANGELOG


## [Unreleased]

### New Features
- add metrics to reinject step
- add getuid() method and better getsite() error reporting
- change the behavior of hardlinks methods to provide atomicity
- introduce acquisition decorators for gunzip and bunzip2
- allow "-" and "." in http receiver


### Bug Fixes
- fix get_original_basename/dirname behaviour in debug mode
- fix failure_policy_move_keep_tags configuration key
- fix default value for step_name
- fix issues with hardlinking when incoming files come with another uid





