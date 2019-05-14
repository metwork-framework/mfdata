
# Miscellaneous

.. index:: switch_logical_condition
## The `switch_logical_condition` field

The `switch_logical_condition` is a plugin configuration field of the `config.ini` file in the rrot directory of the plugin.

The `switch_logical_condition`  **represents the condition that must be respected so the** `switch` ** plugin directs the data to the plugin**. 


When you create a plugin through the `bootstrap_plugin create` command, the default value is set to `False` (that means no file will be processed by the plugin).

`switch_logical_condition = False` means the `switch` plugin doesn't redirect any file to the plugin.

`switch_logical_condition = True` means the `switch` plugin redirects all files to the plugin.

`switch_logical_condition = {condition}` means the `switch` plugin redirects the file to the plugin if the `{condition}` is `True`. 

In most cases, the `{condition}` is based  on tags attributes set by the `switch` plugin.

The main useful tags are: `first.core.original_basename` (the base name of the processed file), `latest.switch.main.system_magic`
`latest.switch.main.{plugin name}_magic` (the 'magic' file. See :doc:`./mfdata_and_magic`).

.. index:: tag attributes
## The `switch` plugin tags attributes

The `switch` plugin sets some tags attributes.

Attributes are stored inside an :py:class:`XattrFile <xattrfile.XattrFile>` object.

These tags trace the flows processed by the different plugins and gives information about processed files.

If you need to set your own tags, refer to :py:meth:`write_tags_in_a_file <xattrfile.XattrFile.write_tags_in_a_file>`, :py:meth:`print_tags <xattrfile.print_tags>`, :py:meth:`set_tag <xattrfile.set_tag>`, :py:meth:`get_tag <xattrfile.get_tag>`

You may also check the :ref:`mfdata_additional_tutorials:Fill in the plugin` section of  :doc:`./mfdata_additional_tutorials`.

.. index:: layerapi2, layerapi2_dependencies, .layerapi2_dependencies, dependencies
## The `.layerapi2_dependencies` file

When you create a plugin with the :ref:`bootstap_plugin <mfdata_create_plugins:Create and customize the plugin>` command, a `.layerapi2_dependencies` file is created in the plugin root directory. This file contains the module/package dependencies you need for the plugin.

By default, the `.layerapi2_dependencies` file contains only minimal dependencies, e.g.:
```cfg
python3@mfdata
```
means the plugin will use Python3 from the python3 package supplied in MFDATA.

For more details on `layerapi2`, check :doc:`MFEXT layerapi2 <mfext:layerapi2>` and :ref:`MFEXT layerapi2 syntax <mfext:layerapi2:general>` documentation.

Let's assume you need a module or package which is available in the MFEXT 'scientific' package, you have to add this dependencies to the `.layerapi2_dependencies` file:
```cfg
python3@mfdata
python3_scientific@mfext
```

Let's assume now, you want to build your plugin relies on Python2 instead of Python3, the `.layerapi2_dependencies` file will look like this:
```cfg
python2@mfdata
python2_scientific@mfext
```

.. index:: layerapi2, layerapi2_extra_env, .layerapi2_extra_env
## The `.layerapi2_extra_env` file

The `.layerapi2_extra_env` file allows you to defined environment variable only in the plugin context. Check `layerapi2` MFEXT documentation.

By default, this `.layerapi2_extra_env` doesn't exist. If you need to add extra environment variables, create this file in the plugin root directory.

.. seealso::
    :ref:`MFEXT layerapi2 syntax <mfext:layerapi2:general>` documentation.

.. index:: http, curl
## Inject data files in HTTP

MFDATA allows to inject files through HTTP protocol.

By default a Nginx HTTP server is listening on port `9091`.

The HTTP url to post your files is `http://{your_mfdata_host_name}:9091/incoming/` (`http://{your_mfdata_host_name}:9091/` works too).

Only HTTP **PUT** and **POST** methods are allowed.

