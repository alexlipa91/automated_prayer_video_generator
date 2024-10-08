docker build -t local-build .

docker run -v docker-output:/output local-build
