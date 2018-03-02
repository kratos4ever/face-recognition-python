import MySQLdb
import os,sys

db = MySQLdb.connect(host="orlawv027",user="biometric-user",passwd="B10M37R1K5",db="biometrics")
cur = db.cursor()
nrows = cur.execute(" select image, lan_id from train_img where status = 'N' ")
results = cur.fetchall()
i = 0
for rs in results:
	path = "./temp/train_"+rs[1]+"_%d.jpg"%i
	path=path.replace("\\","_")
	i = i+1
	print path
	img = open(path,"wb")
	img.write(rs[0])
	img.close()


