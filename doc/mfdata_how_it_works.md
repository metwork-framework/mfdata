.. index:: MFDATA architecture, circus, redis, telegraf, influxdb, jsonlog2elasticsearch, mflog2mfadmin, mflog
# How it works ?


[Circus](https://circus.readthedocs.io/en/latest/) is a Python program in order to monitor and control processes and sockets.

[Redis](https://redis.io/) is an in-memory data structure store, used as a database, cache and message broker.

[Telegraf](https://docs.influxdata.com/telegraf/) is a plugin-driven server agent for collecting and sending metrics and events from databases, systems, and IoT sensors.

`directory_observer` is a Metwork tool that allows you to monitor activity on various directories and push the corresponding events to a Redis queue (a list). For example, you may create a file inside one of your monitored directories, the creation event will be pushed to the Redis queue.

`conf_monitor` is a Metwork tool in order to monitor the configuration files.

[jsonlog2elasticsearch](https://github.com/metwork-framework/jsonlog2elasticsearch) is a daemon to send json logs read from a log file to elasticsearch.

`mflog2mfadmin` (based on [jsonlog2elasticsearch](https://github.com/metwork-framework/jsonlog2elasticsearch)) on is a daemon to send [mflog](https://github.com/metwork-framework/mflog) to elasticsearch.


![MFDATA Overall architecture](./_images/overall_architecture.svg)

Circus acts as a process watcher and runner. You may check the full `circus.ini` configuration file in the `/home/mfdata/tmp/config_auto/` directory. Check the [Circus architecture](https://circus.readthedocs.io/en/latest/design/architecture/)


The `directory_observer.ini` configuration file defines, among others, the following keys for each section (one section per plugin step):
- `active` : whether or not a directory should be scanned
- `directory` : which directory is monitored
- `queue` :  the name of the Redis queue where the events will be pushed.

You may check the full `directory_observer.ini` configuration file in the `/home/mfdata/tmp/config_auto/` directory.

`directory_observer` scans the directories configured in the `directory_observer.ini` file.

`step-xxx` is the a step defines in your plugin.  There is as many `step-xxx` as plugins steps.


Once the monitoring of the directories is started, any action on the monitored directory is noticed and pushed to the Redis queue. The message contains:

- the directory in which the event happened.
- the file which brings about the event (the file which was created, moved or renamed).
- the associated event.
- the event timestamp


Depending on the event, the corresponding plugin step is executed. The event is popped from the Redis queue.

If the MFDATA plugin is :ref:`configured for monitoring <mfdata_tuning_monitoring:Monitor a plugin>`, the metrics are send via [Telegraf](https://docs.influxdata.com/telegraf/) to the [InfluxDB](https://docs.influxdata.com/influxdb/) database on the MFADMIN server.

.. seealso::
    | :doc:`MFADMIN Documentation <mfadmin:index>`
    | :doc:`mfadmin:mfadmin_monitoring_plugins`.

<!--
Intentional comment to prevent m2r from generating bad rst statements when the file ends with a block .. xxx ::
-->