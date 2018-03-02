# facerec.py
import cv2, sys, numpy, os
import datetime
import time
from batch_face_recognizer import prepareFacialModel
from batch_face_recognizer import runFaceRecognition
from pathlib2 import Path

size = 2
fn_haar = 'haarcascade_frontalface_default.xml'
fn_dir = 'att_faces'

if(len(sys.argv) <2 ):
    print("Usage python batch-main.py <IMAGE_FILE_PATH>")
    sys.exit(1)

path = sys.argv[1]
imFile = Path(path)

if(imFile.exists()):
    model = prepareFacialModel()
    now = datetime.datetime.now()

    img = cv2.imread(path)

    runFaceRecognition(img,model)
else:
    print("File does not exist at path: "+ path)
    sys.exit(1)

