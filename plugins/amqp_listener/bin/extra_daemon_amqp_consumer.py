#!/usr/bin/env python3

import argparse
import pika
import signal
import sys
import os
import mfutil
import xattrfile
from acquisition.listener import AcquisitionListener


def parse_args(parser, commands):
    split_argv = [[]]
    for c in sys.argv[1:]:
        if c in commands.choices:
            split_argv.append([c])
        else:
            split_argv[-1].append(c)
    # Initialize namespace
    args = argparse.Namespace()
    for c in commands.choices:
        setattr(args, c, None)
    # Parse each command
    parser.parse_args(split_argv[0], namespace=args)  # Without command
    for argv in split_argv[1:]:  # Commands
        n = argparse.Namespace()
        setattr(args, argv[0], n)
        parser.parse_args(argv, namespace=n)
    return args


def add_common_arg(parser):
    parser.add_argument('--broker-hostname', action='store',
                        default='127.0.0.1',
                        help='the hostname or IP address of the remote broker. Defaults to localhost')
    parser.add_argument('--broker-port', action='store', default=5672, type=int,
                        help='the network port of the server host to connect to. Defaults to 1883.')
    parser.add_argument('--credential-username', action='store', default=None,
                        help='The username to authenticate with.')
    parser.add_argument('--credential-password', action='store', default=None,
                        help='The password to authenticate with.')
    parser.add_argument('--subscription-exchange', action='store',
                        help='string specifying the subscription exchange.')
    parser.add_argument('--delete-queue-after-stop', action='store_true',
                        help='delete the queue after stop process.')
    parser.add_argument('--dest-dir', action='store',
                        help='destination directory of the file made from the MQTT message')
    parser.add_argument('--tmp-suffix', action='store', default='t',
                        help='temporary file suffix. Default t')


def get_argument_parser():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(title='subscription-exchange-type',
                                     help='string specifying the subscription exchange type.')
    cmd_topic_parser = commands.add_parser('topic', help='broadcasts the message with routing key selected')
    cmd_fanout_parser = commands.add_parser('fanout',
                                            help='broadcasts all the messages it receives to all the queues it knows')
    cmd_fanout_parser.add_argument('--subscription-queue', action='store', required=True,
                                   help='string specifying the subscription queue.')

    add_common_arg(cmd_fanout_parser)
    add_common_arg(cmd_topic_parser)
    cmd_topic_parser.add_argument('--routing-topic-keys', action='store', default=['*'], nargs='*',
                                  help='if exchange is topic this argument represent thr topic-key. Default all topics')
    return parser, commands


def get_arguments():
    parser, commands = get_argument_parser()
    args = parse_args(parser, commands)
    print(args)
    if args.topic is not None or args.fanout is not None:
        return args
    else:
        os.system('%s --help' % sys.argv[0])
        self.error('%s: error: a string specifying the subscription exchange type is required' % sys.argv[0])
        exit(0)


