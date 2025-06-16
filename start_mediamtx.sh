
# docker run --rm -it \
#     --network=host \
#     -v $(pwd)/mediamtx.yml:/mediamtx.yml \
#     bluenviron/mediamtx:latest


# docker run --rm -it \
#     -v $(pwd)/mediamtx.yml:/mediamtx.yml \
#     -e MTX_RTSPTRANSPORTS=tcp \
#     -e MTX_WEBRTCADDITIONALHOSTS=192.168.168.105 \
#     -p 554:8554 \
#     -p 1935:1935 \
#     -p 8888:8888 \
#     -p 8889:8889 \
#     bluenviron/mediamtx

# 루트 프로젝트 폴더에서 실행
ROBOT_IP=192.168.168.105 \
docker run --rm -it \
    --network=host \
    -v $(pwd)/mediamtx.yml:/mediamtx.yml:ro \
    -e MTX_RTSPTRANSPORTS=tcp \
    -e MTX_HLSENABLED=true \
    -e MTX_WEBRTCENABLED=true \
    -e MTX_WEBRTCADDITIONALHOSTS=$ROBOT_IP \
    bluenviron/mediamtx:latest
