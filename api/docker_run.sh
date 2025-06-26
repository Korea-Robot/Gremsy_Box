docker run -d --restart unless-stopped \
    --name gremsy_api \
    --network host \
    -e PORT=8000 \
    docker.argusvision.io/intel/krm-gremsy-api:0.2.0