#!/usr/bin/env python3

import pika
import os
import mfutil
import xattrfile
from acquisition.listener import AcquisitionListener


class ExtraDaemonAmqpListener(AcquisitionListener):

    channel = None
    connection = None

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
            default=5672,
            type=int,
            help="the network port of the server host to connect to. "
            "Defaults to 1883.",
        )
        parser.add_argument(
            "--credential-username",
            action="store",
            default=None,
            help="The username to authenticate with.",
        )
        parser.add_argument(
            "--credential-password",
            action="store",
            default=None,
            help="The password to authenticate with.",
        )
        parser.add_argument(
            "--subscription-exchange",
            action="store",
            help="string specifying the subscription exchange.",
        )
        parser.add_argument(
            "--delete-queue-after-stop",
            action="store_true",
            help="delete the queue after stop process.",
        )
        parser.add_argument(
            "--dest-dir",
            action="store",
            help="destination directory of the file made "
            "from the MQTT message",
        )
        parser.add_argument(
            "--tmp-suffix",
            action="store",
            default="t",
            help="temporary file suffix. Default t",
        )

    def connect(self, exchange_type):
        username = self.args.credential_username
        password = self.args.credential_password
        if username is not None and password is not None:
            credentials = pika.PlainCredentials(username, password)
            parameters = pika.ConnectionParameters(
                host=self.args.broker_hostname,
                port=self.args.broker_port,
                credentials=credentials,
            )
        else:
            parameters = pika.ConnectionParameters(
                host=self.args.broker_hostname, port=self.args.broker_port
            )
        try:
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            self.channel.exchange_declare(
                exchange=self.args.subscription_exchange,
                exchange_type=exchange_type,
            )
        except Exception as e:
            self.error(format(e))
            return False
        except Exception:
            self.error("Error unknown")
            return False
        else:
            return True

    def _on_message(
        self,
        _unused_channel,
        basic_deliver,
        properties,
        body,
        add_extra_tags_func=None,
    ):
        basename = mfutil.get_unique_hexa_identifier()
        self.debug("basename: %s" % (basename))
        filename = os.path.join(self.args.dest_dir, basename)
        tmp_filename = ".".join((filename, self.args.tmp_suffix))
        self.debug("Created tmp file name : %s" % tmp_filename)
        with open(tmp_filename, "wb") as f:
            f.write(body)
        xaf = xattrfile.XattrFile(tmp_filename)
        self.set_tag(
            xaf,
            "amqp_listener.subscription_exchange",
            self.args.subscription_exchange,
        )
        self.set_tag(
            xaf,
            "amqp_listener_subscription_queue",
            self.args.subscription_queue,
        )
        self.set_tag(
            xaf, "amqp_listener_broker_hostname", self.args.broker_hostname
        )
        self.set_tag(
            xaf, "amqp_listener_broker_port", str(self.args.broker_port)
        )
        if add_extra_tags_func:
            add_extra_tags_func(
                self, xaf, _unused_channel, basic_deliver, properties, body
            )
        self._set_before_tags(xaf)
        self._set_after_tags(xaf, True)
        xaf.rename(filename)
        self.debug("Created file name : %s" % filename)
        self.info(
            "Received message %s from %s (size: %i)"
            % (basic_deliver.delivery_tag, properties.app_id, len(body))
        )
