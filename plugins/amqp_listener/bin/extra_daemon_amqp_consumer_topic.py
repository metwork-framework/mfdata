#!/usr/bin/env python3

import pika
import signal
from extra_daemon_amqp_listener.py import ExtraDaemonAmqpListener


def _add_extra_tags_func(
    self, xaf, _unused_channel, basic_deliver, properties, body
):
    self.set_tag(
        xaf,
        "amqp_listener_subscription_routing_keys",
        str(self.args.subscription_routing_topic_keys),
    )
    self.set_tag(
        xaf, "amqp_listener_received_routing_key", basic_deliver.routing_key
    )


class ExtraDaemonAmqpConsumerTopic(ExtraDaemonAmqpListener):

    plugin_name = "amqp_listener"
    daemon_name = "extra_daemon_amqp_consumer_topic"
    subscription_queue = None

    def __init__(self):
        super(ExtraDaemonAmqpConsumerTopic, self).__init__()
        signal.signal(signal.SIGTERM, self.__sigintterm_handler)
        signal.signal(signal.SIGINT, self.__sigintterm_handler)

    def __sigintterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        self.channel.queue_delete(self.subscription_queue)
        self.channel.close()

    def add_extra_arguments(self, parser):
        super(ExtraDaemonAmqpConsumerTopic, self).add_extra_arguments(parser)
        parser.add_argument(
            "--subscription-routing-topic-keys",
            action="store",
            default=["*"],
            nargs="+",
            help="if exchange is topic this argument represent thr topic-key."
            "Default all topics",
        )

    def on_message(self, *args, **kwargs):
        kwargs['add_extra_tags_func'] = _add_extra_tags_func
        self._on_message(*args, **kwargs)

    def consume(self):
        result = self.channel.queue_declare("", exclusive=False)
        self.subscription_queue = result.method.queue
        for key in self.args.subscription_routing_topic_keys:
            self.channel.queue_bind(
                exchange=self.args.subscription_exchange,
                queue=self.subscription_queue,
                routing_key=key,
            )
            self.info(
                " [*] Waiting for %s on queue %s and topics %s."
                "To exit press CTRL+C"
                % (
                    self.args.subscription_exchange,
                    self.subscription_queue,
                    self.args.subscription_routing_topic_keys,
                )
            )

        self.channel.basic_consume(
            queue=self.subscription_queue,
            on_message_callback=self.on_message,
            auto_ack=True,
        )

        self.channel.start_consuming()

    def listen(self):
        if self.connect("topic"):
            self.consume()
            self.connection.close()


if __name__ == "__main__":
    x = ExtraDaemonAmqpConsumerTopic()
    x.run()
