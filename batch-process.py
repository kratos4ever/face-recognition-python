#program to run like a schduled task in docker, just prints the current time to stdout
import sys,os
import time
import datetime

def getConnection():
	

def main():
	#get - connection to the mysql server - no externalizing as of now


	#run the query to get the images from stream_img table, set into map<lanid,list<object:lanid,img,capture_time,id,status,etc>>

	#Get a list of unique lanids from the above query and get the training image for each. set in a map<lanid,<object:lanid,id,image>>

	#for each lanid in the stream_img result list, check if there is a training image, if there is, do the facial recog for each record 
	#for the lanid, then write the status accordingly



if __name__ == '__main__':
		main()	