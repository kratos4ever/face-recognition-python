import sys, os
import datetime
import time
import face_recognition

if(len(sys.argv) < 3 ):
    print("Usage python batch-face-id.py <BENCHMARK IMAGE> <TEST IMGAGE>")
    sys.exit(1)

benchmark = face_recognition.load_image_file(sys.argv[1])
testfile = face_recognition.load_image_file(sys.argv[2])

benchEncoding = face_recognition.face_encodings(benchmark)[0]
testEncoding = face_recognition.face_encodings(testfile)[0]

distance = face_recognition.face_distance([benchEncoding],testEncoding)

for i, face_distance in enumerate(distance):
    print("The test image has a distance of {:.2} from known image #{}".format(face_distance, i))
    print("- With a normal cutoff of 0.6, would the test image match the known image? {}".format(face_distance < 0.6))
    print("- With a very strict cutoff of 0.5, would the test image match the known image? {}".format(face_distance < 0.5))
print()

