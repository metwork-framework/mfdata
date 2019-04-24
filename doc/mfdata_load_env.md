# Loading MFDATA environment

## General

After MFDATA installation, all files are located in `/opt/metwork-mfdata-{BRANCH}` directory with probably a `/opt/metwork-mfdata => /opt/metwork-mfdata-{BRANCH}` symbolic link (depending on what you have installed). Have a look in the `/opt` directory.

Because `/opt` is not used by default on [standard Linux](https://en.wikipedia.org/wiki/Filesystem_Hierarchy_Standard), the installation shouldn't break anything.

Therefore, if you do nothing specific after the installation, you won't benefit
of MFDATA environment.

In order to work with MFDATA, you have to load/activate the "Metwork MFDATA environment". There are several ways to do that, described in the sections below.

In the following sections, we use `{MFDATA_HOME}` as the installation directory of the `mfdata` module.

.. _activate_mfdata_user:

## Activate MFDATA environment by logging in as mfdata user.

Once MFDATA is installed, a `mfdata` user and, therefore, a `/home/mfdata` directory are created.

Log in as the mfdata user:
```bash
su - mfdata
```

.. note::
	If it's the first time you log in as mfdata, you have to set a password before (`passwd mfdata` or `sudo passwd mfdata`).

Then, the MFDATA environment is loaded/activated for the whole session of the `mfdata` user.

From now, you are able to work with your plugin(s) in this `/home/mfdata` directory.

## Activate MFDATA environment from any user.

You can activate the MFDATA environment from your own account.

**This way is a good one if you intend to share the same Metwork environment on the same Linux machine with other users.**

Load the `mfdata` environment for the whole shell session by entering:
```bash
source {MFDATA_HOME}/share/interative_profile
```

Then, the MFDATA environment is loaded/activated for the whole session of your account. A `metwork/mfdata` directory is created in your home directory. From now, you are able to work with your plugin(s) in this `~/metwork/mfdata` directory.

.. caution::
	The `~/metwork/mfdata` directory has nothing to do with the `/home/mfdata` :ref:`directory <activate_mfdata_user>` and they don't share anything

.. caution::
	Before sourcing `interactive_profile` mfdata service must not be started, for instance, from a `mfdata` user session. Check from a `mfdata` user session mfdata is stopped : `mfdata.status`, `mfdata.stop`.


.. tip::
	If you are fed up of always entering the `source` command, you may create an `mfdata` alias in your `.bash_profile` file and use this `mfdata` alias when you want to quickly load the "MFDATA environment":
        `MFDATA_HOME=/opt/metwork-mfdata`

        `alias mfdata="source ${MFDATA_HOME}/share/interactive_profile"`

.. warning::
	We don't recommend to source directly `mfdata interactive_profile` in your `.bash_profile` if you are working with a full graphical interface because of possible side effects with desktop environment.


## Activate MFDATA for one command only from any user.

If you want to load the "MFDATA environment" for one only command and then return back to a standard running environment, you can use the specific wrapper `{MFDATA_HOME}/bin/mfdata_wrapper`:
```bash
##### mfdata_wrapper example #####

# where is the system python command ?
$ which python
/usr/bin/python
# => this is the standard/system python command (in /usr/bin)

# what is the version of the system python command ?
$ python --version
Python 2.7.5
# => this is a python2 version

# execute python through the wrapper
# (please replace {MFDATA_HOME} by the real mfdata home !)
$ {MFDATA_HOME}/bin/mfdata_wrapper which python
/opt/metwork-mfext-master/opt/python3_core/bin/python
# => this is the metwork python command included in this module

# what is the version of the mfext python command ?
$ {MFDATA_HOME}/bin/mfext_wrapper python --version
Python 3.5.6
# => this is a python3 version
```

For more details, enter `{MFDATA_HOME}/bin/mfext_wrapper python --help` command.

## Miscellaneous

You may also be interested in the `outside` Metwork command. Check the :ref:`related documentation <outside_metwork_command>`.





