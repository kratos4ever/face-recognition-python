class FaceStreamData:

	#stores the stream_img table data 
	def __init__(self,lanid,empid,id,capture_time,image,status):
		self.lanid = lanid
		self.id = id
		self.empid = empid
		self.capture_time = capture_time
		self.image = image
		self.status = status
		self.result = "PROCESSING"
		self.ip="NONE"
		self.systemname="NONE"
		self.accuracy = 0.0
		self.num_faces = 0

	def printData(self):
		print("Lan_ID:",self.lanid,", capture_time:",self.capture_time,",status:",self.status,",result:",self.result, ", num_faces:",self.num_faces)



class FaceTrainData:

	#stores the train_img table data
	def __init__(self,lanid,empid,id,capture_time,image):
		self.lanid = lanid
		self.id = id
		self.empid = empid
		self.capture_time = capture_time
		self.image = image


	def printData(self):
		print("Lan_ID:",self.lanid)
