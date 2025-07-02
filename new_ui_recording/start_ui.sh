docker build -t gremsy-ui:v0.2.1 .
docker run --rm -it --network=host -v ~/krm_data/gremsy:/app/data gremsy-ui:v0.2.1


# docker run --rm -it --network=host gremsy-ui:v0.2.1
# /home/krm/krm_data/gremsy