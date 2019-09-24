{% extends "layer.md" %}

{% block overview %}

The `layer1_python3` layer includes Python3 MFDATA packages.

It is included in the `.layerapi2_dependencies` file of the plugin when you choose python3 during the :ref:`creation of a plugin <mfdata_create_plugins:Create and customize the plugin>`.

You may also manually include this [dependencies (i.e. Label)](#label) in the `.layerapi2_dependencies` file.

{% endblock %}

{% block utility %}

{{ utility("print_tags") }}
{{ utility("get_tags") }}
{{ utility("set_tag") }}

{% block utility %}
