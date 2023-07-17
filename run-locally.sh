GOOGLE_APPLICATION_CREDENTIALS=prayers-channel-369405-28161d9ee0fe.json

docker run \
  -e UPLOAD_TO_GCS=1 \
  europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder:latest-arm64
