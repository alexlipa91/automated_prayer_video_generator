GOOGLE_APPLICATION_CREDENTIALS=prayers-channel-369405-28161d9ee0fe.json

docker run \
  -e SAVE_LOCAL=1 \
  -e DURATION_SECONDS=40 \
  -v $(pwd)/docker-output:/output \
  europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder:latest-arm64
