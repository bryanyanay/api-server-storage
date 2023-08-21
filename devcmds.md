uvicorn main:app --host 0.0.0.0 --port 8000

export GCLOUD_PROJECT=lila-api-393822


# DOCKER

### Build the Docker image, run from root
docker build -t api-server-storage:test-2 .

### Run the Docker container (replace the port as needed)
docker run -p 8000:8000 api-server-storage:test-0


### Push to Docker Hub
docker login -u bryanyanay

docker tag api-server-storage:test-2 bryanyanay/api-server-storage:test-2
docker push bryanyanay/api-server-storage:test-2