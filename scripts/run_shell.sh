docker build -t local-build .
docker run -v $(pwd)/docker-output:/output --entrypoint /bin/bash -it local-build $@