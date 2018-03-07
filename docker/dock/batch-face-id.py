import sys, os
import datetime
import time
import face_recognition


def runFaceRecognition(trainImg,strmImg):
	benchmark = face_recognition.load_image_file(trainImg)
	testfile = face_recognition.load_image_file(strmImg)

	benchEncoding = face_recognition.face_encodings(benchmark)[0]
	testEncoding = face_recognition.face_encodings(testfile)[0]

	distance = face_recognition.face_distance([benchEncoding],testEncoding)

	return distance

