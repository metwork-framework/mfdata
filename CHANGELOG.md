# release_1.1 CHANGELOG

## [Unreleased]

### New Features

- load the pythonX_scientific_core layer by default in plugins (if the layer is installed) (#331)
- add some new config options to amqp_listener plugin (see issue #317) (#345)

### Bug Fixes

- remove old parameters about AMQP/MQTT from the module configuration file (#336)
- self._consumer.on_message is not set after exception (#338)
- fix multiple steps targets with switch plugin (#352)
- fix missing file in listener template (#360)
- fix some stop/start issues (#380)


