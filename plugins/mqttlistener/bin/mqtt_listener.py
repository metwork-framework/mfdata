#!/usr/bin/env python3

import time
import paho.mqtt.client as mqtt
import xattrfile
import signal
from mfutil import get_unique_hexa_identifier
from acquisition.listener import AcquisitionListener
from acquisition.utils import dest_dir_to_absolute


class MqttListener(AcquisitionListener):

    client = None
    connected = False

    def init(self):
        tmp = self.get_custom_config_value("mqtt_clean_session", default=1,
                                           transform=int)
        self.mqtt_clean_session = (tmp == 1)
        self.mqtt_client_id = self.get_custom_config_value("mqtt_client_id",
                                                           default=None)
        if self.mqtt_client_id is None or self.mqtt_client_id == "" or \
                self.mqtt_client_id == "null":
            if self.mqtt_clean_session is False:
                raise Exception("you must set a mqtt_client_id when "
                                "clean_session==0")
            self.mqtt_client_id = get_unique_hexa_identifier()
        self.mqtt_qos = self.get_custom_config_value("mqtt_qos", default="0",
                                                     transform=int)
        if self.mqtt_qos not in (0, 1, 2):
            raise Exception("mqtt_qos must be 0, 1 or 2")
        self.mqtt_hostname = self.get_custom_config_value("mqtt_hostname",
                                                          default="localhost")
        self.mqtt_port = self.get_custom_config_value("mqtt_port",
                                                      default="1883",
                                                      transform=int)
        self.mqtt_topic = self.get_custom_config_value("mqtt_topic",
                                                       default="#")
        self.mqtt_keepalive = self.get_custom_config_value(
            "mqtt_keepalive", default="60", transform=int)
        tmp = self.get_custom_config_value("dest_dir", default=None)
        self.dest_dir, _ = dest_dir_to_absolute(tmp, allow_absolute=True)
        self.client = mqtt.Client(client_id=self.mqtt_client_id,
                                  clean_session=self.mqtt_clean_session)
        self.client.on_message = self._on_message
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        signal.signal(signal.SIGTERM, self.__sigterm_handler)

    def _on_connect(self, client, userdata, flags, rc):
        self.info("the client is connected to the broker")
        client.subscribe(self.mqtt_topic, self.mqtt_qos)

    def _on_disconnect(self, client, userdata, rc):
        self.info("the client is disconnected")

    def __on_message(self, client, userdata, message):
        self.info("message received on %s (size: %i)", message.topic,
                  len(message.payload))
        self.debug("message qos: %s", message.qos)
        self.debug("message retain flag: %s", message.retain)
        tmp_filepath = self.get_tmp_filepath()
        with open(tmp_filepath, "wb") as f:
            f.write(message.payload)
        xaf = xattrfile.XattrFile(tmp_filepath)
        self.set_tag(xaf, "mqttlistener_topic", message.topic,
                     add_latest=False)
        self.set_tag(xaf, "mqttlistener_hostname", self.mqtt_hostname,
                     add_latest=False)
        self.set_tag(xaf, "mqttlistener_port", str(self.mqtt_port),
                     add_latest=False)
        self._set_before_tags(xaf)
        target = self.get_target_filepath(xaf)
        res, _ = xaf.move_or_copy(target)
        if res:
            self.info("message saved in %s" % target)
        else:
            self.warning("can't save message in %s" % target)

    def _on_message(self, client, userdata, message):
        try:
            return self.__on_message(client, userdata, message)
        except Exception:
            self.exception("exception catched during _on_message()")

    def get_target_filepath(self, xaf):
        return "%s/%s" % (self.dest_dir, get_unique_hexa_identifier())

    def __sigterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        try:
            self.client.disconnect()
        except Exception:
            pass

    def listen(self):
        self.info("Daemon started")
        while True:
            try:
                self.info("Connecting to %s:%i...", self.mqtt_hostname,
                          self.mqtt_port)
                self.client.connect(self.mqtt_hostname, self.mqtt_port,
                                    self.mqtt_keepalive)
            except Exception as e:
                self.warning(
                    "Can't connect to the broker %s:%i with exception: %s"
                    " => let's wait 5s and try again"
                    % (self.mqtt_hostname, self.mqtt_port, e)
                )
                time.sleep(5)
                continue
            self.client.loop_forever()
            break
        self.info("Stopping daemon")


if __name__ == "__main__":
    x = MqttListener()
    x.run()
