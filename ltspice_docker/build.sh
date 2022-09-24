#!/bin/bash
export DISPLAY=:0.0
IMAGE="ltspice_img"
NAME="ltspice"

docker build -t "$IMAGE" .

mkdir -p ../files

docker run \
    --hostname "${NAME}" \
    --interactive \
    --name "${NAME}" \
    --privileged \
    --detach \
    --net=host \
    -u $(id -u) \
    --env DISPLAY=:0.0 \
    --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
    --volume "$(pwd)/../files:/FILES" \
    --volume /tmp/.X11-unix:/tmp/.X11-unix \
    $IMAGE

docker exec --workdir /FILES/ $NAME wget https://ltspice.analog.com/software/LTspice32.exe
docker exec --workdir /FILES/ $NAME wine LTspice32.exe
docker exec --workdir /FILES/ $NAME rm LTspice32.exe
