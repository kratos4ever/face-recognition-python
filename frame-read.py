# facerec.py
import cv2, sys, numpy, os
import datetime
import time
from facialrecognizer import prepareFacialModel
from facialrecognizer import runFaceRecognition
from deskclassifier import deskClassify
size = 2
fn_haar = 'haarcascade_frontalface_default.xml'
fn_dir = 'att_faces'


#call the face model loading method
webcam = cv2.VideoCapture(0)
model = prepareFacialModel()
#webcam = cv2.VideoCapture("rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov")


while True:

    # Loop until the camera is working
    rval = False
    while(not rval):
        # Put the image from the webcam into 'frame'
        (rval, frame) = webcam.read()
        if(not rval):
            print("Failed to open webcam. Trying again...")

    frame=cv2.flip(frame,1,0)
    runFaceRecognition(frame,model)
    now = datetime.datetime.now()
    #print now.strftime("%d%b%Y_%H%M%S")

    path = "./temp/agent_"+now.strftime("%m%d%Y_%H%M%S_%f")+".png"
    cv2.imwrite(path,frame)

    desk_classification, desk_probab = deskClassify(path)
    print("classification %s - probability %f" % (desk_classification,desk_probab))

    cv2.putText(frame,'Status: %s - p:%f'% (desk_classification,desk_probab),(30,60),cv2.FONT_HERSHEY_PLAIN,1,(255, 0, 0))
    cv2.imshow('OpenCV', frame)

    #delete the image file
    os.remove(path)
    if(desk_classification != "working_compliant"):
        cv2.imwrite(path,frame) #save it with the status if not compliant in any way

    #time.sleep(.1)
    


    key = cv2.waitKey(10)
    if key == 27:
        break
