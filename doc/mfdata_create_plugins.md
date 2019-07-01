
# How to create custom plugins
In order to use MFDATA and create your custom plugin, first, you have to **log in as user** `mfdata` from your terminal.

Plugins can be custom made quickly and easily by using existing templates. Making plugins with mfdata is as simple as editing a configuration file. You just have to create a plugin using an existing template, then edit the configuration file so that the plugin fulfills your need, and finally release the plugin. 

Predefined templates are available in order to create your plugin (see [Plugin templates section](#plugin-templates)).

## Create and customize the plugin
To create a plugin, simply **run the command**.
```bash
bootstrap_plugin.py create --template={TEMPLATE} {PLUGIN_NAME}
```
where `{TEMPLATE}` is the tmplate you want to use and `{PLUGIN_NAME}` the name of ypur plugin.

Notice if you omit the `--template` argument, [the default template](#id1) will be used.

Once you have entered this command, you will be asked to fill in some fields to configurate and customize your plugin. 
You can also configure your plugin anytime by **editing the** `mfdata/{PLUGIN_NAME}/config.ini` **config file**. For more details about each field, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.

The syntax to set argument in the `mfdata/{PLUGIN_NAME}/config.ini` file is of the form: `arg_[my-arg]` with `[my-arg]` the argument name, e.g. `arg_dest-dir` means `--dest-dir` argument.

One of the most crucial field for your plugin is `switch_logical_condition`: **it represents the condition that must be respected so the switch directs the data to your plugin**.

In other words, it represents what kind of data will be orientated towards your plugin by the `switch` plugin. For example, this is where you would put that you want `.jpg` files to be treated by a plugin. In the same example, this would translate as `( x['latest.switch.main.system_magic'].startswith(b'JPEG image') )`. The condition is written in Python and is `False` by default. **This condition must be a boolean expression that evaluates as** `True` **for the type of data you are interested in**.


**If the templates don't satisfy your needs, you can always edit the generated** `main.py` **file** in your plugin's directory. This file inherits from a certain class depending on the template you chose during the creation of the plugin (if you chose a template). From your `main.py` file, you can override any method to suit your needs. For further about the role of each method, check :doc:`../api_acquisition` documentation.

The `process` function is one of the most important since it defines what action will be executed on the data files sent to your plugin. It is this function that moves the files, archives them or unzips them... It represents the pre-processing that the data files will go through.

:doc:`../mfdata_quick_start`  and :doc:`../mfdata_additional_tutorials` may help you to create your plugin.

.. index:: plugin templates, templates
## Plugin templates

Predefined templates are available in order to create your plugin.

The following command allows to display the available templates:
```bash
bootstrap_plugin.py list
```

```
List of available plugin templates:
     * archive
     * default
     * delete
     * fork
     * ftpsend
     * move
```



### The `move` template
This template simply **moves incoming files to a set destination folder**. This destination folder is customizable via the `--dest-dir` argument. You can also choose to keep the original filename via the `--keep-original-basenames` argument. You can also force a chmod on target files by inputting octal chmod values (ex: `0700`) to the `--force-chmod` argument.

For more details about each configurable fields, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.

You may also check the :ref:`mfdata_quick_start:Create your first plugin` example which implements a `move` template.

### The `fork` template
This template allows you to **execute shell commands in a subprocess**. The command you want to execute is given to the `--command-template` argument.

For more details about each configurable fields, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.

You may also check the :ref:`mfdata_additional_tutorials:A PNG to JPEG conversion plugin` example which implements a `fork` template.

### The `delete` template
This template **deletes incoming files**, plain and simple.

For more details about each configurable fields, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.


### The `default` template
The `default` template allows you to define a custom behaviour by overriding the   :py:class:`AcquisitionStep <acquisition.step.AcquisitionStep>` class.

Doing so will allow you to define a custom processing method for your data. **Use this if you want to edit** `main.py` **to create a custom pre-processing method which is not based on any existing template**.

For more details about each configurable field, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.

You may also check the :ref:`mfdata_additional_tutorials:Create a plugin from scratch` and :ref:`mfdata_additional_tutorials:Creating a batch plugin` examples which implement a `default` template.


### The `archive` template
This template allows you to **archive data**. Archiving a file moves it to the associated archiving directory, but it also formats its name. The archiving directory and the archiving format are customizable via the  `--dest-dir` and `--strftime-template` arguments.

For more details about each configurable fields, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.

You may also check the :ref:`mfdata_quick_start:Use of the ungzip plugin` example which implements an `archive` template.

### The `ftpsend` template
This template allows you to send your data via `ftp` to a certain host. It has numerous parameters :

For more details about each configurable fields, check the documentation in the `mfdata/{PLUGIN_NAME}/config.ini` file.

You may also check the :ref:`mfdata_additional_tutorials:Sending a file by FTP` example which implements a `ftpsend` template.