#program to run like a schduled task in docker, just prints the current time to stdout
import sys,os
import time
import datetime
import MySQLdb
from face_data_classes import FaceStreamData
from face_data_classes import FaceTrainData
import face_recognition 

### INITIALIZES THE DB CONNECTION TO MYSQL
def initDbConnection():
	global db
	db = MySQLdb.connect(host="orlawv027",user="biometric-user",passwd="B10M37R1K5",db="biometrics")
	global cur
	cur = db.cursor()

def updateStatusAndResult(recList):
	sql = " update stream_img set status = %s, result = %s,num_faces = %s, processed_time = now() where id = %s "
	cur = db.cursor()
	for data in recList:		
		cur.execute(sql,(data.status,data.result,data.num_faces,data.id))

	db.commit()
	cur.close()


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
	#cur.close()
	return

def setStatusAndResultForAllRecs(recList,result,status):
	for data in recList:
		data.result = result
		data.status = status
	return

### gets a single training image per lanid (from the un processed records in the stream_img table) from the train_img table
def loadTrainingImages():
	global faceTrainMap
	faceTrainMap = {}
	lanIdClause = str(faceStrmLanIdSet).replace("{","").replace("}","")

	sql = " select a.lan_id,a.id,date_format(a.capture_time,'%m%d%Y_%H%i%S') as time,a.image from train_img a, (select lan_id, max(id) as id from train_img where lan_id in ("+lanIdClause+") group by lan_id) b where a.id = b.id "

	cur = db.cursor()
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
	cur.close()


### RUN THE image processing pipelien for facial recognition
def runImageProcessingForLanId(lanid, recList, trainData):
	#delete the existing directory?
	#create a directory with lanid name in the data directory
	lanidDir = "./data/"+lanid
	trainDir = "benchmark"
	streamDir = "unknown"
	if not os.path.exists(lanidDir):
		os.makedirs(lanidDir)

	if not os.path.exists(os.path.join(lanidDir,trainDir)):
		os.makedirs(os.path.join(lanidDir,trainDir))

	if not os.path.exists(os.path.join(lanidDir,streamDir)):
		os.makedirs(os.path.join(lanidDir,streamDir))

	#Create all the files
	trainImgPath = os.path.join(lanidDir,trainDir,lanid+".jpg")
	trainImg = open(trainImgPath,"wb")
	trainImg.write(trainData.image)
	trainImg.close()

	#just try to do the check on the fly after the folder check
	######## DO A MULTIPLE FACE CHECK - in the training batch process, which is what it should do??
	try:
		benchImg = face_recognition.load_image_file(trainImgPath)
		benchEnc = face_recognition.face_encodings(benchImg)[0] ## HANDLE MULTIPLE FACES IN TRAINING IMG - ERROR OUT FOR THE LANID. ALSO HANDLE NO FACES ETC
	except: #Have to catch all - get out
		print("error while encoding the training/benchmark image for lanid:",lanid)
		setResultForAllRecs(recList,"ERROR_PROCESSING_TRAIN_IMG","N")


	#### START PROCESSING RECORDS FOR THIS EMP
	for rec in recList:
		strmImgPath = os.path.join(lanidDir,streamDir,str(rec.id)+".jpg")
		strmImg = open(strmImgPath,"wb")
		strmImg.write(rec.image)
		strmImg.close()

		print("\n\n==========\nPROCESSING IMAGE: ",strmImgPath)

		#call face recognition for this image - this can be done as parallel for?
		try:
			testImg = face_recognition.load_image_file(strmImgPath)
			testEnc = face_recognition.face_encodings(testImg)
			

			if(len(testEnc) == 0):
				rec.result = "NO_FACES_FOUND"
				rec.num_faces = 0
			elif(len(testEnc) == 1):
				rec.num_faces = 1
				testResults = face_recognition.face_distance(benchEnc,testEnc)
				if(testResults[0] <0.6):
					rec.result = "SUCCESS"
				else:
					rec.result = "UNKNOWN_PERSON"
			elif(len(testEnc) > 1):
				testResults = face_recognition.face_distance(benchEnc,testEnc)
				rec.num_faces = len(testEnc)
				for rs in testResults:
					if(rs < 0.6):
						rec.result = "SUCCESS_MULTIPLE_FACES"
						break;
				if(rec.result != "SUCCESS_MULTIPLE_FACES"):
					rec.result = "UNKNOWN_MULTIPLE_FACES"

			rec.status = "Y"
			rec.printData()

		except: #catch all exception for this record
			print("error while encoding the streaming image for lanid:",lanid , ", id:",rec.id)
			rec.result = "ERROR_PROCESSING_IMG"
			rec.status = "F"

### main function
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

		print("=========\nProcessing Images\n==============")
		#for each lanid in the stream_img result list, check if there is a training image, if there is, do the facial recog for each record 
		for lanid in faceStrmLanIdSet:
			recList = faceStrmMap[lanid]

			if(lanid in faceTrainMap):
				trainData = faceTrainMap[lanid]
				#save the training and streaming images for processing.
				runImageProcessingForLanId(lanid,faceStrmMap[lanid],trainData)
			else:
				#set the status for all the ids in the list for the lanid from faceStrmMap as "NO_TRAINING_IMAGE"
				setStatusAndResultForAllRecs(recList,"NO_TRAINING_IMAGE","N")

			#processing done for the lan id, update the status- set pending flag to false
			updateStatusAndResult(recList)
	
	except Error as e:
		print("Error while processing images:",e)
	

	
	#for the lanid, then write the status accordingly


if __name__ == '__main__':
	main()	