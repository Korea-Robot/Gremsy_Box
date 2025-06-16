
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


# 각 옵션 설명
# --network=host
# 컨테이너가 호스트 네트워크와 동일하게 동작 → 포트 매핑 (-p) 불필요

# -v "$(pwd)/mediamtx.yml":/mediamtx.yml:ro
# 로컬 설정 파일을 컨테이너에 읽기 전용으로 연결

# -e MTX_RTSPTRANSPORTS=tcp
# RTSP pull 시 TCP 전송만 사용 (UDP 패킷 손실 방지)

# -e MTX_HLSENABLED=true
# HLS 스트리밍 활성화

# -e MTX_WEBRTCENABLED=true
# WebRTC 스트리밍 활성화

# -e MTX_SOURCEONDEMAND=false
# on-demand 끄기 → 컨테이너 기동과 동시에 RTSP를 계속 pull

# -e MTX_WEBRTCADDITIONALHOSTS=$ROBOT_IP
# ICE 후보에 외부 접속용 IP(Tailscale 등)를 추가