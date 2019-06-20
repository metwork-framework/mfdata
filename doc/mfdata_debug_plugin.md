.. index:: debug, log
# Debug a plugin

## Log level

Log level is defined in the `[log]` section of the `~/config/config.ini` file of the module.

There are 2 parameters :

- minimal_level[DEV]: log level in development environment (plugin installed as dev build). default value is `DEBUG`
- minimal_level: log level in production environment. default value is `INFO`

You can change the log level. After changing it, you have to stop and start MFDATA to reload the configuration, by entering the commands :

- either
```bash
mfdata.stop
mfdata.start
```

- or (as root user)
```bash
service metwork restart mfdata
```

## Run the plugin as an independent unit

In some cases, you would like to run only your plugin as an independent unit, i.e without going through others plugins, like the `switch` plugin for instance.

In order to do this, run the command `plugin_env` from the root directory of the plugin.

Then, you are able to run your plugin through a command line, with the expected and optional parameters of your plugin.

Let's assume the plugin step script is `main.py`. Enter:
```bash
python main.py --help
```

This display information about you plugin, including the required or optional parameters defined in the `main.py`.

Let's assume the input of your plugin is as JPEG file. Then, run the command:
```bash
python main.py {my_jpeg_file_path}
```
where `{my_jpeg_file_full_path}` is the path of your JPEG file.

Notice, you didn't specify any (optional) parameters in the command line, in this case the default values defined in the `main.py` will be used. To override the default value, you have to:

- either add the `-c CONFIG_FILE` argument in the command line
```bash
python main.py {my_jpeg_file_path} -c {plugin_config_file_path}
```

- or add the argument(s) in the command line (assuming the argument is dest-dir)
```bash
python main.py {my_jpeg_file_path} --dest-dir {dest_dir_path}
```


