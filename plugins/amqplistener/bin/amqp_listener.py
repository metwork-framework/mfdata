#!/usr/bin/env python3

import time
import sys
import pika
import xattrfile
import signal
import os
from mfutil import get_unique_hexa_identifier
from acquisition.listener import AcquisitionListener
from acquisition.utils import dest_dir_to_absolute
import mflog
import functools

if os.environ.get("MFDATA_CURRENT_APP_DEBUG", "0") != "1":
    # if we are not in debug mode, we silent pika.* loggers
    mflog.add_override("mylogger.*", "CRITICAL")
LOGGER = mflog.get_logger("amqplistener")


def zero_or_one_to_boolean(val):
    if val == "0" or val is False:
        return False
    if val == "1" or val is True:
        return True
    raise Exception("val: %s must be 0 or 1" % val)

def emptystring_to_none(val):
    if val ==  "":
        return None


# A lot of copy/paste from https://github.com/pika/pika/blob/master/examples/
#     asynchronous_consumer_example.py
class Consumer(object):

    def __init__(self, connection_parameters, exchange, exchange_type,
                 exchange_passive, exchange_durable,exchange_auto_delete,
                 exchange_internal, queue, queue_passive,queue_durable,
                 queue_exclusive, queue_auto_delete,routing_key,
                 prefetch_count=1, auto_ack=True, exclusive=False):
                 
        self.should_reconnect = False
        self.was_consuming = False
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._connection_parameters = connection_parameters
        self._consuming = False
        self._exchange = exchange
        self._exchange_type = exchange_type
        self._exchange_passive = exchange_passive
        self._exchange_durable = exchange_durable
        self._exchange_auto_delete = exchange_auto_delete
        self._exchange_internal = exchange_internal
        self._queue = queue
        self._queue_passive = queue_passive
        self._queue_durable = queue_durable
        self._queue_exclusive = queue_exclusive
        self._queue_auto_delete = queue_auto_delete
        self._routing_key = routing_key
        self._prefetch_count = prefetch_count
        self._auto_ack = auto_ack
        self._exclusive = exclusive

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.
        :rtype: pika.SelectConnection
        """
        LOGGER.info('Connecting to %s:%i', self._connection_parameters["host"],
                    self._connection_parameters["port"])
        params = self._connection_parameters
        return pika.SelectConnection(
            parameters=pika.ConnectionParameters(**params),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('Connection is closing or already closed')
        else:
            LOGGER.info('Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.
        :param pika.SelectConnection _unused_connection: The connection
        """
        LOGGER.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """This method is called by pika if the connection to RabbitMQ
        can't be established.
        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error
        """
        LOGGER.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.
        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reconnect necessary: %s',
                           reason)
            self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.
        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        on_channel_open callback will be invoked by pika.
        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.
        Since the channel is now open, we'll declare the exchange to use.
        :param pika.channel.Channel channel: The channel object
        """
        LOGGER.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self._exchange)

    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.
        """
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.
        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed
        """
        LOGGER.warning('Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self, exchange_name):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.
        :param str|unicode exchange_name: The name of the exchange to declare
        """
        # If name is empty, just declare the queue
        if exchange_name is None:
            self.setup_queue(self._queue)
        else:
	        LOGGER.info('Declaring exchange: %s', exchange_name)
	        # Note: using functools.partial is not required, it is demonstrating
	        # how arbitrary data can be passed to the callback when it is called
	        cb = functools.partial(
	            self.on_exchange_declareok, userdata=exchange_name)
	        self._channel.exchange_declare(
	            exchange=exchange_name,
	            exchange_type=self._exchange_type,
	            passive=self._exchange_passive,
	            durable=self._exchange_durable,
	            auto_delete=self._exchange_auto_delete,
	            internal=self._exchange_internal,
	            callback=cb)

    def on_exchange_declareok(self, _unused_frame, userdata):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.
        :param pika.Frame.Method unused_frame: Exchange.DeclareOk
            response frame
        :param str|unicode userdata: Extra user data (exchange name)
        """
        LOGGER.info('Exchange declared: %s', userdata)
        self.setup_queue(self._queue)

    def setup_queue(self, queue_name):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.
        :param str|unicode queue_name: The name of the queue to declare.
        """
        LOGGER.info('Declaring queue %s', queue_name)
        cb = functools.partial(self.on_queue_declareok, userdata=queue_name)
        self._channel.queue_declare(queue=queue_name,
                                    passive=self._queue_passive,
                                    durable=self._queue_durable,
                                    exclusive=self._queue_exclusive,
                                    auto_delete=self._queue_auto_delete,
                                    callback=cb)

    def on_queue_declareok(self, _unused_frame, userdata):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.
        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        queue_name = userdata
        if self._exchange is None:
            LOGGER.info('(Work/Task Queue declared \'{}\'.'.format(queue_name))
            self.start_consuming()
            return
        LOGGER.info('Binding %s to %s with %s', self._exchange, queue_name,
                    self._routing_key)
        cb = functools.partial(self.on_bindok, userdata=queue_name)
        self._channel.queue_bind(
            queue_name,
            self._exchange,
            routing_key=self._routing_key,
            callback=cb)

    def on_bindok(self, _unused_frame, userdata):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will set the prefetch count for the channel.
        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame
        :param str|unicode userdata: Extra user data (queue name)
        """
        LOGGER.info('Queue bound: %s', userdata)
        self.set_qos()

    def set_qos(self):
        """This method sets up the consumer prefetch to only be delivered
        one message at a time. The consumer must acknowledge this message
        before RabbitMQ will deliver another one. You should experiment
        with different prefetch values to achieve desired performance.
        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        """Invoked by pika when the Basic.QoS method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed RPC commands to start the process.
        :param pika.frame.Method _unused_frame: The Basic.QosOk response frame
        """
        LOGGER.info('QOS set to: %d', self._prefetch_count)
        self.start_consuming()

    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.
        """
        LOGGER.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self._queue, self.on_message, auto_ack=self._auto_ack,
            exclusive=self._exclusive)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.
        """
        LOGGER.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.
        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.
        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body
        """
        raise NotImplementedError("on_message must be overriden")

    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.
        :param int delivery_tag: The delivery tag from the Basic.Deliver frame
        """
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def reject_message(self, delivery_tag, requeue=False):
        LOGGER.info('Rejecting message %s', delivery_tag)
        self._channel.basic_reject(delivery_tag, requeue=requeue)

    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.
        """
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = functools.partial(
                self.on_cancelok, userdata=self._consumer_tag)
            self._channel.basic_cancel(self._consumer_tag, cb)

    def on_cancelok(self, _unused_frame, userdata):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.
        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame
        :param str|unicode userdata: Extra user data (consumer tag)
        """
        self._consuming = False
        LOGGER.info(
            'RabbitMQ acknowledged the cancellation of the consumer: %s',
            userdata)
        self.close_channel()

    def close_channel(self):
        """Call to close the channel with RabbitMQ cleanly by issuing the
        Channel.Close RPC command.
        """
        LOGGER.info('Closing the channel')
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        if not self._closing:
            self._closing = True
            LOGGER.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            LOGGER.info('Stopped')


