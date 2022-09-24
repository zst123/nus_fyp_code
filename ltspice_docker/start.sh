#!/bin/bash
export DISPLAY=:0.0
xhost +local:docker

NAME="ltspice"
IMAGE="ltspice_img"

mkdir -p ./files

docker start $NAME
