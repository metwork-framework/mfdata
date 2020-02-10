
# Miscellaneous

.. index:: switch_logical_condition
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

.. index:: tag attributes
## The `switch` plugin tags attributes

The `switch` plugin sets some tags attributes.

Attributes are stored inside an :py:class:`XattrFile <xattrfile.XattrFile>` object.

These tags trace the flows processed by the different plugins and gives information about processed files.

If you need to set your own tags, refer to :py:meth:`write_tags_in_a_file <xattrfile.XattrFile.write_tags_in_a_file>`, :py:meth:`print_tags <xattrfile.print_tags>`, :py:meth:`set_tag <xattrfile.set_tag>`, :py:meth:`get_tag <xattrfile.get_tag>`

You may also check the :ref:`mfdata_additional_tutorials:Fill in the plugin` section of  :doc:`./mfdata_additional_tutorials`.

.. index:: layerapi2, layerapi2_dependencies, .layerapi2_dependencies, dependencies
## The `.layerapi2_dependencies` file

When you create a plugin with the :ref:`bootstap_plugin <mfdata_create_plugins:Create and customize the plugin>` command, a `.layerapi2_dependencies` file is created in the plugin root directory. This file contains the module/package dependencies you need for the plugin.

By default, the `.layerapi2_dependencies` file contains only minimal dependencies, e.g.:
```cfg
python3@mfdata
```
means the plugin will use Python3 from the python3 package supplied in MFDATA.

For more details on `layerapi2`, check :doc:`MFEXT layerapi2 <mfext:layerapi2>` and :ref:`MFEXT layerapi2 syntax <mfext:layerapi2_syntax>` documentation.

Let's assume you need a module or package which is available in the MFEXT 'scientific' package, you have to add this dependencies to the `.layerapi2_dependencies` file:
```cfg
python3@mfdata
python3_scientific@mfext
```

Let's assume now, you want to build your plugin relies on Python2 instead of Python3, the `.layerapi2_dependencies` file will look like this:
```cfg
python2@mfdata
python2_scientific@mfext
```

.. index:: layerapi2, layerapi2_extra_env, .layerapi2_extra_env
## The `.layerapi2_extra_env` file

The `.layerapi2_extra_env` file allows you to defined environment variable only in the plugin context. Check `layerapi2` MFEXT documentation.

By default, this `.layerapi2_extra_env` doesn't exist. If you need to add extra environment variables, create this file in the plugin root directory.

.. seealso::
    :ref:`MFEXT layerapi2 syntax <mfext:layerapi2_syntax>` documentation.

.. index:: http, curl
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

.. index:: MQTT, Mosquitto MQTT broker, mqtt_listener plugin 
## Trigger MFDATA plugins with MQTT messages 

