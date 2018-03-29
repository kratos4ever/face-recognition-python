cd ~/bio-source/
sudo docker rm $(sudo docker stop $(sudo docker ps -a -q --filter name=bio_* --format="{{.ID}}"))
cd ~/bio-source/face-recognition-python
git pull
cd ~/bio-source/
sudo docker build -t biometric-sense/bio1 --rm=true -f ./Dockerfile . 
sudo docker run -d -e MODE=FaceStreaming --name bio_fstream biometric-sense/bio1:latest 
sudo docker run -d -e MODE=FaceTraining --name bio_ftrain biometric-sense/bio1:latest 
cd ~
