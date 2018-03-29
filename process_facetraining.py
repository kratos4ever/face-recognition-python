#program to run like a schduled task in docker, just prints the current time to stdout
import sys,os
import time
import datetime
import MySQLdb
import json
from face_data_classes import FaceStreamData
from face_data_classes import FaceTrainData
import face_recognition
import push_queue
import const

### INITIALIZES THE DB CONNECTION TO MYSQL
def initDbConnection():
	global db
	db = MySQLdb.connect(host="orlawv027",user="biometric-user",passwd="B10M37R1K5",db="biometrics")
	global cur
	cur = db.cursor()

def loadConfig():
	global resultCodes
	resultCodes = {}

	cur = db.cursor()
	sql = " select result_id, result_desc from results_master "
	nrows = cur.execute(sql)
	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			resultCodes[data[1]]=data[0]

	cur.close()	

def updateStatusAndResult(data):
	sql = "  insert into imageprocess_status (imagebagid, imageprocessorid, processedon, status, result,num_faces,result_id,distance,accuracy) VALUES (%s,1,now(),%s,%s,%s,%s,%s,%s) "
	cur = db.cursor()
	cur.execute(sql,(data.id,data.status,data.result,data.num_faces,data.resultCode,data.distance,data.accuracy))

	db.commit()
	cur.close()


### GETS THE UNPROCESSED RECORDS FROM STREAM_IMG TABLE
def getUnProcessedTrainingImage(id):

	sql = " select a.empid, a.imagefile, date_format(a.createdon,'%m%d%Y_%H%i%S') as time, b.lanid, c.ipaddress as ip, c.systemname  from imagebag a, employee b, systemenviornment c where a.empid = b.empid and a.systemenviornmentid = c.systemenviornmentid and imagebagid = " + id
	#print("SQL:" ,sql)
	
	nrows = cur.execute(sql)
	streamData = None
	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			empid = data[0]
			image = data[1]
			capture_time = data[2]
			lanid = data[3]
			status = "N"
			streamData = FaceStreamData(lanid,empid,id,capture_time,image,status)
			streamData.ip = data[4]
			streamData.system = data[5]
		streamData.printData()
	#cur.close()
	return streamData

### gets a single training image per lanid (from the un processed records in the stream_img table) from the train_img table
def loadTrainingImages(empid,lanid):

	sql = " select b.imagebagid, b.imagefile, date_format(b.createdon,'%m%d%Y_%H%i%S') as time from imagebag b, (select max(a.imagebagid) as id from imagebag a,imageprocess_status c, results_master d  where  a.imagesourceid = 2 and a.empid = "+str(empid)+" and a.imagebagid = c.imagebagid and  c.result_id = d.result_id and d.result_desc = '"+SUCCESS+"')  e where e.id = b.imagebagid  "
	trainData = None
	cur = db.cursor()
	#print(sql)
	nrows = cur.execute(sql)
	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			id = data[0]
			image = data[1]
			capture_time = data[2]

			trainData = FaceTrainData(lanid,empid,id,capture_time,image)

	cur.close()
	
	return trainData


### RUN THE image processing pipelien for facial recognition
def runImageProcessing(data, trainData):
	#delete the existing directory?
	#create a directory with lanid name in the data directory
	lanidDir = "./data/"+data.id
	trainDir = "benchmark"
	streamDir = "unknown"
	if not os.path.exists(lanidDir):
		os.makedirs(lanidDir)

	if not os.path.exists(os.path.join(lanidDir,trainDir)):
		os.makedirs(os.path.join(lanidDir,trainDir))

	if not os.path.exists(os.path.join(lanidDir,streamDir)):
		os.makedirs(os.path.join(lanidDir,streamDir))


	#### START PROCESSING RECORDS FOR THIS EMP
	strmImgPath = os.path.join(lanidDir,streamDir,str(data.id)+".jpg")
	strmImg = open(strmImgPath,"wb")
	strmImg.write(data.image)
	strmImg.close()

	#print("\n\n==========\nPROCESSING IMAGE: ",strmImgPath)

	#call face recognition for this image - this can be done as parallel for?
	try:
		testImg = face_recognition.load_image_file(strmImgPath)
		testEnc = face_recognition.face_encodings(testImg)
		

		if(len(testEnc) == 0):
			data.result = NO_FACES_FOUND
			data.status = "F"
			data.resultCode = resultCodes[NO_FACES_FOUND]
			data.num_faces = 0
		elif(len(testEnc) == 1):
			data.num_faces = 1
			data.result = SUCCESS
			data.resultCode = resultCodes[SUCCESS]
			data.status = "Y"

			if trainData is None:
				#As there is no previous training image - treat it as a success if there is only one face 
			else:
				#Create prev training files and check for likeness with prev training image
				trainImgPath = os.path.join(lanidDir,trainDir,data.lanid+".jpg")
				trainImg = open(trainImgPath,"wb")
				trainImg.write(trainData.image)
				trainImg.close()

				#just try to do the check on the fly after the folder check
				######## DO A MULTIPLE FACE CHECK - in the training batch process, which is what it should do??
				try:
					benchImg = face_recognition.load_image_file(trainImgPath)
					benchEnc = face_recognition.face_encodings(benchImg)[0] 

					testResults = face_recognition.face_distance(benchEnc,testEnc)
					data.distance = testResults[0]
				except Exception as e: #Have to catch all - do nothing - if the prev training image is bad, doesn't matter for the new training image
					print("error while encoding the previous training/benchmark image for lanid:",data.lanid , ". Error:",str(e))
			data.calcAccuracy()

		elif(len(testEnc) > 1):
			data.status = "F"
			data.result = MULTIPLE_FACES
			data.resultCode = resultCodes[MULTIPLE_FACES]
			data.num_faces = len(testEnc)

		data.printData()

	except Exception as e: #catch all exception for this record
		print("error while encoding the training image for lanid:",data.lanid , ", imagebagid:",data.id , ". Error:",str(e))
		data.result = "ERROR_PROCESSING_IMG"
		data.status = "F"
		return
		#delete the image as the processing is done
		

### main function
def process(id):
	print("Starting the FaceTraining Message processing for imagebagid:",id)
	
	try:
		#init - connection to the mysql server - no externalizing as of now
		initDbConnection()

	except MySQLdb.Error as e:
		#### if cur is null or db is null then DB connection failed -> print error/email and exit
		print("Error in getting connection:",e)
		sys.exit(1)


	try:
		#run the query to get the images from stream_img table, set into map<lanid,list<object:lanid,img,capture_time,id,status,etc>>	
		streamData = getUnProcessedTrainingImage(id)

		if(streamData is None):
			print("No records found for processing, exiting")
			sys.exit(0)

		#Get a list of unique lanids from the above query and get the training image for each. set in a map<lanid,<object:lanid,id,image>>
		lanid = streamData.lanid
		empid = streamData.empid
		trainData = loadTrainingImages(empid,lanid)
		
		loadConfig()

		runImageProcessing(streamData,trainData)

		updateStatusAndResult(streamData)
		
		push_queue.pushToQueue(streamData,"FaceTrainStatus")

	except Exception as e:
		print("Error while processing message:", id, ". Error:",str(e))
	

	
	#for the lanid, then write the status accordingly
