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

def updateStatusAndResult(data):
	sql = "  insert into imageprocess_status (imagebagid, imageprocessorid, processedon, status, result,num_faces) VALUES (%s,1,now(),%s,%s,%s) "
	cur = db.cursor()
	cur.execute(sql,(data.id,data.status,data.result,data.num_faces))

	db.commit()
	cur.close()


### GETS THE UNPROCESSED RECORDS FROM STREAM_IMG TABLE
def getUnProcessedTrainingImage(id):

	sql = " select employeeid, imagefile, date_format(createdon,'%m%d%Y_%H%i%S') as time from imagebag where imagebagid = " + id
	print("SQL:" ,sql)
	
	nrows = cur.execute(sql)
	streamData = None
	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			empid = data[0]
			image = data[1]
			capture_time = data[2]
			status = "N"
			streamData = FaceStreamData(empid,id,capture_time,image,status)

		streamData.printData()
	#cur.close()
	return streamData

### gets a single training image per lanid (from the un processed records in the stream_img table) from the train_img table
def loadTrainingImages(empid):

	sql = " select b.imagebagid, b.imagefile, date_format(b.createdon,'%m%d%Y_%H%i%S') as time from imagebag b, (select max(imagebagid) as id from imagebag a where a.employeeid = '"+empid+"' and imagesourceid = '2') a where a.id = b.imagebagid  "
	trainData = None
	cur = db.cursor()
	print(sql)
	nrows = cur.execute(sql)
	if(nrows > 0):
		resultset = cur.fetchall()
		for data in resultset:
			id = data[0]
			image = data[1]
			capture_time = data[2]

			trainData = FaceTrainData(empid,id,capture_time,image)

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

	print("\n\n==========\nPROCESSING IMAGE: ",strmImgPath)

	#call face recognition for this image - this can be done as parallel for?
	try:
		testImg = face_recognition.load_image_file(strmImgPath)
		testEnc = face_recognition.face_encodings(testImg)
		

		if(len(testEnc) == 0):
			data.result = "FAIL_NO_FACES_FOUND"
			data.status = "F"
			data.num_faces = 0
		elif(len(testEnc) == 1):
			data.num_faces = 1
			data.result = "SUCCESS"
			data.status = "Y"
			
			if trainData is None:
				#As there is no previous training image - treat it as a success if there is only one face 
			elif:
				#Create all the files
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
					if(testResults[0] <0.6):
						data.result = "SUCCESS_MATCH_PREV_TRAINING"
				except Exception as e: #Have to catch all - do nothing - if the prev training image is bad, doesn't matter for the new training image
					print("error while encoding the previous training/benchmark image for empid:",data.lanid , ". Error:",str(e))


		elif(len(testEnc) > 1):
			data.status = "F"
			data.result = "FAIL_MULTIPLE_FACES"

		data.status = "Y"
		data.printData()

	except Exception as e: #catch all exception for this record
		print("error while encoding the training image for emp-id:",data.lanid , ", imagebagid:",data.id , ". Error:",str(e))
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
		empid = streamData.lanid
		print("=========\ntrying to load training data for employeeid : " + empid +"\n==============")
		trainData = loadTrainingImages(empid)
		
		runImageProcessing(streamData,trainData)

		updateStatusAndResult(streamData)

	except Exception as e:
		print("Error while processing message:", id, +". Error:",str(e))
	

	
	#for the lanid, then write the status accordingly
