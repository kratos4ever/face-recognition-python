#!/bin/bash
echo $MODE

echo "Running the consumer process for $MODE"

if ["$MODE" == "FaceStreaming"]; then
	python3 -u consumer.py
elif ["$MODE" == "FaceTraining"]; then
	python3 -u training_consumer.py
else
	echo "Invalid mode, allowed values are FaceTraining OR FaceStreaming"
fi
