---
title: "Tutorial"
date: 2018-02-12T11:06:31+01:00
weight: 20
---
A Youtube playlist is at you disposal [here](https://www.youtube.com/watch?v=3Xx9c3Wc16o&index=1&list=PLAkVnmgPixyN3DYD8S6LVBx1jKCEhFbrT) if you want short video tutorials regarding installation, usage, plugin creation, plugin release and deploy.

# How to install
To install mfdata, you first need to run the following script :

    cat >/etc/yum.repos.d/metwork.repo <<EOF
    [metwork_stable]
    name=Metwork Stable Branch
    baseurl=ftp://synapse.meteo.fr/pub/metwork/releases/rpms/continuous_integration/centos$releasever/stable
    gpgcheck=0
    enabled=1
    metadata_expire=0
    EOF

This script creates a Yum repository for Metwork. From there, you can install mfdata or any Metwork module for Centos 6 or 7. Simply **run `yum install metwork-mfdata`**.

You can also install mfdata using `.rpm` files : you first have to **download mfext, mfcom and mfdata** rpm packages form [here](ftp://synapse.meteo.fr/pub/metwork/releases/rpms/continuous_integration/centos7/stable/) (or [here](ftp://synapse.meteo.fr/pub/metwork/releases/rpms/continuous_integration/centos6/stable/) for Centos 6) and place them in a directory with them and only them in this directory. Once this is done, **run `rpm -Uvh *.rpm`**.

After the installation, you now have to start Metwork services. You can do so by **running `/etc/init.d/metwork start`**. After that, mfdata is ready to be used!

# Configurating mfdata
Configurating mfdata can be done in 2 ways : from the mfdata user after installation or by providing a custom config file for the installation.

## From mfdata user
 After logging in as mfdata in your terminal, you can edit the `mfdata/config/config.ini` configuration file. You will notice that every key-value pair is commented. This file is a copy of the default configuration file. By uncommenting a key-value pair, this new uncommented pair will overwrite the default value. You only need to uncomment key-value pairs that you want to change.
 
## During installation
If you need to configurate mfdata during its installation (when user mfdata doesn't exist yet) to avoid having to manually configurate it later, you can do so by providing a custom configuration file as `/etc/metwork.config.d/mfdata/external_plugins/config.ini` before installing mfdata. This file will be the one configuring mfdata, even if you add a configuration file in `mfdata/config/`.

It is advised to use this method only if you're familiar with mfdata and you know exactly what you want to do.

# How to use
First, you need to **log in as user mfdata** in your terminal. From there, you can run commands associated with mfdata. For instance, you can get the list of installed plugins by running `plugins.list`.

By default, **`mfdata/var/in/incoming` is the directory that receives incoming data** that needs pre-treating. If you put any file in there, it will be handled by mfdata.

Mfdata only has one plugin installed at base, the switch. Therefore, if you don't install any plugin, any incoming data will be sent to the trash by default. The trash folder is `mfdata/var/in/trash`.

If you want to use mfdata in a more interesting way than sending everything to the trash, you will need to install custom plugins.

# How to create custom plugins
Plugins can be custom made quickly and easily by using existing templates. Making plugins with mfdata is as simple as editing a configuration file. You just have to create a plugin using an existing template, then edit the configuration file so that the plugin fulfills your need, and finally release the plugin. You have multiple templates at your disposal to create your custom plugins : `move`, `archive`, and many others.

## Create and customize the plugin
To create a plugin, simply **run the `bootstrap_plugin.py create --template={TEMPLATE} {PLUGIN_NAME}` command** (more info on templates below). Once you have entered this command, you will be asked to fill in some fields to configurate and customize your plugin. You can reconfigurate your plugin anytime by **editing the `mfdata/src/{{PLUGIN_NAME}}/config.ini` config file**. For more details about each field, check the documentation in the said file. 

One of the most crucial field for your plugin is `switch_logical_condition` : **it represents the condition that must be respected so the switch directs the data to your plugin**. In other words, it represents what kind of data will be orientated towards your plugin by the switch. For example, this is where you would put that you want `.jpg` files to be treated by a plugin. In the same example, this would translate as `( x['latest.switch.main.system_magic'].startswith(b'JPEG image') )`. The condition is written in Python and is `None` by default. **This condition must be a boolean expression that evaluates as `True` for the type of data you are interested in**.

You can also chain plugins together if you don't want to systematically return a pre-treated data to the switch. You can change where the resulting pre-treated data will be injected. You can see an example shown in [this video](https://www.youtube.com/watch?v=XdZgA5t_rdI&list=PLAkVnmgPixyN3DYD8S6LVBx1jKCEhFbrT&index=6) at 0:42, redirecting the output of the plugin created in [this video](https://www.youtube.com/watch?v=7ofkZ7eW6Og&index=5&list=PLAkVnmgPixyN3DYD8S6LVBx1jKCEhFbrT). For example, you can choose to send all files converted to `.jpg` to one of your server via ftp.

**If the templates don't satisfy your needs, you can always edit the generated `main.py` file** in your plugin's directory. This file inherits from a certain class depending on the template you chose during the creation of the plugin (if you chose a template). From your `main.py` file, you can override any method to suit your needs. For more infos about the role of each method, check [the documentation](http://synapse/pub/metwork/docs/master/mfdata/api_acquisition.html). The `process` function is one of the most important since it defines what action will be executed on the data files sent to your plugin. It is this function that moves the files, archives them or unzips them... It represents the pre-processing that the data files will go through.

## Install on dev build
Once you're done customizing your plugin, just **enter `make develop` in your terminal** (from the plugin's directory) and your custom plugin will be installed so you can test its behavior. Incoming data will now react to your new plugin. **Only use this installation method in a developing environment, not in production!**

## Release
To **release a stable version of your plugin, enter `make release`** in your terminal (from the plugin's directory). Doing so will create a `.plugin` file that will be used to deploy your plugins. Releasing a plugin makes it production-ready, ready to be deployed.

## Deploy
To deploy your custom plugins, it is advised that you put all of their associated `.plugin` files in the same directory. From there, you can **run `plugins.install {{.plugin FILE}}` to install your released plugins** in your production environment. You can check if the installation worked by running `plugins.list`. **Once all of your released plugins were installed, you can delete the `.plugin` files**, hence the advice to group them all in a single directory : you'll only have to delete the directory.

# Plugin templates
The following arguments have to be set in the `args` filed in the configuration file.

## The `move` template
This template simply **moves incoming files to a set destination folder**. This destination folder is customizable via the `--dest-dir` argument. You can also choose to keep the original filename via the `--keep-original-basenames` argument. You can also force a chmod on target files by inputting octal chmod values (ex: `0700`) to the `--force-chmod` argument.


## The `fork` template
This template allows you to **execute shell commands in a subprocess**. The command you want to execute is given to the `--command-template` argument. You can use the `{PATH}` and `{PLUGIN_DIR}` variables in the shell commands you want to input to represent the data file's path and the plugin's path respectively.


## The `delete` template
This template **deletes incoming files**, plain and simple.


## The `default` template
The `default` template allows you to  define a custom behaviour by overriding `metwork/mfdata/src/acquisition/acquisition/step.py`. Doing so will allow you to define a custom processing method for your data. **Use this if you want to edit `main.py` to create a custom pre-processing method which is not based on any existing template**.


## The `archive` template
This template allows you to **archive data**. Archiving a file moves it to the associated archiving directory, but it also formats its name. The archiving directory and the archiving format are customizable via the  `--dest-dir` and `--strftime-template` arguments. 

You can use the `{ORIGINAL_BASENAME}`, `{ORIGINAL_DIRNAME}`, `{RANDOM_ID}` and `{STEP_COUNTER}` variables in `--strftime-template` for customizing the archiving format. By default, the archiving fromat is `%Y%m%d/{RANDOM_ID}`


## The `ftpsend` template
This template allows you to send your data via ftp to a certain host. It has numerous parameters : 

- `--machine`, `--user` and `--passwd` : these parameters allow you to define on which host you will send the files and with which user.
- `--directory` and `--keep-original-basenames` : just like with the `move` template, these parameters define, respectively, the **destination directory** and if you want to **keep the original names for the transfered data files** (the files will have the same name on the target machine as they had previously).
- `--suffix` : **temporary suffix that will be attached to files during the transfer**. By default, the suffix is `.t`.
- `--max-number` : **maximum number of files before transferring the batch of data files**. By default, it is `100`. It represents the size limit of the batch of files that needs to be transfered via FTP. If you get to this limit, the batch will be sent immediately instead of waiting for the time limit. For example, by default, if you receive 344 files, you will send 3 batches of 100 files immediately and you will have a last batch of 44 files waiting for the time limit.
- `--max-wait` : **maximum time before transferring the batch of data files**. By default, it is `10`. If after this set amount of time, a batch has not been saturated (the maximum number of files has not been reached), the batch of files will be sent. In the last example, the last batch of 44 files will be sent after 10 seconds.

# Included plugins

- `switch` : This plugin is installed by default. As explained before, it **guides incoming data files towards the appropriate plugin** depending on switch conditions defined by each plugins.

- `ungzip` : This plugin allows you to unzip `.gz` files. This plugin automatically handles `.gz` files and returns the unzipped file to the switch. This plugin is **NOT** installed by default.

# Some helpful commands
- `plugins.list` : You can get the list of installed plugins using this command

        > plugins.list
        Installed plugins:
        
        | NAME                      | VERSION                   | RELEASE
        ---------------------------------------------------------------------------
        | switch                    | master.bf83454            | 1
        
        Total: 1 plugin(s)

- `plugins.info {{PLUGIN NAME}}` : This command allows you to get more infomation concerning a given plugin.

        > plugins.info switch
        Metadata:

        Name        : switch
        Version     : master.bf83454
        Release     : 1
        Architecture: x86_64
        Install Date: Mon 22 Jan 2018 09:26:45 AM CET
        Group       : Development/Tools
        Size        : 142521
        License     : BSD
        Signature   : (none)
        Source RPM  : switch-master.bf83454-1.src.rpm
        Build Date  : Mon 08 Jan 2018 03:29:59 PM CET
        Build Host  : synflood310x
        Relocations : /metwork_plugin 
        Packager    : Fabien MARTY <fabien.marty@gmail.com>
        Vendor      : MetWork
        URL         : http://metwork
        Summary     : plugin which feeds other plugins depending on file types
        Description :
        plugin which feeds other plugins depending on file types

        List of files:

        /home/user/metwork/mfdata/var/plugins
        /home/user/metwork/mfdata/var/plugins/switch
        /home/user/metwork/mfdata/var/plugins/switch/config.ini
        /home/user/metwork/mfdata/var/plugins/switch/main.py
        /home/user/metwork/mfdata/var/plugins/switch/python3_virtualenv_sources
        /home/user/metwork/mfdata/var/plugins/switch/python3_virtualenv_sources/requirements-to-freeze.txt
        /home/user/metwork/mfdata/var/plugins/switch/python3_virtualenv_sources/requirements3.txt
        /home/user/metwork/mfdata/var/plugins/switch/python3_virtualenv_sources/src
        /home/user/metwork/mfdata/var/plugins/switch/python3_virtualenv_sources/src/python-magic-0.4.13.tar.gz

# Uninstalling a plugin
You can uninstall a plugin by running `plugins.uninstall {{PLUGIN NAME}}`
