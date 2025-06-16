
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
# ROBOT_IP=192.168.168.105 \
# docker run --rm -it \
#     --network=host \
#     -v $(pwd)/mediamtx.yml:/mediamtx.yml:ro \
#     -e MTX_RTSPTRANSPORTS=tcp \
#     -e MTX_HLSENABLED=true \
#     -e MTX_WEBRTCENABLED=true \
#     -e MTX_WEBRTCADDITIONALHOSTS=$ROBOT_IP \
#     bluenviron/mediamtx:latest


#!/bin/bash
export ROBOT_IP=192.168.168.105     # 실제 로봇 내부 IP (미리 export)
docker run --rm -it \
    --network=host \
    -v $(pwd)/mediamtx.yml:/mediamtx.yml:ro \
    -e MTX_RTSPTRANSPORTS=tcp \
    -e MTX_HLSENABLED=true \
    -e MTX_WEBRTCENABLED=true \
    -e MTX_SOURCEONDEMAND=false \
    -e MTX_RUNONSTARTUP=true        \   # ← 있으면 좋습니다
    -e MTX_WEBRTCADDITIONALHOSTS=${ROBOT_IP} \
    bluenviron/mediamtx:latest
# rtsp://robot-159:8554/gremsy
# http://100.87.140.159:8888/hls/gremsy/index.m3u8
# ws://robot-159:8889/gremsy