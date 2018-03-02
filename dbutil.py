import MySQLdb
import os,sys

db = MySQLdb.connect(host="orlawv027",user="biometric-user",passwd="B10M37R1K5",db="biometrics")
cur = db.cursor()
results = cur.execute(" select img, lan_id from train_img where status = 'N' ")
i = 0
for rs in results:
	img = open("./temp/train_"+rs[1]+"_%d",++i,"wb")
	img.write(rs[0])
	img.close()


