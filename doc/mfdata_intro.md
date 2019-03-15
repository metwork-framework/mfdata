# Introduction to MFDATA

## What is mfdata?
Mfdata is a Python module that receives incoming data and pre-processes this data depending on its attributes, using custom methods. Mfdata works with plugins, each plugin doing a specific pre-processing like archiving, unzipping or sending the data to a specific ftp host for example. By using multiple plugins, you can create more complex behaviours : for example, if you are only interested in images with a `.jpg` format, you can create a plugin that archives `.jpg` files, one that converts `.png` image to `.jpg`, one that automatically unzip `.gz` files if you expect to receive zipped data (like `image.jpg.gz`). Any data that you are not interested in is discarded.

## How do plugins work?
All of the plugins are linked (directly or indirectly) to a central plugin, the `switch`, that receives incoming data and directs it towards the appropriate plugin (s). Each plugin has a switch condition that allows the switch to properly guide the data. For example, the `ungzip` plugin's switch condition will only take files that end in `.gz`. As said earlier, any data that can't be orientated by the switch is discarded in a trash directory. 

If multiple plugins have the same switch condition, the data is duplicated and distributed to each plugin. You can use this mechanism to create ftp duplicators for example.

![Plugin interactions](graph_plugin_interractions_mfdata.png "Plugin interactions")

A plugin's output can be directed to various destinations, depending on the plugin's role. It can be directed back to the switch for more pre-processing (if you unzip a file, for example, and want to pre-process the unzipped file depending on its type), it can be directed to a specific destination like an archive directory or a ftp host or even directed to another plugin for more complex pre-processing.

## Why would I use mfdata?
If you have a data stream with various types of files, mfdata is the tool you need. You can set multiple rules depending on the data files' attributes (like its extension for example). As long as you can make a boolean condition, you can direct incoming data. 

If you want different pre-processing like archiving, un-gzipping, sending through ftp or any custom method for different file types, you can do that easily with mfdata. You even have templates at your disposal for building your own custom plugins quickly and easily!
