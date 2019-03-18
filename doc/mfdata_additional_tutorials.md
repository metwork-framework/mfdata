# Additional Tutorials

## A PNG to JPEG conversion plugin

Let's create an plugin to convert a PNG image to a JPEG image and then to archive the JPEG image.

First, we have to modify the `archive_image` plugin to be able to archive all images and not only PNG images.

Open the `config.ini` file of the `archive_image` plugin and change the `switch_logical_condition` to accept all images:

```cfg
switch_logical_condition = ( b'image' in ['latest.switch.main.system_magic'] )
```

Now, **create the converter plugin** from the MFDATA `fork` template which allows to **execute shell commands in a subprocess**. Enter the command:
```bash
bootstrap_plugin.py create --template=fork convert_png
```

Configure the `switch_logical_condition` parameter in  the `convert_png/config.ini` that allow to convert PNG files.

```cfg
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'PNG image') )
```

Then, let's create a script file (`convert.sh` in the `convert_png` plugin directory) to convert a PNG file to a JPEG file (we will use the ImageMagick convert tool):
```bash
#!/bin/bash
# $1 is the incoming PNG file.

# Convert to JPEG
convert "$1" "$1.jpeg"
# Re-inject the converted file to the switch plugin
inject_file --plugin=switch "$1.jpeg"
```

Set `convert.sh` as an executable file:
```bash
chmod +x convert.sh

```

Now, we have to say to the `convert_png` plugin to launch the `convert.sh` script for each file. To do this, configure the `arg_command-template` parameter in the `convert_png/config.ini`:

```cfg
arg_command-template = "{PLUGIN_DIR}/convert.sh {PATH}"
```


Then, install (as dev build) the plugin by entering the command `make develop` from the `convert_png` plugin directory.

Check the plugin is installed, by running `plugins.list`.

Run the plugin: inject a PNG compressed file :

```bash
inject_file --incomming /tmp/my_png_file.png.gz
```


Check the archive directory. Go to the `/tmp/my_archive_image/[YYYYMMDD]` directory where `[YYYYMMDD]` is the current date.You will see two files, a PNG one and a JPEG one, with a 'RANDOM_ID' name: e.g. `85c87fe07e604c01bb81ba8311611466` and  `c210be74b8644aeeb6c1d41e4883649d`:

```bash
file 85c87fe07e604c01bb81ba8311611466
```

> 85c87fe07e604c01bb81ba8311611466: PNG image data, 120 x 165, 8-bit/color RGBA, non-interlaced

```bash
file c210be74b8644aeeb6c1d41e4883649d
```

> c210be74b8644aeeb6c1d41e4883649d: JPEG image data, JFIF standard 1.01  

The diagram below shows the data flow:

![png_to_jpeg_flow](./images/png_to_jpeg_flow.jpg)


1. The GZIP file is processed by the `switch` plugin from the MFDATA `incoming` directory
2. The `gunzip` plugin uncompress the file
3. The `gunzip` plugin puts the PNG file in the `incoming` directory. It will be process by the `switch` plugin
4. The `archive_image` plugin process the PNG file (its `switch_logical_condition` is `True`). The `convert_image` plugin process the PNG file (its `switch_logical_condition` is `True`).
5. The `convert_image` plugin puts the JPEG file in the `incoming` directory. It will be process by the `switch` plugin
6. The `archive_image` plugin process the JPEG file (its `switch_logical_condition` is `True`).


## Sending a file by FTP

Let's now create an plugin from the "ftpsend" MFDATA template.

This new plugin aims to send a JPEG file to a FTP host.

Use the `ftpsend` template to create the plugin : run the following command:
```bash
bootstrap_plugin.py create --template=ftpsend ftpsend_to_mybox
```

Enter the `machine`, `user` and `passwd` when prompting, respectively  the destination host, user and password (press [Enter] for the other parameters to keep the default value).


Go to the `ftpsend_to_mybox` sub-directory, open the `config.ini` file and check the parameters: you have just entered:
```cfg
# machine : target machine for ftp transfer
arg_machine = mybox
# user : target user for ftp transfer
arg_user = myuser
# passwd : target passwd for ftp transfer
arg_passwd = mypassword
```

Then, install (as dev build) the plugin by entering the command `make develop` from the `ftpsend_to_mybox` plugin directory.

Check the plugin is installed, by running `plugins.list`.

Let's now change the `convert_png` plugin to feed the new `ftpsend_to_mybox` plugin.

Open the `convert_png/convert.sh` script file and change the `inject_file` command as below in the `convert_png` plugin directory) to convert a PNG file to a JPEG file (we will use the ImageMagick convert tool):
```bash
#!/bin/bash
# $1 is the incoming PNG file.

# Convert to JPEG
convert "$1" "$1.jpeg"
# Re-inject the converted file to the switch plugin
inject_file --plugin=ftpsend_to_mybox --step=send "$1.jpeg"
```



## Using the `batch` template

TODO

## Create a plugin from scratch

TODO

