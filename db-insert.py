import MySQLdb
import os,sys

def read_file(filename):
    with open(filename, 'rb') as f:
        photo = f.read()
    return photo

if(len(sys.argv)<4):
	print("usage -> python db-insert.py <TRAIN/STREAM> <LAN_ID> <IMAGE_PATH>")
	sys.exit(1)

mode = sys.argv[1]
lanid = sys.argv[2]
path = sys.argv[3]

imgFile = read_file(path)

query = " INSERT INTO "+str.lower(mode)+"_img (LAN_ID,CAPTURE_TIME,IMAGE,STATUS) VALUES (%s,NOW(), %s,'N') ";
args = (lanid,imgFile)

conn = MySQLdb.connect(host="localhost",user="biometric-user",passwd="B10M37R1K5",db="biometrics")
cur = conn.cursor()
cur.execute(query,args)
conn.commit()
