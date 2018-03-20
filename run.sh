#!/bin/bash
echo $MODE

echo "Running the consumer process for $MODE"
FTRN="FaceStreaming"
FSTR="FaceTraining"
if [[ $MODE = $FSTR ]]
then
	python3 -u consumer.py
elif [[ $MODE = $FTRN ]]
then
	python3 -u training_consumer.py
else
	echo "Invalid mode, allowed values are FaceTraining OR FaceStreaming"
fi