You can now trigger your MFDATA plugins with [MQTT](https://github.com/mqtt/mqtt.github.io) messages.

In order to use MQTT protocol with MFDATA, you have to install the Metwork **mqtt_listener** plugin by setting `install_mqtt_listener=1` in the `[internal_plugins]` section of the MFDATA configuration file (`/home/mfdata/config/config.ini`).
Then, restart MFDATA service by entering `service metwork restart mfdata` command (as root user).

Check the `mqtt_listener` plugin is installed, by entering the `plugins.list` command.

When this plugin is installed, it connects to a configured MQTT broker, listens for a configured topic (can be a wildcard) and write a file in a configured directory (“incoming” directory by default) for each message received.

Check (and configure) the MQTT configuration (`mqtt_*` arguments) in the MQTT part in the `[internal_plugins]` section of the MFDATA configuration file (`/home/mfdata/config/config.ini`), e.g.:
```cfg
####################
#####   MQTT   #####
####################
# the hostname or IP address of the remote broker
mqtt_listener_broker_hostname=localhost

# the network port of the server host to connect to. Defaults to 1883.
mqtt_listener_broker_port=1883

# a string specifying the subscription topic to subscribe to.Default to # (all)
mqtt_listener_subscription_topic=#
```

Logs are recorded in the `extra_daemon_mqtt_listener_plugin_mqtt_listener.log` file of the MFDATA `log` directory.

.. seealso::
    | `Eclipse Mosquitto MQTT broker <https://mosquitto.org>`_
    | **mqtt_listener plugin configuration** file in the `./var/plugins/mqtt_listener` MFDATA home directory.
    | `extra_daemon_mqtt_listener.py` (**mqtt_listener plugin source code**) in the `./var/plugins/mqtt_listener/bin` MFDATA home directory.


You can do a simple test by sending a MQTT message with [mosquitto_pub](https://mosquitto.org/man/mosquitto_pub-1.html) (you need to install [Mosquitto MQTT Broker](https://mosquitto.org), e.g. `yum install mosquitto` as  root user).    

For this test, set `minimal_level=DEBUG` in the `[log]` section  and `switch_no_match_policy=keep` in `[internal_plugins]` section of the MFDATA configuration file (`/home/mfdata/config/config.ini`) and restart MFDATA.

Check the `extra_daemon_mqtt_listener_plugin_mqtt_listener.log` file:
```cfg
2019-08-20T09:21:32.312765Z     [INFO] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) Start daemon extra_daemon_mqtt_listener
2019-08-20T09:21:32.314009Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) broker_hostname: localhost
2019-08-20T09:21:32.314094Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) broker_port: 1883
2019-08-20T09:21:32.314140Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) keep_alive: 60
2019-08-20T09:21:32.314182Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) dest_dir: /home/mfdata/var/in/incoming
2019-08-20T09:21:32.314222Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) subscription-topic: #
2019-08-20T09:21:32.314261Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) user_data: None
2019-08-20T09:21:32.318131Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) Waiting for connection ...
2019-08-20T09:21:32.322292Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#71834) the client is connecting to the broker.
```

Now, publish a message, by entering the command:
```bash
 mosquitto_pub -m "message from mosquitto_pub client" -t "test" -d
```

```
Client mosqpub|77111-AND-MF-ME sending CONNECT
Client mosqpub|77111-AND-MF-ME received CONNACK (0)
Client mosqpub|77111-AND-MF-ME sending PUBLISH (d0, q0, r0, m1, 'test', ... (33 bytes))
Client mosqpub|77111-AND-MF-ME sending DISCONNECT
```

Check in the `extra_daemon_mqtt_listener_plugin_mqtt_listener.log` file, the message has been received:

```cfg
...
2019-08-20T14:10:04.859351Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) message received: message from mosquitto_pub client
2019-08-20T14:10:04.859456Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) message topic: test
2019-08-20T14:10:04.859510Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) message qos: 0
2019-08-20T14:10:04.859559Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) message retain flag: 0
2019-08-20T14:10:04.859604Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) message info: (0, 0)
2019-08-20T14:10:04.859667Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) userdata: None
2019-08-20T14:10:04.859784Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) basename: 539841478e8544d28886decc6f7bec15
2019-08-20T14:10:04.859851Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) Created tmp file name : /home/mfdata/var/in/incoming/539841478e8544d28886decc6f7bec15.t
2019-08-20T14:10:04.861961Z    [DEBUG] (xattrfile#92651) /home/mfdata/var/in/incoming/539841478e8544d28886decc6f7bec15.t moved to /home/mfdata/var/in/incoming/539841478e8544d28886decc6f7bec15
2019-08-20T14:10:04.862073Z    [DEBUG] (mfdata.mqtt_listener.extra_daemon_mqtt_listener#92651) Created file name : /home/mfdata/var/in/incoming/539841478e8544d28886decc6f7bec15
...
```
Check also the `step_switch_main.stdout` log file:
```cfg
...
2019-08-20T14:10:04.878991Z     [INFO] (mfdata.switch.main#92752) /home/mfdata/var/in/tmp/switch.main/e1af594f4d1a4811a52289622b2a1db8 moved into /home/mfdata/var/in/trash/switch.nomatch/e1af594f4d1a4811a52289622b2a1db8
2019-08-20T14:10:04.879643Z     [INFO] (mfdata.switch.main#92752) End of the /home/mfdata/var/in/incoming/539841478e8544d28886decc6f7bec15 processing after 9 ms
...
```

May be the content of the message doesn't suite any of your MFDATA plugins (if you have some installed), so and because we set `switch_no_match_policy=keep`,  
the file containing your message and created by MFDATA has been kept in the  `/home/mfdata/var/in/trash/switch.nomatch` directory. In this case, you will find the following files (according to the example above):
- e1af594f4d1a4811a52289622b2a1db8 (it contains your message)
- e1af594f4d1a4811a52289622b2a1db8.tags (it contains the tags attributes set by the switch plugin)


.. index:: AMQP, RabbitMQ, amqp_listener plugin
## AMQP incoming messages support

MFDATA has [AMQP (0.9.1)](http://www.amqp.org/specification/0-9-1/amqp-org-download) incoming messages support.

In order to use AMQP with MFDATA, you have to install the Metwork **amqp_listener** plugin by setting set `install_amqp_listener=1` in the `[internal_plugins]` section of the MFDATA configuration file (`/home/mfdata/config/config.ini`).
Then, restart MFDATA service by entering `service metwork restart mfdata` command (as root user).

Check the `amqp_listener` plugin is installed, by entering the `plugins.list` command.

Check (and configure) the AMQP configuration (`amqp*` arguments) in the AMQP part in the `[internal_plugins]` section of the MFDATA configuration file (`/home/mfdata/config/config.ini`), e.g.:
```cfg
####################
#####   AMQP   #####
####################
# the hostname or IP address of the remote broker
amqp_consumer_broker_hostname=localhost

# the network port of the server host to connect to
amqp_consumer_broker_port=5672

# The username to use to connect to the broker
amqp_consumer_credential_user=guest

# The password to use to connect to the broker (use \ to escape special chars)
amqp_consumer_credential_password=\$guest

# The subscription exchange name
amqp_consumer_subscription_exchange=test

# The subscription exchange type (fanout or topic)
amqp_consumer_subscription_exchange_type=fanout

# The subscription queue (for "fanout" mode)
amqp_consumer_subscription_queue=my_queue

# The subscription routing key (wildcards allowed) (for "topic" mode)
amqp_consumer_subscription_routing_topic_keys = "*"

```

Logs are recorded in the `extra_daemon_amqp_consumer_plugin_amqp_listener.log` file of the MFDATA `log` directory.

.. seealso::
    | `RabbitMQ Tutorials <https://www.rabbitmq.com/getstarted.html>`_
    | `Python implementation of the AMQP 0-9-1 with Pika <https://github.com/pika/pika>`_
    | `AMQP 1.0 support for RabbitMQ <https://github.com/rabbitmq/rabbitmq-amqp1.0/blob/v3.7.x/README.md>`_
    | `Qpid Proton - AMQP messaging toolkit <https://github.com/apache/qpid-proton>`_
    | **amqp_listener plugin configuration** file in the `./var/plugins/amqp_listener` MFDATA home directory.
    | `extra_daemon_amqp_consumer.py` (**amqp_listener plugin source code**) in the `./var/plugins/amqp_listener/bin` MFDATA home directory.

    
**Let's now create a simple test with RabbitMQ.**

You have to [install RabbitMQ](https://www.rabbitmq.com/download.html).

Then enable [rabbitmq_management](https://www.rabbitmq.com/management.html) by entering the following command as root user:
```bash
rabbitmq-plugins enable rabbitmq_management
```

Once RabbitMQ is installed, create an `admin` account with administrator permissions by entering the following commands:
```bash
rabbitmqctl add_user admin admin
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions admin ".*" ".*" ".*"
```

From your browser, you are now able to log in with the `admin` account to the [RabbitMQ Management UI Access](https://www.rabbitmq.com/management.html#usage-ui), e.g. `http://{hostname}:15672/`. 

**Then, check and change the MFDATA AMQP configuration** (`/home/mfdata/config/config.ini`) **to set the correct account:**
```cfg
# The username to use to connect to the broker
amqp_consumer_credential_user=admin

# The password to use to connect to the broker (use \ to escape special chars)
amqp_consumer_credential_password=admin
```

Check also the hostname or IP address of the remote broker (RabbitMQ):
```cfg
amqp_consumer_broker_hostname=localhost
```

For this test, set `minimal_level=DEBUG` in the `[log]` section  and `switch_no_match_policy=keep` in `[internal_plugins]` section of the MFDATA configuration file (`/home/mfdata/config/config.ini`).

Once the MFDATA configuration is changed, don't forget to restart MFDATA service by entering `service metwork restart mfdata` command (as root user).

**Then, write** :download:`a simple Python code </_downloads/amqp/amqp_publish.py>` **in order to publish an AMQP message with AMQP** [Pika](https://pika.readthedocs.io/en/stable/) Python library:
```python
import pika

# Set credentials
credentials = pika.PlainCredentials('admin', 'admin')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_serv, credentials=credentials))

connection = None

try:
    # Connect to RabbitMQ broker
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="and-mf-metgate-ci.akka.eu", port=5672, credentials=credentials))

    channel = connection.channel()

    # Create the queue declared in the amqp_consumer_subscription_queue MFDATA configuration, e.g. 'my_queue'
    channel.queue_declare(queue='my_queue', exclusive=False)

    # Enabled delivery confirmations
    # - see https://pika.readthedocs.io/en/stable/examples/blocking_publish_mandatory.html
    # - see https://pika.readthedocs.io/en/stable/examples/blocking_delivery_confirmations.html
    channel.confirm_delivery()

    # Set the exchange name declare in the amqp_consumer_subscription_exchange MFDATA configuration, e.g. 'test'
    exchange = "test"
    # Set the content of the message, in this example, we want to send an xml content
    message = "<notification>message from AMQP 0.9.1 client</notification>"
    # Publish th message 
    # (see https://pika.readthedocs.io/en/stable/modules/channel.html?highlight=basic_publish#pika.channel.Channel.basic_publish)
    return_code = channel.basic_publish(exchange=exchange,
                                        routing_key='my_queue',
                                        body=message,
                                        properties=pika.BasicProperties(content_type='application/xml',
                                                                        delivery_mode=1),
                                        mandatory=True)
    if return_code:
        print('Message was published (ACK)')
    else:
        print('Message was returned (NACK)')

except Exception as e:
    print(e)
finally:
    if connection is not None:
        connection.close()

```

Check in the `extra_daemon_amqp_consumer_plugin_amqp_listener.log` file, the message has been received:

```cfg
...
2019-08-20T14:14:52.856793Z    [DEBUG] (pika.adapters.utils.io_services_utils#97504) Recv would block on <socket.socket fd=7, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=6, laddr=('172.25.254.137', 54876), raddr=('172.25.254.138', 5672)>
2019-08-20T14:14:52.857675Z    [DEBUG] (mfdata.amqp_listener.extra_daemon_amqp_consumer#97504) basename: 3b4539b7f78745768e5e38ddd5356d2e
2019-08-20T14:14:52.858120Z    [DEBUG] (mfdata.amqp_listener.extra_daemon_amqp_consumer#97504) Created tmp file name : /home/mfdata/var/in/incoming/3b4539b7f78745768e5e38ddd5356d2e.t
2019-08-20T14:14:52.862111Z    [DEBUG] (xattrfile#97504) /home/mfdata/var/in/incoming/3b4539b7f78745768e5e38ddd5356d2e.t moved to /home/mfdata/var/in/incoming/3b4539b7f78745768e5e38ddd5356d2e
2019-08-20T14:14:52.862464Z    [DEBUG] (mfdata.amqp_listener.extra_daemon_amqp_consumer#97504) Created file name : /home/mfdata/var/in/incoming/3b4539b7f78745768e5e38ddd5356d2e
2019-08-20T14:14:52.862788Z     [INFO] (mfdata.amqp_listener.extra_daemon_amqp_consumer#97504) Received message 1 from None : b'<notification>   <product_id>product167</product_id>   <instance_id>product167_201810220600000</instance_id>   <ref_date>2018-12-14T06:00:00</ref_date>   <node_id>national_node_107</node_id>   <service>WFS</service>   <operation>C</operation> </notification>'
...
```


Check also the `step_switch_main.stdout` log file:
```cfg
...
2019-08-20T14:14:52.882382Z     [INFO] (mfdata.switch.main#97601) /home/mfdata/var/in/tmp/switch.main/5fec2670f30f45d98bd094d72030669d moved into /home/mfdata/var/in/trash/switch.nomatch/5fec2670f30f45d98bd094d72030669d
2019-08-20T14:14:52.883024Z     [INFO] (mfdata.switch.main#97601) End of the /home/mfdata/var/in/incoming/3b4539b7f78745768e5e38ddd5356d2e processing after 10 ms
...
```

May be the content of the message doesn't suite any of your MFDATA plugins (if you have some installed), so and because we set `switch_no_match_policy=keep`,  
the file containing your message and created by MFDATA has been kept in the  `/home/mfdata/var/in/trash/switch.nomatch` directory. In this case, you will find the following files (according to the example above):
- 5fec2670f30f45d98bd094d72030669d (it contains your message)
- 5fec2670f30f45d98bd094d72030669d.tags (it contains the tags attributes set by the switch plugin)

    
.. index:: multiple steps
## Plugins with more than one step

A plugin may one or more step.

In most cases, when you create a plugin with `bootstrap_plugin.py`, only one step called `main` is created with the corresponding Python script (i.e. `main.py`).

However, you may create a plugin with more than one step.

_ _ _

For instance, the `archive_image` plugin introduced in the :ref:`mfdata_quick_start:Use of the ungzip plugin` tutorial and the `convert_png` plugin introduced in the :ref:`mfdata_additional_tutorials:A PNG to JPEG conversion plugin` tutorial could be merged into one plugin with 2 steps:

- one step to archive all images files, we will call it `archive_image`
- one step to convert PNG image to JPEG image, we will call it `convert_png`

**Let's create this '2 steps' plugin.**

Create an a new plugin `convert_png_archive` from the `archive` template:
```bash
bootstrap_plugin.py create --template=archive convert_png_archive
```

Rename the `main.py` to `archive_image.py`.

Change the `archive_image.py` to get something like this:
```python
#!/usr/bin/env python3

from acquisition import AcquisitionArchiveStep


class Convert_png_archiveArchiveStep(AcquisitionArchiveStep):
    plugin_name = "convert_png_archive"
    step_name = "archive_image"


if __name__ == "__main__":
    x = Convert_png_archiveArchiveStep()
    x.run()
```

Edit the `config.ini` plugin configuration file and rename `[step_main]` section to `[step_archive_image]`. Change also the `cmd` parameters to call the `archive_image.py`. The `[step_archive_image]` should look like this:
```cfg
{% raw %}
[step_archive_image]
# Command (without args) which implements the step daemon
cmd = {{MFDATA_CURRENT_PLUGIN_DIR}}/archive_image.py
# Arguments for the cmd
args = --config-file={{MFDATA_CURRENT_CONFIG_INI_PATH}} {{MFDATA_CURRENT_STEP_QUEUE}}
arg_redis-unix-socket-path = {{MFMODULE_RUNTIME_HOME}}/var/redis.socket
arg_dest-dir = {{MFMODULE_RUNTIME_HOME}}/var/archive
# Arguments above this line should not be modified
# Arguments below are asked for value when running
#   bootstrap_plugin2.py create --template archive [--make [--install] [--delete] ] name
# strftime-template : template inside above archive directory (strftime
#    placeholders are allowed, / are allowed to define subdirectories,
#    {ORIGINAL_BASENAME}, {ORIGINAL_DIRNAME}, {RANDOM_ID} and {STEP_COUNTER}
#    are also available
#    Default is : "%Y%m%d/{RANDOM_ID}"
arg_strftime-template = %Y%m%d/{RANDOM_ID}

# Keep tags/attributes in an additional file
arg_keep_tags = 1

# If keep_tags=1, the suffix to add to the filename to store tags
arg_keep_tags_suffix = .tags

# Step extra configuration
# For data supply with switch plugin : True, False or logical expression
# on file tags
# Example : (x['first.core.original_dirname'] == b'transmet_fac')
switch_logical_condition = ( b'image' in x['latest.switch.main.system_magic'] )

switch_use_hardlink = False
{% endraw %}
```

Then, copy the `main.py` from the `convert_png` plugin to `convert_png.py` in the `convert_png_archive` plugin directory.

Change the `convert_png.py` to get something like this:
```python
#!/usr/bin/env python3

import subprocess
import os

from acquisition import AcquisitionForkStep


class Convert_pngConvertStep(AcquisitionForkStep):
    plugin_name = "convert_png_archive"
    step_name = "convert_png"

    def process(self, xaf):
        cmd = self.get_command(xaf.filepath)
        self.info("Calling %s ...", cmd)
        return_code = subprocess.call(cmd, shell=True)
        if return_code != 0:
            self.warning("%s returned a bad return code: %i",
                         cmd, return_code)
        return return_code == 0


if __name__ == "__main__":
    x = Convert_pngConvertStep()
    x.run()

```

Edit the `config.ini` plugin configuration file and copy the `[step_main]` section from the `convert_png` plugin `[step_convert_png]`. Change also the `cmd` parameters to call the `convert_png.py`. The `[step_convert_png]` should look like this:
```cfg
{% raw %}
[step_convert_png]
# Command (without args) which implements the step daemon
cmd = {{MFDATA_CURRENT_PLUGIN_DIR}}/convert_png.py

# Arguments for the cmd
args = --config-file={{MFDATA_CURRENT_CONFIG_INI_PATH}} {{MFDATA_CURRENT_STEP_QUEUE}}
arg_redis-unix-socket-path = {{MFMODULE_RUNTIME_HOME}}/var/redis.socket
# Arguments above this line should not be modified
# Arguments below are asked for value when running
# command-template : command template to execute on each file
#    {PATH} string will be replaced by the file fullpath ({PATH} must be
#       present in command-template
#    {PLUGIN_DIR} string will be replaced by the full plugin directory
#    Example : ffmpeg -i {PATH} -acodec libmp3lame {PATH}.mp3
#arg_command-template = "{PLUGIN_DIR}/convert.sh {PATH}"
arg_command-template = {PLUGIN_DIR}/convert.sh {PATH}
##### Step extra configuration #####
# For data supply with switch plugin : True, False or logical expression
# on file tags
# Example : (x['first.core.original_dirname'] == b'transmet_fac')
switch_logical_condition = ( x['latest.switch.main.system_magic'].startswith(b'PNG image') )
{% endraw %}
```

Copy the `convert.sh` from the `convert_png` plugin to the `convert_png_archive` plugin directory.

Build the plugin (`make develop`) and run it by injecting PNG or JPEG files:

- JPEG files are archived
- PNG files are converted to JPEG files and then archived


The behaviour of this '2 steps' `convert_png_archive` plugin is similar to the `archive_image` + `convert_png` plugins.

.. tip::
	The benefit of designing a plugin with multiple steps is that each step can share resources, functions, classes,... while plugins can't

_ _ _

.. tip::
	When you create a plugin from the `ftpsend` template, the plugin contains 2 step : the `send` one, and the `reinject` one. Check the :ref:`mfdata_additional_tutorials:Sending a file by FTP` tutorial.

.. index:: outside command
.. _outside_metwork_command:

## The `outside` Metwork command

The `outside` is a command utility that allow you execute commands outside the Metwork environment.

For instance, let's assume the Python version of Metwork is 3.5.6 and the Python version installed on your system is Python 2.7.5.

For instance:

- Entering the command from the Metwork environment:

```bash
python --version
```
```
Python 3.5.6
```

- Entering the command from the Metwork environment:

```bash
outside python --version
```
```
Python 2.7.5
```
.. index:: crontab support
## The `crontab` support

Each plugin has a `crontab` support to schedule the execution of programs.

In order to enable your plugin `crontab`, just create a `crontab` file in the root directory of the plugin and set the tasks you want to schedule. For further details about `crontab`, check the Linux documentation (`man crontab` command or http://man7.org/linux/man-pages/man5/crontab.5.html)

An example of `crontab` file can be check by creating a plugin from an `archive` template (:ref:`mfdata_quick_start:Use of the ungzip plugin` tutorial). After creating the plugin, edit and check the `crontab` file in the root directory of the plugin.

In order to (re)load the contab file:
- If the crontab file does not exist and you create it, you have to restart MFDATA by entering `mfdata.stop` then `mfdata.start` commands (or reinstall the plugin)
- If the crontab file exists and you just change its content, you have just to wait a few seconds for the changes to be automatically taken into account.

.. tip::
    - you may use environment variable in your command surrounded with {% raw %}{{ }} {% endraw %}. Environment variables are substituted when cron is installed
    - you may use the wrapper `cronwrap.sh` in order to execute the command in the Metwork context.

.. warning::
	- Never use `crontab -e` to edit the crontab file inline.
	- Never override the crontab file by entering the command `crontab [your_crontab_file]`


If you need to execute your `cron` command in the Metwork context, you should use the cron wrapper script `${MFDATA_HOME}/bin/cronwrap.sh`, e.g. :
```cfg
{% raw %}
{{MFDATA_HOME}}/bin/cronwrap.sh --lock --low "find {{MFMODULE_RUNTIME_HOME}}/var/archive/ -type f -mtime +5 -exec rm -f {} \;" >/dev/null 2>&1

{{MFDATA_HOME}}/bin/cronwrap.sh --log-capture-to [your_log_filename] -- plugin_wrapper [your_plugin_name]  [your_sh_command]
{% endraw %}
```

Enter `cronwrap.sh --help` for more details.

.. index:: Extra daemon, daemon
## Extra daemon

You can add extra daemons which will be launched within your plugin. In order to do this, edit the `config.ini` plugin configuration file and add an `[extra_daemon_xxx]` section.
You have to provide a command to daemonize (the command must run in foreground and not daemonize by itself):
```cfg
[extra_daemon_foo]
cmd_and_args = /your/foreground/command command_arg1 command_arg2
# numprocesses=1
```
The `numprocesses` argument is the the number of processes allocated to you daemon command. The default value is 1.

Of course, you can define as many daemon as you want by adding `[extra_daemon_*]` section:
```cfg
[extra_daemon_xxx]
cmd_and_args = /your/foreground/command1 command_arg1 command_arg2

[extra_daemon_yyy]
cmd_and_args = /your/foreground/command2 command_arg1

[extra_daemon_zzz]
cmd_and_args = /your/foreground/command3

...
```

## Access a database

A plugin can access a database through Python ORMs, like [SQLAlchemy](https://www.sqlalchemy.org/), [Records](https://github.com/kennethreitz/records), [Django ORM](https://www.djangoproject.com/), [peewee](http://docs.peewee-orm.com/), and so on.

Metwork supplies :index:`PostgreSQL`/:index:`PostGIS` database through the MFBASE storage module. If you want to easily and quickly install a Postgres database, check the :doc:`MFBASE documentation <mfbase:index>`.

.. tip::
    | If your plugin needs to access PostgreSQL database, you may have to install the corresponding Python library (e.g. `psycopg2`) and to load the layer (`scientific_core@mfext`) containing the postgreSQL binaries.
    | Don't forget to add :
    | - the Python library in the :ref:`requirements-to-freeze.txt file <plugins_guide:Python virtualenv>` file
    | - the `scientific_core@mfext` layer in the `.layerapi2_dependencies` file of your plugin


<!--
Intentional comment to prevent m2r from generating bad rst statements when the file ends with a block .. xxx ::
-->

