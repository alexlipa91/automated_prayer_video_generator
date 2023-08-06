docker buildx build --platform linux/amd64 -t europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder:latest .
docker buildx build --platform linux/arm64 -t europe-west4-docker.pkg.dev/prayers-channel-369405/images/prayer-channel-video-builder:latest-arm64 .

#docker buildx build -f audio-processing/Dockerfile --platform linux/amd64 -t europe-west4-docker.pkg.dev/prayers-channel-369405/images/demucs-audio-processing:latest .
#docker buildx build -f audio-processing/Dockerfile --platform linux/arm64 -t europe-west4-docker.pkg.dev/prayers-channel-369405/images/demucs-audio-processing:latest-arm64 .