docker build -t local-build .
docker run -v $(pwd)/docker-output:/output local-build
