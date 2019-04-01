
# Miscellaneous

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


## The `switch` plugin tags attributes

The `switch` plugin sets some tags attributes.

Attributes are stored inside an :py:class:`XattrFile <xattrfile.XattrFile>` object.

These tags trace the flows processed by the different plugins and gives information about processed files.

If you need to set your own tags, refer to :py:meth:`write_tags_in_a_file <xattrfile.XattrFile.write_tags_in_a_file>`, :py:meth:`print_tags <xattrfile.print_tags>`, :py:meth:`set_tag <xattrfile.set_tag>`, :py:meth:`get_tag <xattrfile.get_tag>`

You may also check the :ref:`mfdata_additional_tutorials:Fill in the plugin` section of  :doc:`./mfdata_additional_tutorials`.

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

## Plugins with more than one step

TODO 

## The `outside` Metwork command
TODO

## The `crontab` support
TODO

## MFDATA - How it works ?

TODO (circus - redis - directory observer)

