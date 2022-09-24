#!/bin/bash
sudo service docker status
sudo groupadd docker
sudo usermod -aG docker ${USER}
su -s ${USER}