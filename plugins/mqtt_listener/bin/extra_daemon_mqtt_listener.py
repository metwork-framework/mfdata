#!/usr/bin/env python3

import configargparse
import mfutil
import os
import paho.mqtt.client as mqtt
import xattrfile
import signal
import time
from acquisition.acquisition_base import AcquisitionBase


def on_connect(client, userdata, flags, rc):
    client.is_connecting = True
    client.debug("the client is connecting to the broker.")
    client.subscribe(client.args.subscription_topic)

def on_disconnect(client, userdata, rc):
    client.debug("the client disconnects from the broker.")
    client.stop_flag = True
    client.is_connecting = False

def on_message(client, userdata, message):
    client.debug("message received: %s" ,str(message.payload.decode("utf-8")))
    client.debug("message topic: %s",message.topic)
    client.debug("message qos: %s",message.qos)
    client.debug("message retain flag: %s",message.retain)
    client.debug("message info: %s",message.info)
    client.debug("userdata: %s",userdata)
    basename = mfutil.get_unique_hexa_identifier()
    client.debug("basename: %s" % (basename))

    filepath = os.path.join(client.args.dest_dir, basename)
    tmp_filepath = '.'.join((filepath, client.args.tmp_suffix))
    client.debug("Created tmp file name : %s" % (tmp_filepath))
    with open(tmp_filepath, "w") as fichier:
        fichier.write(str(message.payload.decode("utf-8")))
    xaf = xattrfile.XattrFile(tmp_filepath)
    client.set_tag(xaf, 'mqtt_listener_subscription_topic', client.args.subscription_topic)
    client.set_tag(xaf, 'mqtt_listener_received_topic', message.topic)
    client.set_tag(xaf, 'mqtt_listener_broker_hostname', client.args.broker_hostname)
    client.set_tag(xaf, 'mqtt_listener_broker_port', str(client.args.broker_port))
    if userdata is not None:
        client.set_tag(xaf, 'mqtt_listener_user_data', userdata)
    xaf.rename(filepath)
    client.debug("Created file name : %s" % (filepath))


class ExtraDaemonMqttListener(mqtt.Client, AcquisitionBase):

    plugin_name = "mqtt_listener"
    daemon_name = "extra_daemon_mqtt_listener"
    is_connecting = False

    def __init__(self):
        super(ExtraDaemonMqttListener, self).__init__()
        signal.signal(signal.SIGTERM, self.__sigterm_handler)

    def __sigterm_handler(self, *args):
        self.debug("SIGTERM signal handled => schedulling shutdown")
        self.stop_flag = True

    def get_argument_parser(self):
        """Make and return an ArgumentParser object.
        If you want to add some extra options, you have to override
        the add_extra_arguments() method.
        Returns:
            an ArgumentParser object with all options added.
        """
        parser = configargparse.ArgumentParser()

        parser.add_argument('--broker-hostname', action='store',
                            default='127.0.0.1',
                            help='the hostname or IP address of the remote broker. Defaults to localhost')
        parser.add_argument('--broker-port', action='store', default=1883, type=int,
                            help='the network port of the server host to connect to. Defaults to 1883.')
        parser.add_argument('--keep-alive', action='store', default=60, type=int,
                            help='maximum period in seconds allowed between communications with the broker')
        parser.add_argument('--user-data', action='store',
                            default=None,
                            help='user defined data of any type. Defaults None')
        parser.add_argument('--dest-dir', action='store',
                            help='destination directory of the file made from the MQTT message')
        parser.add_argument('--subscription-topic', action='store', default='#',
                            help='string specifying the subscription topic to subscribe to. Default everybody')
        parser.add_argument('--tmp-suffix', action='store', default='t',
                            help='temporary file suffix. Default t')
        return parser

    def run(self):
        self.info("Start daemon %s" % self.daemon_name)
        parser = self.get_argument_parser()
        self.args = parser.parse_args()
        self.debug("broker_hostname: %s" % self.args.broker_hostname)
        self.debug("broker_port: %s" % self.args.broker_port)
        self.debug("keep_alive: %s" % self.args.keep_alive)
        self.debug("dest_dir: %s" % self.args.dest_dir)
        self.debug("subscription-topic: %s" % self.args.subscription_topic)
        self.debug("user_data: %s" % self.args.user_data)
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        try:
            self.connect(self.args.broker_hostname, port=self.args.broker_port)
            self.loop_start()
        except Exception:
           self.warning("Can not connect to the broker %s on port %d" % (self.args.broker_hostname,
                                                                          self.args.broker_port))
        else:
            while not self.is_connecting:
                self.debug("Waiting for connection ...")
                time.sleep(1)
            try:
                while not self.stop_flag:
                    self.loop_forever()
                self.info("Stop daemon %s" % self.daemon_name)
                self.disconnect()
            except Exception:
                self.warning("Daemon stopped on mqtt error")


if __name__ == "__main__":
    x = ExtraDaemonMqttListener()
    x.run()
