# release_0.8 CHANGELOG

## v0.8.6 (2019-10-25)

### New Features

- change the behavior of hardlinks methods to provide atomicity

## v0.8.5 (2019-10-22)

### New Features

- allow "-" and "." in http receiver

## v0.8.4 (2019-09-22)

### New Features

- increase default file size limit for plugins

## v0.8.3 (2019-09-05)

### New Features

- introduce a bunzip2 plugin

### Bug Fixes

- fix some warnings on switch plugin with hardlinking

## v0.8.2 (2019-08-29)

### Bug Fixes

- important fix about failure_policy_move_keep_tags

## v0.8.1 (2019-08-26)

### Bug Fixes

- fix amqp listener plugin configuration

## v0.8.0 (2019-08-14)

### New Features

- use envtpl new option --reduce-multi-blank-lines
- use template inheritance for mfdata plugins (inspired by mfserv)
- add optional amqp 0.9.1 incoming messages support

### Bug Fixes

- create a missing directory during hot reload after a new plugin install


