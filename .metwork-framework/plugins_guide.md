# Plugins guide

## Plugins Commands

This section sums up all the commands you will need to build, install a plugin.

Use `-h` or `--help` option of the command to review all available options of the command.

### `plugins.list`

List installed plugins.
```bash
plugins.list [options]
```

Note: if you have a version named `dev_link`, the plugin is installed as a symbolic link to a source directory. 
It's a kind of "development mode".


### `plugins.install`

Install a given plugin from a `.plugin` file.
```bash
plugins.install {plugin file path} [options]
```

### `plugins.uninstall`

Uninstall a given plugin **name** (not file). The name corresponds to the first column of `plugins.list` output.
```bash
plugins.uninstall {plugin name} [options]
```

### `plugins.info`

Get more infomation about a  plugin.
```bash
plugins.info {plugin_name}
```

### `plugin_env`

If you have a virtualenv in your plugin or if you want to simulate the exact environment your code will run in the context of your plugin, you can use the `plugin_env` interactive command.

If you are developping, the best way is to go in the root directory of your plugin and use `plugin_env` without argument.

If you have a "normal" installed plugin, you can use `plugin_env {PLUGIN_NAME}`.

When you are inside a plugin environment, you will find some extra environment variables:
```bash
env | grep "^${MODULE}_" | grep CURRENT
```

```
MFDATA_CURRENT_PLUGIN_NAME=my_plugin
MFDATA_CURRENT_PLUGIN_DIR=/home/mfdata/var/plugins/my_plugin
MFDATA_CURRENT_PLUGIN_LABEL=plugin_my_plugin@mfdata
```

And of course, paths of your plugin "layer" (kind of virtualenv generalization) are loaded before system paths.

### `plugin_wrapper`

This command follows the same idea than `plugin_env` but in a non-interactive way. Use it for example for `crontabs` or if you want to execute a command in a given plugin environment without changing anything to the current shell.

```bash
plugin_wrapper {PLUGIN_NAME} {COMMAND} [{COMMAND_ARG1}] [{COMMAND_ARG2}] [...]
```

Note: the plugin {PLUGIN_NAME} must be installed.

## Make Commands

### make develop

Install your plugin in "development mode" (you don't need to release and install each time you make a modification), the plugin installed through a symlink.
```bash
make develop
```

### make release

Release your plugin as a `.plugin` file.
```bash
make release
```

### make clean

Clean (before release)
```bash
make clean
```

### make superclean

Hard-clean, can be useful when you have error with your virtualenv
```bash
make superclean
```

### make

Build your virtualenv from sources
```bash
make
```

#### python3_virtualenv_sources/requirements-to-freeze.txt

Add you python3 dependencies inside this file

FIXME: explain requirements3.txt and the differences with requirements-to-freeze.txt and how the freeze of versions
is managed

#### python2_virtualenv_sources/requirements-to-freeze.txt

Add you python2 dependencies inside this file

FIXME: explain requirements3.txt and the differences with requirements-to-freeze.txt and how the freeze of versions
is managed






