
# How to create custom plugins
In order to use MFDATA and create your custom plugin, first, you have to **log in as user** `mfdata` from your terminal.

Plugins can be custom made quickly and easily by using existing templates. Making plugins with mfdata is as simple as editing a configuration file. You just have to create a plugin using an existing template, then edit the configuration file so that the plugin fulfills your need, and finally release the plugin. 

Predefined templates are available in order to create your plugin (see [Plugin templates section](#plugin-templates)).

## Create and customize the plugin
To create a plugin, simply **run the `bootstrap_plugin.py create --template={TEMPLATE} {PLUGIN_NAME}` command** (more info on templates below). Once you have entered this command, you will be asked to fill in some fields to configurate and customize your plugin. You can reconfigurate your plugin anytime by **editing the `mfdata/src/{{PLUGIN_NAME}}/config.ini` config file**. For more details about each field, check the documentation in the said file. 

One of the most crucial field for your plugin is `switch_logical_condition` : **it represents the condition that must be respected so the switch directs the data to your plugin**. In other words, it represents what kind of data will be orientated towards your plugin by the switch. For example, this is where you would put that you want `.jpg` files to be treated by a plugin. In the same example, this would translate as `( x['latest.switch.main.system_magic'].startswith(b'JPEG image') )`. The condition is written in Python and is `None` by default. **This condition must be a boolean expression that evaluates as `True` for the type of data you are interested in**.

You can also chain plugins together if you don't want to systematically return a pre-treated data to the switch. You can change where the resulting pre-treated data will be injected. You can see an example shown in [this video](https://www.youtube.com/watch?v=XdZgA5t_rdI&list=PLAkVnmgPixyN3DYD8S6LVBx1jKCEhFbrT&index=6) at 0:42, redirecting the output of the plugin created in [this video](https://www.youtube.com/watch?v=7ofkZ7eW6Og&index=5&list=PLAkVnmgPixyN3DYD8S6LVBx1jKCEhFbrT). For example, you can choose to send all files converted to `.jpg` to one of your server via ftp.

**If the templates don't satisfy your needs, you can always edit the generated `main.py` file** in your plugin's directory. This file inherits from a certain class depending on the template you chose during the creation of the plugin (if you chose a template). From your `main.py` file, you can override any method to suit your needs. For more infos about the role of each method, check [the documentation](http://synapse/pub/metwork/docs/master/mfdata/api_acquisition.html). The `process` function is one of the most important since it defines what action will be executed on the data files sent to your plugin. It is this function that moves the files, archives them or unzips them... It represents the pre-processing that the data files will go through.

## Plugin templates
The following arguments have to be set in the `args` filed in the configuration file.
Predefined templates are available in order to create your plugin.

### The `move` template
This template simply **moves incoming files to a set destination folder**. This destination folder is customizable via the `--dest-dir` argument. You can also choose to keep the original filename via the `--keep-original-basenames` argument. You can also force a chmod on target files by inputting octal chmod values (ex: `0700`) to the `--force-chmod` argument.


### The `fork` template
This template allows you to **execute shell commands in a subprocess**. The command you want to execute is given to the `--command-template` argument. You can use the `{PATH}` and `{PLUGIN_DIR}` variables in the shell commands you want to input to represent the data file's path and the plugin's path respectively.


### The `delete` template
This template **deletes incoming files**, plain and simple.


### The `default` template
The `default` template allows you to  define a custom behaviour by overriding `metwork/mfdata/src/acquisition/acquisition/step.py`. Doing so will allow you to define a custom processing method for your data. **Use this if you want to edit `main.py` to create a custom pre-processing method which is not based on any existing template**.


### The `archive` template
This template allows you to **archive data**. Archiving a file moves it to the associated archiving directory, but it also formats its name. The archiving directory and the archiving format are customizable via the  `--dest-dir` and `--strftime-template` arguments. 

You can use the `{ORIGINAL_BASENAME}`, `{ORIGINAL_DIRNAME}`, `{RANDOM_ID}` and `{STEP_COUNTER}` variables in `--strftime-template` for customizing the archiving format. By default, the archiving fromat is `%Y%m%d/{RANDOM_ID}`


### The `ftpsend` template
This template allows you to send your data via ftp to a certain host. It has numerous parameters : 

- `--machine`, `--user` and `--passwd` : these parameters allow you to define on which host you will send the files and with which user.
- `--directory` and `--keep-original-basenames` : just like with the `move` template, these parameters define, respectively, the **destination directory** and if you want to **keep the original names for the transfered data files** (the files will have the same name on the target machine as they had previously).
- `--suffix` : **temporary suffix that will be attached to files during the transfer**. By default, the suffix is `.t`.
- `--max-number` : **maximum number of files before transferring the batch of data files**. By default, it is `100`. It represents the size limit of the batch of files that needs to be transfered via FTP. If you get to this limit, the batch will be sent immediately instead of waiting for the time limit. For example, by default, if you receive 344 files, you will send 3 batches of 100 files immediately and you will have a last batch of 44 files waiting for the time limit.
- `--max-wait` : **maximum time before transferring the batch of data files**. By default, it is `10`. If after this set amount of time, a batch has not been saturated (the maximum number of files has not been reached), the batch of files will be sent. In the last example, the last batch of 44 files will be sent after 10 seconds.
