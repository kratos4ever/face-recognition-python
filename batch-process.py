#program to run like a schduled task in docker, just prints the current time to stdout
import sys,os
import time
import datetime
import MySQLdb
import smtplib
from face_data_classes import FaceStreamData
from face_data_classes import FaceTrainData

### INITIALIZES THE DB CONNECTION TO MYSQL
def initDbConnection():
	global db
	db = MySQLdb.connect(host="localhost",user="biometric-user",passwd="B10M37R1K5",db="biometrics")
	global cur
	cur = db.cursor()


### GETS THE UNPROCESSED RECORDS FROM STREAM_IMG TABLE
def getUnProcessedStreamImages():

	sql = " select lan_id,date_format(capture_time,'%m%d%Y_%H%i%S') as time, image,id  from stream_img where status = 'N' order by lan_id,id "
	nrows = cur.execute(sql)
	
	global faceStrmLanIdSet 
	global faceStrmMap
	faceStrmMap = {}
	faceStrmLanIdSet = set()

	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			lanid = data[0]
			capture_time = data[1]
			image = data[2]
			id = data[3]
			status = "N"
			streamData = FaceStreamData(lanid,id,capture_time,image,status)
			
			faceStrmLanIdSet.add(lanid)

			if lanid in faceStrmMap:
				faceStrmMap[lanid].append(streamData)
			else:
				imgDataArray = []
				imgDataArray.append(streamData)
				faceStrmMap[lanid]=imgDataArray

		print(faceStrmLanIdSet)
		print(faceStrmMap)
	return


### gets a single training image per lanid (from the un processed records in the stream_img table) from the train_img table
def loadTrainingImages():
	global faceTrainMap
	faceTrainMap = {}
	lanIdClause = str(faceStrmLanIdSet).replace("{","").replace("}","")

	sql = " select a.lan_id,a.id,date_format(a.capture_time,'%m%d%Y_%H%i%S') as time,a.image from train_img a, (select lan_id, max(id) as id from train_img where lan_id in ("+lanIdClause+") group by lan_id) b where a.id = b.id "

	print(sql)
	nrows = cur.execute(sql)
	print(nrows)
	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			lanid = data[0]
			id = data[1]
			capture_time = data[2]
			image = data[3]

			trainData = FaceTrainData(lanid,id,capture_time,image)
			faceTrainMap[lanid] = trainData #There will be only one training data per image. For any other pipeline, change this to a list?

		print(faceTrainMap)


def main():
	print("Starting the batch-process iteration:")
	
	try:
		#init - connection to the mysql server - no externalizing as of now
		initDbConnection()

	except MySQLdb.Error as e:
		#### if cur is null or db is null then DB connection failed -> print error/email and exit
		print("Error in getting connection:",e)
		sys.exit(1)


	try:
		#run the query to get the images from stream_img table, set into map<lanid,list<object:lanid,img,capture_time,id,status,etc>>	
		getUnProcessedStreamImages()

		if(faceStrmLanIdSet is None or len(faceStrmLanIdSet) == 0):
			print("No records found for processing, exiting")
			sys.exit(0)

		#Get a list of unique lanids from the above query and get the training image for each. set in a map<lanid,<object:lanid,id,image>>
		print("=========\ntrying to load training data\n==============")
		loadTrainingImages()
	
	except Error as e:
		print("Error while processing images:",e)
	

	#for each lanid in the stream_img result list, check if there is a training image, if there is, do the facial recog for each record 
	#for the lanid, then write the status accordingly


if __name__ == '__main__':
	main()	