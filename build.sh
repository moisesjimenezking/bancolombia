sudo docker build -t bancolombia .
sudo docker stop bancolombia
sudo docker rm bancolombia
sudo docker run -v ./app/config/logs:/app/config/logs -d -p 23301:5000 --name bancolombia bancolombia