#!/bin/bash

# Run:
# ./curl_test.sh http://localhost:8080
# ./curl_test.sh https://capdf.csiro.au/aemvl-backend

URL_ROOT=$1

if [ ! "$URL_ROOT" ]; then
    echo "You must specify a URL. Try:"
    echo './curl_test.sh http://localhost:8080'
    exit
fi

echo '' > cookies.txt

if [ -d "../uploads/testuser" ]; then
    rm -r ../uploads/testuser
fi

curl -s \
    -c cookies.txt \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F "datafile=@../data/AUS_10004_CSIRO_EM_HM_reduced.XYZ" \
    -F "configfile=@../data/AUS_10004_CSIRO_EM_HM_reduced.json" \
    "${URL_ROOT}/api/upload"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -X POST \
    "${URL_ROOT}/api/getLines"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "column_names=HM_Z,PLNI" \
    -X POST \
    "${URL_ROOT}/api/getLine"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F 'mask_details={"line_number": 200301,
        "component_name": "HM_Z",
        "masks":
        [
            { "fid": 261069.7, "mask": [0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,-1,0,0,0,0,0,0,-1,0,0,-1,0]},
            { "fid": 261069.6, "mask": [0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,-1,0,0,0,0,0,0,-1,0,0,-1,0]}
        ]}' \
    "${URL_ROOT}/api/applyMaskToFiducials"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F 'mask_details={"line_number": 200301,
        "component_name": "HM_Z",
        "mask": -1,
        "range": [261348.0, 261348.5]}' \
    "${URL_ROOT}/api/applyMaskToAllChannelsBetweenFiducials"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "column_names=HM_Z,PLNI" \
    -X POST \
    "${URL_ROOT}/api/getLine"

curl -s \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -X POST \
    "${URL_ROOT}/api/list_test_datasets"

curl -s \
    -c cookies.txt \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F "test_dataset_name=AUS_10004_CSIRO_EM_HM_reduced" \
    -X POST \
    "${URL_ROOT}/api/start_test_session"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F "line_number=200001" \
    -F "column_names=HM_Z,PLNI" \
    -X POST \
    "${URL_ROOT}/api/getLine"

# Do a test to work out what is set for Access-Control-Allow-Origin:
TEMP=$(mktemp)
curl -s \
    -i \
    -I \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    "${URL_ROOT}/api/getLines" > $TEMP

echo $'\nThe next line will show the value of Access-Control-Allow-Origin if it has been set:'
grep 'Access-Control-Allow-Origin' $TEMP
rm $TEMP

curl -s \
    -O \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -X POST \
    "${URL_ROOT}/api/export"

