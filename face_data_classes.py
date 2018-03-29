import math

class FaceStreamData:

	#stores the stream_img table data 
	def __init__(self,lanid,empid,id,capture_time,image,status):
		self.lanid = lanid
		self.id = id
		self.empid = empid
		self.capture_time = capture_time
		self.image = image
		self.status = status
		self.result = "Processing"
		self.resultCode = 0
		self.ip="NONE"
		self.systemname="NONE"
		self.accuracy = 0.0
		self.num_faces = 0
		self.distance = 1

	def calcAccuracy(self):
		x = self.distance
		# self.accuracy = 98.21546 - (9.480826/-4.050239)*(1 - math.exp(+4.050239*x))  #initial eqn gives 0.66 as 66 percent, 0.72 as 57 percent
		 self.accuracy = 99.98174 - (16.45671/-2.444457)*(1 - math.exp(+2.444457*x))

		if(self.accuracy > 100):
			self.accuracy = 100
		elif(self.accuracy < 0):
			self.accuracy = 0

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
