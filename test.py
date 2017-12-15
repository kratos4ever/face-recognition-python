#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='alerts')

channel.basic_publish(body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()