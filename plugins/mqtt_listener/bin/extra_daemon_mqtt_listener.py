#!/usr/bin/env python3

import mfutil
import os
import paho.mqtt.client as mqtt
import xattrfile
import signal
from acquisition.listener import AcquisitionListener


class ExtraDaemonMqttListener(AcquisitionListener):

    client = None
    plugin_name = "mqtt_listener"
    daemon_name = "extra_daemon_mqtt_listener"
    connected = False

    def __init__(self):
        super(ExtraDaemonMqttListener, self).__init__()
        self.client = mqtt.Client()
        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        signal.signal(signal.SIGTERM, self.__sigterm_handler)

    def _on_connect(self, client, userdata, flags, rc):
        self.info("the client is connected to the broker")
        client.subscribe(self.args.subscription_topic)

    def _on_disconnect(self, client, userdata, rc):
        self.info("the client disconnected from the broker")

    def _on_message(self, client, userdata, message):
        self.info("message received on %s (size: %i)", message.topic,
                  len(message.payload))
        self.debug("message qos: %s", message.qos)
        self.debug("message retain flag: %s", message.retain)
        self.debug("message info: %s", message.info)
        basename = mfutil.get_unique_hexa_identifier()
        filepath = os.path.join(self.args.dest_dir, basename)
        tmp_filepath = ".".join((filepath, self.args.tmp_suffix))
        with open(tmp_filepath, "wb") as f:
            f.write(message.payload)
        xaf = xattrfile.XattrFile(tmp_filepath)
        self.set_tag(
            xaf, "mqtt_listener_subscription_topic",
            self.args.subscription_topic
        )
        self.set_tag(xaf, "mqtt_listener_received_topic", message.topic)
        self.set_tag(
            xaf, "mqtt_listener_broker_hostname", self.args.broker_hostname
        )
        self.set_tag(
            xaf, "mqtt_listener_broker_port", str(self.args.broker_port)
        )
        self._set_before_tags(xaf)
        xaf.rename(filepath)

    def __sigterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        try:
            self.client.disconnect()
        except Exception:
            pass

    def add_extra_arguments(self, parser):
        parser.add_argument(
            "--broker-hostname",
            action="store",
            default="127.0.0.1",
            help="the hostname or IP address of the remote broker. "
            "Defaults to localhost",
        )
        parser.add_argument(
            "--broker-port",
            action="store",
            default=1883,
            type=int,
            help="the network port of the server host to "
            "connect to. Defaults to 1883.",
        )
        parser.add_argument(
            "--keep-alive",
            action="store",
            default=60,
            type=int,
            help="maximum period in seconds allowed between"
            " communications with the broker",
        )
        parser.add_argument(
            "--dest-dir",
            action="store",
            help="destination directory of the file "
            "made from the MQTT message",
        )
        parser.add_argument(
            "--subscription-topic",
            action="store",
            default="#",
            help="string specifying the subscription topic "
            "to subscribe to. Default everybody",
        )
        parser.add_argument(
            "--tmp-suffix",
            action="store",
            default="t",
            help="temporary file suffix. Default t",
        )

    def listen(self):
        self.info("Start daemon %s" % self.daemon_name)
        self.debug("broker_hostname: %s" % self.args.broker_hostname)
        self.debug("broker_port: %s" % self.args.broker_port)
        self.debug("keep_alive: %s" % self.args.keep_alive)
        self.debug("dest_dir: %s" % self.args.dest_dir)
        self.debug("subscription-topic: %s" % self.args.subscription_topic)
        try:
            self.client.connect(self.args.broker_hostname,
                                port=self.args.broker_port)
        except Exception:
            self.warning(
                "Can not connect to the broker %s on port %d"
                % (self.args.broker_hostname, self.args.broker_port)
            )
            return
        self.client.loop_forever()
        self.info("Stopping daemon")


if __name__ == "__main__":
    x = ExtraDaemonMqttListener()
    x.run()
