# Identify particular types of files

## Introduction

In lot of cases, you we have to identify the type of file processed by MFDATA
In most cases, you may want to identify the type of file your MFDATA plugin have to to deal with.

In order to do this, you configure the `switch_logical_condition` parameter in your plugin `config.ini` file, e.g. to identifiy JPEG files
```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'JPEG image') )

```

By default, MDFATA uses the default Linux `magic` file in its attempt to identify the type of a file.

To locate the `magic` file path, enter:

```bash
file --version
```
```
file-5.11
magic file from /etc/magic:/usr/share/misc/magic

```

So it uses both the `/etc/magic` file, and the `/usr/share/misc/magic`.
The magic file contains lines describing magic numbers, which identify particular types of files.

In order to identify type which are not in the default `magic` file or if the `file` identification doesn't suit you, you may:

- either create your own `magic` file with your identification rule(s) and put it in you plugin directory. This will be available only in your plugin context.
- or add the your identification rule(s) in the `/etc/magic` file. This will be available in the Linux system.

## Example:

Identify `grib` files.

By default `grib` file are identified as data:
```bash
file example.grib
```
```
example.grib: data
```

Edit the `/etc/magic` file (as `root` user) and add `grib` identification rules:
```cfg
# Magic local data for file(1) command.
# Insert here your local magic data. Format is described in magic(5).

# GRIB
0   string  GRIB    GRIB file
```

Save the  `/etc/magic` file and enter again;
```bash
file example.grib
```

```
example.grib: GRIB file
```

For further inforamtion, check Linux documentaition.


From now, you are able to identify GRIB files in your plugin, by setting the `switch_logical_condition` parameter in your plugin `config.ini` file:
```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'GRIB file') )

```
or
```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].contains(b'GRIB file') )

```