class AmqpListener(AcquisitionListener):

    def init(self):
        self.amqp_hostname = self.get_custom_config_value("amqp_hostname",
                                                          default="localhost")
        self.amqp_virtualhost = self.get_custom_config_value(
            "amqp_virtualhost", default="/")
        self.amqp_port = self.get_custom_config_value(
            "amqp_port", default="5672", transform=int)
        # configuration exchange
        self.amqp_exchange_name = self.get_custom_config_value(
            "amqp_exchange_name", transform=emptystring_to_none)
        self.amqp_exchange_type = self.get_custom_config_value(
            "amqp_exchange_type")
        self.amqp_exchange_passive = self.get_custom_config_value(
            "amqp_exchange_passive", transform=zero_or_one_to_boolean)
        self.amqp_exchange_durable = self.get_custom_config_value(
            "amqp_exchange_durable", transform=zero_or_one_to_boolean)
        self.amqp_exchange_auto_delete = self.get_custom_config_value(
            "amqp_exchange_auto_delete", transform=zero_or_one_to_boolean)
        self.amqp_exchange_internal = self.get_custom_config_value(
            "amqp_exchange_internal", transform=zero_or_one_to_boolean)
        # configuration queue
        self.amqp_queue_name = self.get_custom_config_value(
            "amqp_queue_name")
        self.amqp_queue_passive = self.get_custom_config_value(
            "amqp_queue_passive", transform=zero_or_one_to_boolean)
        self.amqp_queue_durable = self.get_custom_config_value(
            "amqp_queue_durable", transform=zero_or_one_to_boolean)
        self.amqp_queue_exclusive = self.get_custom_config_value(
            "amqp_queue_exclusive", transform=zero_or_one_to_boolean)
        self.amqp_queue_auto_delete = self.get_custom_config_value(
            "amqp_queue_auto_delete", transform=zero_or_one_to_boolean)
        self.amqp_routing_key = self.get_custom_config_value(
            "amqp_routing_key", transform=emptystring_to_none)

        tmp = self.get_custom_config_value("dest_dir", default=None)
        self.dest_dir, _ = dest_dir_to_absolute(tmp, allow_absolute=True)

        self.amqp_prefetch_count = self.get_custom_config_value(
            "amqp_prefetch_count", default=1, transform=int)
        self.amqp_auto_ack = self.get_custom_config_value(
            "amqp_auto_ack", default="1", transform=zero_or_one_to_boolean)
        self.amqp_requeue = self.get_custom_config_value(
            "amqp_requeue", default="0", transform=zero_or_one_to_boolean)
        self.amqp_exclusive = self.get_custom_config_value(
            "amqp_exclusive", default="0", transform=zero_or_one_to_boolean)
        self.amqp_credentials_type = self.get_custom_config_value(
            "amqp_credentials_type", default="plain")
        self.amqp_credentials_username = self.get_custom_config_value(
            "amqp_credentials_username", default="guest")
        self.amqp_credentials_password = self.get_custom_config_value(
            "amqp_credentials_password", default="guest")
        if self.amqp_credentials_type != "plain":
            raise Exception("invalid amqp_credentials_type value: %s (only "
                            "plain is supported for now" %
                            self.amqp_credentials_type)
        self.consumer_args = [
            {
                "host": self.amqp_hostname,
                "port": self.amqp_port,
                "virtual_host": self.amqp_virtualhost,
                "credentials": pika.credentials.PlainCredentials(
                    self.amqp_credentials_username,
                    self.amqp_credentials_password
                )
            },
            self.amqp_exchange_name,
            self.amqp_exchange_type,
            self.amqp_exchange_passive,
            self.amqp_exchange_durable,
            self.amqp_exchange_auto_delete,
            self.amqp_exchange_internal,
            self.amqp_queue_name,
            self.amqp_queue_passive,
            self.amqp_queue_durable,
            self.amqp_queue_exclusive,
            self.amqp_queue_auto_delete,
            self.amqp_routing_key
        ]
        self.consumer_kwargs = {
            "prefetch_count": self.amqp_prefetch_count,
            "auto_ack": self.amqp_auto_ack,
            "exclusive": self.amqp_exclusive
        }
        self._sigterm_received = False
        signal.signal(signal.SIGTERM, self.__sigterm_handler)
        self._consumer = None

    def get_target_filepath(self, xaf):
        return "%s/%s" % (self.dest_dir, get_unique_hexa_identifier())

    def __sigterm_handler(self, *args):
        self.info("SIGTERM signal handled => schedulling shutdown")
        self._sigterm_received = True
        if self._consumer is not None:
            try:
                self._consumer.stop()
            except Exception:
                self.exception("exception during consumer.stop() => hard exit")
                sys.exit(1)

    def on_message(self, basic_deliver, properties, body):
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        tmp_filepath = self.get_tmp_filepath()
        with open(tmp_filepath, "wb") as f:
            f.write(body)
        xaf = xattrfile.XattrFile(tmp_filepath)
        # FIXME: other tags
        self.set_tag(xaf, "amqplistener_hostname", self.amqp_hostname,
                     add_latest=False)
        self.set_tag(xaf, "amqplistener_port", str(self.amqp_port),
                     add_latest=False)
        self._set_before_tags(xaf)
        target = self.get_target_filepath(xaf)
        res, _ = xaf.move_or_copy(target)
        if res:
            self.info("message saved in %s" % target)
        else:
            self.warning("can't save message in %s" % target)
        return res

    def _on_message(self, _unused_channel, basic_deliver, properties, body):
        res = False
        try:
            res = self.on_message(basic_deliver, properties, body)
        except Exception:
            self.exception("exception during on_message() call")
        if res:
            if not self.amqp_auto_ack:
                self._consumer.acknowledge_message(basic_deliver.delivery_tag)
        else:
            if not self.amqp_auto_ack:
                self._consumer.reject_message(basic_deliver.delivery_tag,
                                              requeue=self.amqp_requeue)

    def listen(self):
        self.info("Daemon started")
        cargs = self.consumer_args
        ckwargs = self.consumer_kwargs
        self._consumer = Consumer(*cargs, **ckwargs)
        self._consumer.on_message = self._on_message
        while not self._sigterm_received:
            try:
                self._consumer.run()
            except Exception:
                self.exception("exception during consumer.run()")
                break
            if self._consumer.should_reconnect:
                self._consumer.stop()
                self.info("Waiting 5s and reconnecting...")
                time.sleep(5)
                self._consumer = Consumer(*cargs, **ckwargs)
                self._consumer.on_message = self._on_message


if __name__ == "__main__":
    x = AmqpListener()
    x.run()
