import sys,os,pika,threading
import process_facetraining

class ConsumerThread(threading.Thread):
	def __init__(self, host, *args, **kwargs):
		super(ConsumerThread, self).__init__(*args, **kwargs)
		self._host = host

    # Not necessarily a method.
	def callback_func(self, channel, method, properties, body):
		print("{} received '{}'".format(self.name, body.decode()))
		id = body.decode()
		process_facetraining.process(id)

	def run(self):
		credentials = pika.PlainCredentials("guest", "guest")
		connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._host,credentials=credentials))
		channel = connection.channel()
		channel.queue_declare(queue='FaceTraining',durable='True')
		channel.basic_consume(self.callback_func, queue='FaceTraining', no_ack=True)
		print(' [*] Waiting for messages. To exit press CTRL+C')
		channel.start_consuming()

		
if __name__ == "__main__":
	threads = [ConsumerThread("orlawv027")]
	for thread in threads:
		thread.start()