
docker run --rm -it \
    -d --restart unless-stopped \
    --network=host \
    -v "$(pwd)/mediamtx.yml":/mediamtx.yml:ro \
    bluenviron/mediamtx:latest


# rtsp   : rtsp://robot-ip:8554/gremsy/
# webrtc : http://robot-ip:8889/gremsy/