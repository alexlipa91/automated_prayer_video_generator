IMAGE_NAME=europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder

docker buildx build --platform linux/amd64 -t $IMAGE_NAME:$(git rev-parse HEAD) -t $IMAGE_NAME:latest .
docker push $IMAGE_NAME:latest