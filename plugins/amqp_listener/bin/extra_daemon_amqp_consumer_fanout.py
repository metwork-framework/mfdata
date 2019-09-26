#!/usr/bin/env python3

import pika
import signal
import os
import mfutil
import xattrfile
from acquisition.listener import AcquisitionListener


class ExtraDaemonAmqpConsumerFanout(AcquisitionListener):

    plugin_name = "amqp_listener"
    daemon_name = "extra_daemon_amqp_consumer_fanout"
    subscription_exchange_type = "fanout"
    channel = None
    connection = None
    message_number = 1

    def __init__(self):
        """
        Create a new instance of the consumer class
        """
        super(ExtraDaemonAmqpConsumerFanout, self).__init__()
        signal.signal(signal.SIGTERM, self.__sigterm_handler)
        signal.signal(signal.SIGINT, self.__sigterm_handler)

    def __sigterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        if self.args.delete_queue_after_stop:
            self.channel.queue_delete(self.subscription_queue)
        self.channel.close()

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
            "--subscription-queue",
            action="store",
            help="string specifying the subscription queue.",
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

    def connect(self):
        if self.args.credential_username is not None \
                and self.args.credential_password is not None:
            credentials = pika.PlainCredentials(
                self.args.credential_username, self.args.credential_password
            )
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
                exchange_type=self.subscription_exchange_type,
            )
        except Exception as e:
            self.error(format(e))
            return False
        except Exception:
            self.error("Error unknown")
            return False
        else:
            return True

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param _unused_channel: The channel object
        :param basic_deliver: basic_deliver method
        :param properties: properties
        :param body: The message body
        :return:
        """
        basename = mfutil.get_unique_hexa_identifier()
        self.debug("basename: %s" % (basename))
        filename = os.path.join(self.args.dest_dir, basename)
        tmp_filename = ".".join((filename, self.args.tmp_suffix))
        self.debug("Created tmp file name : %s" % tmp_filename)
        with open(tmp_filename, "w") as fichier:
            fichier.write(str(body))
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
        xaf.rename(filename)
        self.debug("Created file name : %s" % filename)
        self.info(
            "Received message %s from %s : %s"
            % (basic_deliver.delivery_tag, properties.app_id, body)
        )

    def consume(self):
        result = self.channel.queue_declare(
            self.args.subscription_queue, exclusive=False
        )
        self.channel.queue_bind(
            queue=self.args.subscription_queue,
            exchange=self.args.subscription_exchange,
        )
        self.info(
            " [*] Waiting for %s on queue %s. To exit press CTRL+C"
            % (self.args.subscription_exchange, self.args.subscription_queue)
        )

        self.channel.basic_consume(
            queue=self.args.subscription_queue,
            on_message_callback=self.on_message,
            auto_ack=True,
        )

        self.channel.start_consuming()

    def listen(self):
        if self.connect():
            self.consume()
            self.connection.close()


if __name__ == "__main__":
    x = ExtraDaemonAmqpConsumerFanout()
    x.run()
