docker build -t ca22_selenium ~/github/ca22-selenium/
docker tag ca22_selenium localhost:5000/ca22_selenium
docker push localhost:5000/ca22_selenium