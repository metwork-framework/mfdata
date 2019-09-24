import pika

# Set credentials
credentials = pika.PlainCredentials('admin', 'admin')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host_serv, credentials=credentials))

connection = None

try:
    # Connect to RabbitMQ broker
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="and-mf-metgate-ci.akka.eu", port=5672, credentials=credentials))

    channel = connection.channel()

    # Create the queue declared in the amqp_consumer_subscription_queue MFDATA configuration, e.g. 'my_queue'
    channel.queue_declare(queue='my_queue', exclusive=False)

    # Enabled delivery confirmations
    # - see https://pika.readthedocs.io/en/stable/examples/blocking_publish_mandatory.html
    # - see https://pika.readthedocs.io/en/stable/examples/blocking_delivery_confirmations.html
    channel.confirm_delivery()

    # Set the exchange name declare in the amqp_consumer_subscription_exchange MFDATA configuration, e.g. 'test'
    exchange = "test"
    # Set the content of the message, in this example, we want to send an xml content
    message = "<notification>message from AMQP 0.9.1 client</notification>"
    # Publish th message
    # (see https://pika.readthedocs.io/en/stable/modules/channel.html?highlight=basic_publish#pika.channel.Channel.basic_publish)
    return_code = channel.basic_publish(exchange=exchange,
                                        routing_key='my_queue',
                                        body=message,
                                        properties=pika.BasicProperties(content_type='application/xml',
                                                                        delivery_mode=1),
                                        mandatory=True)
    if return_code:
        print('Message was published (ACK)')
    else:
        print('Message was returned (NACK)')

except Exception as e:
    print(e)
finally:
    if connection is not None:
        connection.close()
