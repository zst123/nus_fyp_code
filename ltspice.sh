export DISPLAY=:0.0
# xhost +local:docker
docker exec "ltspice" wine "/home/appuser/.wine/drive_c/Program Files/LTC/LTspiceXVII/XVIIx86.exe" $@
