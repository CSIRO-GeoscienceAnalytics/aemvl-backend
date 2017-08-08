# Use like this:
#   ./run.sh http://localhost:8080
#   ./run.sh https://capdf.csiro.au/aemvl-backend
URL=$1

sed "s#{{URL}}#${URL}#g" postman.json > postman_temp.json

newman run postman_temp.json
rm postman_temp.json
