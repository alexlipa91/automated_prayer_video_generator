GOOGLE_APPLICATION_CREDENTIALS=prayers-channel-369405-28161d9ee0fe.json

docker run \
  -e GOOGLE_APPLICATION_CREDENTIALS=/credentials-firestore.json \
  -e SAVE_LOCAL=1 \
  -e LANGUAGE="ES" \
  -v $(pwd)/prayers-channel-369405-608070bcf3ae.json:/credentials-firestore.json \
  -v $(pwd)/docker-output:/output \
  europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder:latest-arm64
