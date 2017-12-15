# facerec.py
import cv2, sys, numpy, os
import argparse
import datetime
import imutils
import time

firstFrame = None


def detectOccupancy(frame):
    global firstFrame

    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray

    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 500:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    return text; 


size = 2
fn_haar = 'haarcascade_frontalface_default.xml'
fn_dir = 'att_faces'

# Part 1: Create fisherRecognizer
print('Training...')

# Create a list of images and a list of corresponding names
(images, lables, names, id) = ([], [], {}, 0)

# Get the folders containing the training data
for (subdirs, dirs, files) in os.walk(fn_dir):

    # Loop through each folder named after the subject in the photos
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(fn_dir, subdir)

        # Loop through each photo in the folder
        for filename in os.listdir(subjectpath):

            # Skip non-image formates
            f_name, f_extension = os.path.splitext(filename)
            if(f_extension.lower() not in
                    ['.png','.jpg','.jpeg','.gif','.pgm']):
                print("Skipping "+filename+", wrong file type")
                continue
            path = subjectpath + '/' + filename
            lable = id

            # Add to training data
            images.append(cv2.imread(path, 0))
            lables.append(int(lable))
        id += 1
(im_width, im_height) = (112, 92)

# Create a Numpy array from the two lists above
(images, lables) = [numpy.array(lis) for lis in [images, lables]]

# OpenCV trains a model from the images
# NOTE FOR OpenCV2: remove '.face'
model = cv2.createFisherFaceRecognizer()
model.train(images, lables)




# Part 2: Use fisherRecognizer on camera stream
haar_cascade = cv2.CascadeClassifier(fn_haar)
webcam = cv2.VideoCapture(0)
#Set the framerate to 2 frames per sec
webcam.set(cv2.cv.CV_CAP_PROP_FPS, 2)

#webcam = cv2.VideoCapture("rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov")

while True:

    # Loop until the camera is working
    rval = False
    while(not rval):
        # Put the image from the webcam into 'frame'
        (rval, frame) = webcam.read()
        if(not rval):
            print("Failed to open webcam. Trying again...")

    text = detectOccupancy(frame)
    if("Occupied"==text):
        # Flip the image (optional)
        frame=cv2.flip(frame,1,0)

        # Convert to grayscalel
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Resize to speed up detection (optinal, change size above)
        mini = cv2.resize(gray, (int(gray.shape[1] / size), int(gray.shape[0] / size)))

        # Detect faces and loop through each one
        faces = haar_cascade.detectMultiScale(mini)
        for i in range(len(faces)):
            face_i = faces[i]

            # Coordinates of face after scaling back by `size`
            (x, y, w, h) = [v * size for v in face_i]
            face = gray[y:y + h, x:x + w]
            face_resize = cv2.resize(face, (im_width, im_height))

            # Try to recognize the face
            prediction = model.predict(face_resize)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # [1]
            # Write the name of recognized face
            cv2.putText(frame,
               '%s - %.0f' % (names[prediction[0]],prediction[1]),
               (x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
    else:
        print("Unoccupied")
    # Show the image and check for ESC being pressed
    cv2.imshow('OpenCV', frame)
    key = cv2.waitKey(10)
    if key == 27:
        break
   