#!/bin/sh
docker build -t ca22 .

docker build -t ca22_selenium ~/github/ca22-backend/
docker tag ca22_selenium localhost:5000/ca22_selenium
docker push localhost:5000/ca22_selenium