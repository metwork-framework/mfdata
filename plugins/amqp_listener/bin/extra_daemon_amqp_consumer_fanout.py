#!/usr/bin/env python3

import pika
import signal
from extra_daemon_amqp_listener.py import ExtraDaemonAmqpListener


class ExtraDaemonAmqpConsumerFanout(ExtraDaemonAmqpListener):

    plugin_name = "amqp_listener"
    daemon_name = "extra_daemon_amqp_consumer_fanout"

    def __init__(self):
        super(ExtraDaemonAmqpConsumerFanout, self).__init__()
        signal.signal(signal.SIGTERM, self.__sigintterm_handler)
        signal.signal(signal.SIGINT, self.__sigintterm_handler)

    def __sigintterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        if self.args.delete_queue_after_stop:
            self.channel.queue_delete(self.args.subscription_queue)
        self.channel.close()

    def add_extra_arguments(self, parser):
        super(ExtraDaemonAmqpConsumerFanout, self).add_extra_arguments(parser)
        parser.add_argument(
            "--subscription-queue",
            action="store",
            help="string specifying the subscription queue.",
        )

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        self._on_message(_unused_channel, basic_deliver, properties, body)

    def consume(self):
        self.channel.queue_declare(
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
        if self.connect("fanout"):
            self.consume()
            self.connection.close()


if __name__ == "__main__":
    x = ExtraDaemonAmqpConsumerFanout()
    x.run()
