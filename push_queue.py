import pika
import json
from face_data_classes import FaceStreamData


def pushToQueue(streamData,queueName):

	resultMessage = dict()
	resultMessage['lanid']=streamData.lanid
	if (streamData.status == "Y"):
		resultMessage['status']="SUCCESS"
	else:
		resultMessage['status']="FAILURE"
	resultMessage['imagebagid']=streamData.id
	resultMessage['result']=streamData.result

	messageString = json.dumps(resultMessage)

	credentials = pika.PlainCredentials("admin", "p@ssw0rd")
	connection = pika.BlockingConnection(pika.ConnectionParameters(host="murcnvepachedu",credentials=credentials))
	channel = connection.channel()
	channel.queue_declare(queue=queueName,durable=True)
	channel.basic_publish(exchange='',routing_key=queueName,body=messageString)
	print(" [x] Sent " + messageString)
	connection.close()


#streamData = FaceStreamData("NA\nvep5898","100405898",12333,'time','img','Y')
##streamData.result = "NO_FACES_FOUND"
#pushToQueue(streamData,"FaceTrainStatus")

