
# docker run --rm -it \
#     --network=host \
#     -v $(pwd)/mediamtx.yml:/mediamtx.yml \
#     bluenviron/mediamtx:latest


docker run --rm -it \
    -v $(pwd)/mediamtx.yml:/mediamtx.yml \
    -e MTX_RTSPTRANSPORTS=tcp \
    -e MTX_WEBRTCADDITIONALHOSTS=192.168.168.105 \
    -p 554:8554 \
    -p 1935:1935 \
    -p 8888:8888 \
    -p 8889:8889 \
    bluenviron/mediamtx