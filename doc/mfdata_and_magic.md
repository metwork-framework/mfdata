# Identify particular types of files

## Introduction

In lot of cases, you we have to identify the type of file processed by MFDATA
In most cases, you may want to identify the type of file your MFDATA plugin have to to deal with.

In order to do this, you configure the `switch_logical_condition` parameter in your plugin `config.ini` file, e.g. to identifiy JPEG files
```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'JPEG image') )

```

By default, MDFATA uses the default Linux `magic` file in its attempt to identify the type of a file. For further inforamtion about `magic`, see https://en.wikipedia.org/wiki/File_(command) or http://man7.org/linux/man-pages/man3/libmagic.3.html.

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

- either create your own `magic` file with your identification rule(s) and put it in you plugin directory. This will be available only in your plugin context.** This is the recommended way in order to manage custom magic file**.
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

Create a new `magic` file in your plugin directory and add `grib` identification rules:
```cfg
# GRIB
0   string  GRIB    GRIB file
```

Save the  `magic` file and enter the `file` with `-m {magic_file)` where `magic_file` is the path to your magic file:
```bash
file example.grib -m magic
```

```
example.grib: GRIB file
```

For further inforamtion, check Linux documentation (https://en.wikipedia.org/wiki/File_(command), http://man7.org/linux/man-pages/man3/libmagic.3.html, Linux `man file` and `man magic` commands)


From now, you are able to identify GRIB files in your plugin, by setting the `switch_logical_condition` parameter in your plugin `config.ini` file:
```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'GRIB file') )

```
or
```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].contains(b'GRIB file') )

```