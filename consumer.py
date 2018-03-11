#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='murcnvepachedu',user='admin',password='p@ssw0rd'))
channel = connection.channel()


channel.queue_declare(queue='FaceTraining')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback, queue='FaceTraining', no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
