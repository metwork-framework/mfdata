# Installation

## Prerequisites

You must:
- have configured the metwork yum repository (see below)
- have an internet access on this computer

Metwork works on:
- a `Centos 6 x86_64` or `Centos 7 x86_64` Linux distribution installed (it should also work with correponding RHEL or ScientificLinux distribution)
- at least 6 GB available on `/opt`
- a yum repository configured for system packages (done by default)


## Configure the Metwork yum repository ?

### Choose a Metwork version

Depending on your needs (stability versus new features), you can choose between serveral versions :

- released stable versions with a standard [semantic versionning](https://semver.org/) `X.Y.Z` version number *(the more **stable** choice)*
- continuous integration versions of the release branch *(to get future **patch** versions before their release)*
- continuous integration of the `master` branch *(to get future **major** and **minor** versions before their release)*
- continuous integration of the `integration` branch *(the more **bleeding edge** choice)*

For each version, you will find the `BaseURL` in the following table:

Version | BaseURL
------- | -------
released stable | http://metwork-framework.org/pub/metwork/releases/rpms/stable/centos6/ (for centos6)<br/>http://metwork-framework.org/pub/metwork/releases/rpms/stable/centos7/ (for centos7)
continuous stable | http://metwork-framework.org/pub/metwork/continuous_integration/rpms/stable/centos6/ (for centos6)<br/>http://metwork-framework.org/pub/metwork/continuous_integration/rpms/stable/centos7/ (for centos7)
continuous master | http://metwork-framework.org/pub/metwork/continuous_integration/rpms/master/centos6/ (for centos6)<br/>http://metwork-framework.org/pub/metwork/continuous_integration/rpms/master/centos7/ (for centos7)
continuous integration | http://metwork-framework.org/pub/metwork/continuous_integration/rpms/integration/centos6/ (for centos6)<br/>http://metwork-framework.org/pub/metwork/continuous_integration/rpms/integration/centos7/ (for centos7)

### Configure the Metwork yum repository for CentOS 6 distribution

First, check the output of `uname -a |grep x86_64`. If you have nothing, you don't have a `x86_64` distribution installed and you can't install MetWork on it.

Then, if you are still here, check the output of `cat /etc/redhat-release` command. If the result is `CentOS release 6[...]`, you have a CentOS 6 distribution and you can continue here. Else, jump to the centos7 section.

To configure the metwork yum repository for **releases stable** versions on **centos6**, you just have to create a new `/etc/yum.repos.d/metwork.repo` with the following content:

```cfg
[metwork_stable]
name=MetWork Stable
baseurl=http://metwork-framework.org/pub/metwork/releases/rpms/stable/centos6/
gpgcheck=0
enabled=1
metadata_expire=0
```

You can do this with one command (as `root` user):

```bash
    cat >/etc/yum.repos.d/metwork.repo <<EOF
    [metwork_stable]
    name=MetWork Stable
    baseurl=http://metwork-framework.org/pub/metwork/releases/rpms/stable/centos6/
    gpgcheck=0
    enabled=1
    metadata_expire=0
    EOF
```

Of course, if you prefer to choose another version, you have to change the `baseurl` parameter. For example, to get `continuous master` version on `centos6`, use:

`baseurl=http://metwork-framework.org/pub/metwork/continuous_integration/rpms/master/centos6/`

### Configure the Metwork yum repository for CentOS 7 distribution


First check the output of `uname -a |grep x86_64`. If you have nothing, you don't have a `x86_64` distribution installed and you can't install MetWork on it.

Then, if you are still here, check the output of `cat /etc/redhat-release` command. If the result is `CentOS release 7[...]`, you have a CentOS 7 distribution and you can continue here. Else, go back to the centos6 section.

To configure the metwork yum repository for centos7, you just have to create a new `/etc/yum.repos.d/metwork.repo` with the following content:

```cfg
[metwork_stable]
name=MetWork Stable
baseurl=http://metwork-framework.org/pub/metwork/releases/rpms/stable/centos7/
gpgcheck=0
enabled=1
metadata_expire=0
```

You can do this with one command (as `root` user):

```bash
    cat >/etc/yum.repos.d/metwork.repo <<EOF
    [metwork_stable]
    name=MetWork Stable
    baseurl=http://metwork-framework.org/pub/metwork/releases/rpms/stable/centos7/
    gpgcheck=0
    enabled=1
    metadata_expire=0
    EOF
```

Of course, if you prefer to choose another version, you have to change the `baseurl` parameter. For example, to get `continuous master` version on `centos7`, use:

`baseurl=http://metwork-framework.org/pub/metwork/continuous_integration/rpms/master/centos7/`

### Test the Metwork yum repository

To test the repository, you can use the command `yum list "metwork*"` (as `root` user). You must have several `metwork-...` packages available.

## Install a Metwork package

You just have to execute the following command (as `root` user):

```bash
yum install metwork-{METWORK_PACKAGE_NAME}
```

with `{METWORK_PACKAGE_NAME}` replaced by `mfext`, `mfcom`, `mfbase`, `mfadmin`, `mfsysmon`, `mfserv` or `mfdata` depending of your needs.

For example, to install `mfdata` package:

```bash
yum install metwork-mfdata
```

Of course, you can install several packages on the same linux box.

You can start corresponding services (not necessary for `mfext` or `mfcom` packages) with the root command:

```bash
service metwork start
```

Or you can also reboot your computer (because metwork services are started automatically on boot).


## Uninstall a Metwork package

To uninstall a given metwork package, please stop corresponding metwork services with the `root` command:

```bash
# note: this is not necessary with mfext or mfcom
# because there is no corresponding services
service metwork stop {METWORK_PACKAGE_NAME}
```

Then, use the following command (still as `root` user):

```bash
yum remove "metwork-{METWORK_PACKAGE_NAME}*"
```

## Uninstall all Metwork packages

To uninstall all Metwork packages, use following root commands:

```bash
# We stop metwork services
service metwork stop

# we remove metwork packages
yum remove "metwork-*"
```

## Upgrade all Metwork packages

The same idea applies to upgrade.

For example, to upgrade all metwork packages on a computer, use following root commands:

```bash
# We stop metwork services
service metwork stop

# We upgrade metwork packages
yum upgrade "metwork-*"

# We start metwork services
service metwork start
```