Here is a example to inject data with curl [curl](https://curl.haxx.se/docs/manpage.html):
```bash
curl -v -X POST -d @{your file path} http://localhost:9091/incoming/
```

You may change some configuration fields of the nginx server (including the port) in the `[nginx]` section of the `/home/mfdata/config/config.ini` file.

For a more detailed description of nginx configuration, check the  `/home/mfdata/config/config.ini` file.

.. index:: multiple steps
## Plugins with more than one step

A plugin may one or more step.

In most cases, when you create a plugin with `bootstrap_plugin.py`, only one step called `main` is created with yhe corresponding Python script (i.e. `main.py`).

However, you may create a plugin with more than one step.

_ _ _

For instance, the `archive_image` plugin introduced in the :ref:`mfdata_quick_start:Use of the ungzip plugin` tutorial and the `convert_png` plugin introduced in the :ref:`mfdata_additional_tutorials:A PNG to JPEG conversion plugin` tutorial could be merged into one plugin with 2 steps:

- one step to archive all images files, we will call it `archive_image`
- one step to convert PNG image to JPEG image, we will call it `convert_png`

**Let's create this '2 steps' plugin.**

Create an a new plugin `convert_png_archive` from the `archive` template:
```bash
bootstrap_plugin.py create --template=archive convert_png_archive
```

Rename the `main.py` to `archive_image.py`.

Change the `archive_image.py` to get something like this:
```python
#!/usr/bin/env python3

from acquisition import AcquisitionArchiveStep


class Convert_png_archiveArchiveStep(AcquisitionArchiveStep):
    plugin_name = "convert_png_archive"
    step_name = "archive_image"


if __name__ == "__main__":
    x = Convert_png_archiveArchiveStep()
    x.run()
```

Edit the `config.ini` plugin configuration file and rename `[step_main]` section to `[step_archive_image]`. Change also the `cmd` parameters to call the `archive_image.py`. The `[step_archive_image]` should look like this:
```cfg
{% raw %}
[step_archive_image]
# Command (without args) which implements the step daemon
cmd = {{MFDATA_CURRENT_PLUGIN_DIR}}/archive_image.py
# Arguments for the cmd
args = --config-file={{MFDATA_CURRENT_CONFIG_INI_PATH}} {{MFDATA_CURRENT_STEP_QUEUE}}
arg_redis-unix-socket-path = {{MODULE_RUNTIME_HOME}}/var/redis.socket
arg_dest-dir = {{MODULE_RUNTIME_HOME}}/var/archive
# Arguments above this line should not be modified
# Arguments below are asked for value when running
#   bootstrap_plugin2.py create --template archive [--make [--install] [--delete] ] name
# strftime-template : template inside above archive directory (strftime
#    placeholders are allowed, / are allowed to define subdirectories,
#    {ORIGINAL_BASENAME}, {ORIGINAL_DIRNAME}, {RANDOM_ID} and {STEP_COUNTER}
#    are also available
#    Default is : "%Y%m%d/{RANDOM_ID}"
arg_strftime-template = %Y%m%d/{RANDOM_ID}

# Keep tags/attributes in an additional file
arg_keep_tags = 1

# If keep_tags=1, the suffix to add to the filename to store tags
arg_keep_tags_suffix = .tags

# Step extra configuration
# For data supply with switch plugin : True, False or logical expression
# on file tags
# Example : (x['first.core.original_dirname'] == b'transmet_fac')
switch_logical_condition = ( b'image' in x['latest.switch.main.system_magic'] )

switch_use_hardlink = False
{% endraw %}
```

Then, copy the `main.py` from the `convert_png` plugin to `convert_png.py` in the `convert_png_archive` plugin directory.

Change the `convert_png.py` to get something like this:
```python
#!/usr/bin/env python3

import subprocess
import os

from acquisition import AcquisitionForkStep


class Convert_pngConvertStep(AcquisitionForkStep):
    plugin_name = "convert_png_archive"
    step_name = "convert_png"

    def process(self, xaf):
        cmd = self.get_command(xaf.filepath)
        self.info("Calling %s ...", cmd)
        return_code = subprocess.call(cmd, shell=True)
        if return_code != 0:
            self.warning("%s returned a bad return code: %i",
                         cmd, return_code)
        return return_code == 0


if __name__ == "__main__":
    x = Convert_pngConvertStep()
    x.run()

```

Edit the `config.ini` plugin configuration file and copy the `[step_main]` section from the `convert_png` plugin `[step_convert_png]`. Change also the `cmd` parameters to call the `convert_png.py`. The `[step_convert_png]` should look like this:
```cfg
{% raw %}
[step_convert_png]
# Command (without args) which implements the step daemon
cmd = {{MFDATA_CURRENT_PLUGIN_DIR}}/convert_png.py

# Arguments for the cmd
args = --config-file={{MFDATA_CURRENT_CONFIG_INI_PATH}} {{MFDATA_CURRENT_STEP_QUEUE}}
arg_redis-unix-socket-path = {{MODULE_RUNTIME_HOME}}/var/redis.socket
# Arguments above this line should not be modified
# Arguments below are asked for value when running
# command-template : command template to execute on each file
#    {PATH} string will be replaced by the file fullpath ({PATH} must be
#       present in command-template
#    {PLUGIN_DIR} string will be replaced by the full plugin directory
#    Example : ffmpeg -i {PATH} -acodec libmp3lame {PATH}.mp3
#arg_command-template = "{PLUGIN_DIR}/convert.sh {PATH}"
arg_command-template = {PLUGIN_DIR}/convert.sh {PATH}
##### Step extra configuration #####
# For data supply with switch plugin : True, False or logical expression
# on file tags
# Example : (x['first.core.original_dirname'] == b'transmet_fac')
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'PNG image') )
{% endraw %}
```

Copy the `convert.sh` from the `convert_png` plugin to the `convert_png_archive` plugin directory.

Build the plugin (`make develop`) and run it by injecting PNG or JPEG files:

- JPEG files are archived
- PNG files are converted to JPEG files and then archived


The behaviour of this '2 steps' `convert_png_archive` plugin is similar to the `archive_image` + `convert_png` plugins.

.. tip::
	The benefit of designing a plugin with multiple steps is that each step can share resources, functions, classes,... while plugins can't

_ _ _

.. tip::
	When you create a plugin from the `ftpsend` template, the plugin contains 2 step : the `send` one, and the `reinject` one. Check the :ref:`mfdata_additional_tutorials:Sending a file by FTP` tutorial.

.. index:: outside command
.. _outside_metwork_command:

## The `outside` Metwork command

The `outside` is a command utility that allow you execute commands outside the Metwork environment.

For instance, let's assume the Python version of Metwork is 3.5.6 and the Python version installed on your system is Python 2.7.5.

For instance:

- Entering the command from the Metwork environment:

```bash
python --version
```
```
Python 3.5.6
```

- Entering the command from the Metwork environment:

```bash
outside python --version
```
```
Python 2.7.5
```
.. index:: crontab support
## The `crontab` support

Each plugin has a `crontab` support to schedule the execution of programs.

In order to enable your plugin `crontab`, just create a `crontab` file in the root directory of the plugin and set the tasks you want to schedule. For further details about `crontab`, check the Linux documentation (`man crontab` command or http://man7.org/linux/man-pages/man5/crontab.5.html)

An example of `crontab` file can be check by creating a plugin from an `archive` template (:ref:`mfdata_quick_start:Use of the ungzip plugin` tutorial). After creating the plugin, edit and check the `crontab` file in the root directory of the plugin.

In order to (re)load the contab file:
- If the crontab file does not exist and you create it, you have to restart MFDATA by entering `mfdata.stop` then `mfdata.start` commands (or reinstall the plugin)
- If the crontab file exists and you just change its content, you have just to wait a few seconds for the changes to be automatically taken into account.

.. tip::
    - you may use environment variable in your command surrounded with {% raw %}{{ }} {% endraw %}. Environment variables are substituted when cron is installed
    - you may use the wrapper `cronwrap.sh` in order to execute the command in the Metwork context.

.. warning::
	- Never use `crontab -e` to edit the crontab file inline.
	- Never override the crontab file by entering the command `crontab [your_crontab_file]`


If you need to execute your `cron` command in the Metwork context, you should use the cron wrapper script `${MFDATA_HOME}/bin/cronwrap.sh`, e.g. :
```cfg
{% raw %}
{{MFDATA_HOME}}/bin/cronwrap.sh --lock --low "find {{MODULE_RUNTIME_HOME}}/var/archive/ -type f -mtime +5 -exec rm -f {} \;" >/dev/null 2>&1

{{MFDATA_HOME}}/bin/cronwrap.sh -- plugin_wrapper [your_plugin_name]  [your_sh_command] >{{MODULE_RUNTIME_HOME}}/log/[your_log_filename] 2>&1
{% endraw %}
```

Enter `cronwrap.sh --help` for more details.

.. index:: Extra daemon, daemon
## Extra daemon

You can add extra daemons which will be launched within your plugin. In order to do this, edit the `config.ini` plugin configuration file and add an `[extra_daemon_xxx]` section.
You have to provide a command to daemonize (the command must run in foreground and not daemonize by itself):
```cfg
[extra_daemon_foo]
cmd_and_args = /your/foreground/command command_arg1 command_arg2
# numprocesses=1
```
The `numprocesses` argument is the the number of processes allocated to you daemon command. The default value is 1.

Of course, you can define as many daemon as you want by adding `[extra_daemon_*]` section:
```cfg
[extra_daemon_xxx]
cmd_and_args = /your/foreground/command1 command_arg1 command_arg2

[extra_daemon_yyy]
cmd_and_args = /your/foreground/command2 command_arg1

[extra_daemon_zzz]
cmd_and_args = /your/foreground/command3

...
```

## Access a database

A plugin can access a database through Python ORMs, like [SQLAlchemy](https://www.sqlalchemy.org/), [Records](https://github.com/kennethreitz/records), [Django ORM](https://www.djangoproject.com/), [peewee](http://docs.peewee-orm.com/), and so on.

Metwork supplies :index:`PostgreSQL`/:index:`PostGIS` database through the MFBASE storage module. If you want to easily and quickly install a Postgres database, check the :doc:`MFBASE documentation <mfbase:index>`.


## MFDATA - How it works ?


[Circus](https://circus.readthedocs.io/en/latest/) is a Python program in order to monitor and control processes and sockets.


[Redis](https://redis.io/) is an in-memory data structure store, used as a database, cache and message broker.

`directory_observer` is a Metwork tool that allows you to monitor activity on various directories and push the corresponding events to a Redis queue (a list). For example, you may create a file inside one of your monitored directories, the creation event will be pushed to the Redis queue.

`conf_monitor` is a Metwork tool in order to monitor the configuration files.

![MFDATA Overall architecture](./images/overall_architecture.jpg)

Circus acts as a process watcher and runner. You may check the full `circus.ini` configuration file in the `/home/mfdata/tmp/config_auto/` directory. Check the [Circus architecture](https://circus.readthedocs.io/en/latest/design/architecture/)


The `directory_observer.ini` configuration file defines, among others, the following keys for each section (one section per plugin step):
- `active` : whether or not a directory should be scanned
- `directory` : which directory is monitored
- `queue` :  the name of the Redis queue where the events will be pushed.

You may check the full `directory_observer.ini` configuration file in the `/home/mfdata/tmp/config_auto/` directory.

`directory_observer` scans the directories configured in the `directory_observer.ini` file.

`step-xxx` is the a step defines in your plugin.  There is as many `step-xxx` as plugins steps.


Once the monitoring of the directories is started, any action on the monitored directory is noticed and pushed to the Redis queue. The message contains:

- the directory in which the event happened.
- the file which brings about the event (the file which was created, moved or renamed).
- the associated event.
- the event timestamp


Depending on the event, the corresponding plugin step is executed. The event is popped from the Redis queue.