class ExtraDaemonAmqpConsumer(AcquisitionListener):

    plugin_name = "amqp_listener"
    daemon_name = "extra_daemon_amqp_consumer"

    channel = None
    connection = None
    message_number = 1

    subscription_exchange_type = None
    broker_hostname = None
    broker_port = None
    credential_username = None
    credential_password = None
    subscription_exchange = None
    subscription_queue = None
    delete_queue_after_stop = False
    routing_topic_keys = []
    dest_dir = None
    tmp_suffix = None

    def __init__(self):
        """
        Create a new instance of the consumer class
        """
        super(ExtraDaemonAmqpConsumer, self).__init__()
        signal.signal(signal.SIGTERM, self.__sigterm_handler)
        signal.signal(signal.SIGINT, self.__sigterm_handler)

    def __sigterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        if self.delete_queue_after_stop:
            self.channel.queue_delete(self.subscription_queue)
        self.channel.close()

    def connect(self):
        """"This method connects to RabbitMQ, returning true when the connection
        is established.

        :return: True if Ok else False
        """
        if self.credential_username is not None and self.credential_password is not None:
            credentials = pika.PlainCredentials(self.credential_username,
                                                self.credential_password)
            parameters = pika.ConnectionParameters(host=self.broker_hostname,
                                                   port=self.broker_port,
                                                   credentials=credentials)
        else:
            parameters = pika.ConnectionParameters(host=self.broker_hostname,
                                                   port=self.broker_port)
        try:
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            self.channel.exchange_declare(exchange=self.subscription_exchange,
                                          exchange_type=self.subscription_exchange_type)
        except Exception as e:
            self.error(format(e))
            return False
        except:
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
        filepath = os.path.join(self.dest_dir, basename)
        tmp_filepath = '.'.join((filepath, self.tmp_suffix))
        self.debug("Created tmp file name : %s" % (tmp_filepath))
        with open(tmp_filepath, "w") as fichier:
            fichier.write(str(body))
        xaf = xattrfile.XattrFile(tmp_filepath)
        self.set_tag(xaf, 'amqp_listener.subscription_exchange', self.subscription_exchange)
        self.set_tag(xaf, 'amqp_listener_subscription_exchange_type', self.subscription_exchange_type)
        if self.subscription_exchange_type == 'topic':
            self.set_tag(xaf, 'amqp_listener_subscription_routing_keys', self.routing_topic_keys)
            self.set_tag(xaf, 'amqp_listener_received_routing_key', basic_deliver.routing_key)
        elif self.subscription_exchange_type == 'fanout':
            self.set_tag(xaf, 'amqp_listener_subscription_queue', self.subscription_queue)
        self.set_tag(xaf, 'amqp_listener_broker_hostname', self.broker_hostname)
        self.set_tag(xaf, 'amqp_listener_broker_port', str(self.broker_port))
        xaf.rename(filepath)
        self.debug("Created file name : %s" % (filepath))
        self.info('Received message %s from %s : %s' % (basic_deliver.delivery_tag, properties.app_id, body))

    def consume(self):
        if self.subscription_exchange_type == u'fanout':
            result = self.channel.queue_declare(self.subscription_queue, exclusive=False)
            self.channel.queue_bind(queue=self.subscription_queue, exchange=self.subscription_exchange)
            self.info(' [*] Waiting for %s on queue %s. To exit press CTRL+C' % (
                self.subscription_exchange,
                self.subscription_queue))
        elif self.subscription_exchange_type == 'topic':
            result = self.channel.queue_declare('', exclusive=False)
            self.subscription_queue = result.method.queue
            for key in self.routing_topic_keys:
                self.channel.queue_bind(exchange=self.subscription_exchange, queue=self.subscription_queue,
                                        routing_key=key)
            self.info(' [*] Waiting for %s on queue %s and topics %s. To exit press CTRL+C' % (
                self.subscription_exchange,
                self.subscription_queue,
                self.routing_topic_keys))

        self.channel.basic_consume(queue=self.subscription_queue, on_message_callback=self.on_message, auto_ack=True)

        self.channel.start_consuming()

    def listen(self):
        args = get_arguments()
        if args.fanout is not None:
            self.subscription_exchange_type = 'fanout'
            self.broker_hostname = args.fanout.broker_hostname
            self.broker_port = args.fanout.broker_port
            self.credential_username = args.fanout.credential_username
            self.credential_password = args.fanout.credential_password
            self.subscription_exchange = args.fanout.subscription_exchange
            self.subscription_queue = args.fanout.subscription_queue
            self.delete_queue_after_stop = args.fanout.delete_queue_after_stop
            self.dest_dir = args.fanout.dest_dir
            self.tmp_suffix = args.fanout.tmp_suffix

        elif args.topic is not None:
            self.subscription_exchange_type = 'topic'
            self.broker_hostname = args.topic.broker_hostname
            self.broker_port = args.topic.broker_port
            self.credential_username = args.topic.credential_username
            self.credential_password = args.topic.credential_password
            self.subscription_exchange = args.topic.subscription_exchange
            self.delete_queue_after_stop = args.topic.delete_queue_after_stop
            self.routing_topic_keys = args.topic.routing_topic_keys
            self.dest_dir = args.topic.dest_dir
            self.tmp_suffix = args.topic.tmp_suffix

        if self.connect():
            self.consume()
            self.connection.close()


if __name__ == "__main__":
    x = ExtraDaemonAmqpConsumer()
    x.run()
