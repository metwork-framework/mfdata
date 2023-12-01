[![logo](https://raw.githubusercontent.com/metwork-framework/resources/master/logos/metwork-white-logo-small.png)](http://www.metwork-framework.org)
# mfdata

[//]: # (automatically generated from https://github.com/metwork-framework/github_organization_management/blob/master/common_files/README.md)

**Status (master branch)**

[![GitHub CI](https://github.com/metwork-framework/mfdata/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/metwork-framework/mfdata/actions?query=workflow%3ACI+branch%3Amaster)
[![Maintenance](https://raw.githubusercontent.com/metwork-framework/resources/master/badges/maintained.svg)](https://github.com/metwork-framework/resources/blob/master/badges/maintained.svg)
[![License](https://github.com/metwork-framework/resources/blob/master/badges/bsd.svg)]()
[![Gitter](https://github.com/metwork-framework/resources/blob/master/badges/community-en.svg)](https://gitter.im/metwork-framework/community-en?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Gitter](https://github.com/metwork-framework/resources/blob/master/badges/community-fr.svg)](https://gitter.im/metwork-framework/community-fr?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)



## What is MetWork FrameWork?

[MetWork Framework](https://metwork-framework.org) is an opensource system
for building and managing production grade applications or micro-services
(from development to operations).


## What is it?

This is the **M**etwork **F**ramework **DATA** processing **module**. This module is a "production ready" framework
for processing "incoming files".

*Incoming files* can arrive by:

- system FTP
- system SCP
- Restful HTTP
- MQTT
- AMQP
- [...] (you can provide a "listener plugin" to support other things)

These "incoming files" are transient. The goal in to do something with them
**in the stream**.

To do that, you can easily code and provide **plugins** to build a
workflow. This workflow can be really easy and stupid (for example: do something
for every incoming files) but also really complex with hundreds of plugins, routing rules,
plugin sequences, file duplications...

To help with complex workflows, you can rely on :

- "loose coupling" and "dynamic business routing rules" between plugins thanks to the provided **switch plugin**
- "context transmission" thanks to the **xattrfile** library
- "full inspection support" in case of errors thanks to **failure policy**, **xattrfile** libraries and **archive plugins**
- "retry mechanisms" thanks to **failure policy** and **reinject plugins**
- "full monitoring" thanks to embedded metrics and logs management (and **mfadmin module**)

It's designed to process terrabytes of data every day in a very robust way:

- you can choose the parallelism level of each plugin with a configuration file
- plugins are automatically restarted if necessary
- "waiting queues" and "resources limits" protect the system for overloading

Last but not least, thanks to the "no polling at all" principle, you can process
several thousands of file by second.

## What is not in?

Of course, you can code the behavior you want but **mfdata module** is
mainly designed to be "stateless". If you want to store durably something,
have a look at **mfbase module**.





## Cheatsheet

A cheatsheet for this module is available [here](https://metwork-framework.org/pub/metwork/continuous_integration/docs/master/mfdata/800-cheatsheet/)



## Reference documentation

- (for **master (development)** version), see [this dedicated site](http://metwork-framework.org/pub/metwork/continuous_integration/docs/master/mfdata/) for reference documentation.
- (for **latest released stable** version), see [this dedicated site](http://metwork-framework.org/pub/metwork/releases/docs/stable/mfdata/) for reference documentation.

For very specific use cases, you might be interested in
[reference documentation for integration branch](http://metwork-framework.org/pub/metwork/continuous_integration/docs/integration/mfdata/).

And if you are looking for an old released version, you can search [here](http://metwork-framework.org/pub/metwork/releases/docs/).




## Installation guide

See [this document](https://metwork-framework.org/pub/metwork/continuous_integration/docs/master/mfdata/100-installation_guide/).


## Configuration guide

See [this document](https://metwork-framework.org/pub/metwork/continuous_integration/docs/master/mfdata/300-configuration_guide/).



## Contributing guide

See [CONTRIBUTING.md](CONTRIBUTING.md) file.



## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file.



## Sponsors

*(If you are officially paid to work on MetWork Framework, please contact us to add your company logo here!)*

[![logo](https://raw.githubusercontent.com/metwork-framework/resources/master/sponsors/meteofrance-small.jpeg)](http://www.meteofrance.com)
