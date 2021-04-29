export PUSHED_APP_KEY=$1 
export PUSHED_APP_SECRET=$2
export CA_LOGIN=$3
export CA_PASSWORD=$4
export CA_ACCOUNT=$5

printenv

docker build -t ca22_selenium ~/github/ca22-selenium/
docker tag ca22_selenium localhost:5000/ca22_selenium
docker push localhost:5000/ca22_selenium
docker stack rm ca22_selenium
docker stack deploy --prune --with-registry-auth --resolve-image=always -c ~/github/ca22-selenium/ca22_selenium.yml ca22_selenium
