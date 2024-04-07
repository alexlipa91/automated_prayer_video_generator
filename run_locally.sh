GOOGLE_APPLICATION_CREDENTIALS=prayers-channel-369405-28161d9ee0fe.json

docker buildx build --platform linux/arm64 -t local-build .

docker run \
  -e GOOGLE_APPLICATION_CREDENTIALS=/credentials-firestore.json \
  -e SAVE_LOCAL=1 \
  -e LANGUAGE="ES" \
  -v $(pwd)/prayers-channel-369405-608070bcf3ae.json:/credentials-firestore.json \
  -v $(pwd)/docker-output:/output \
  local-build
