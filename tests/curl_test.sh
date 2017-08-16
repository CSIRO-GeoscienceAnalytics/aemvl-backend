#!/bin/bash

# Run:
# ./curl_test.sh http://conda:8080
# ./curl_test.sh https://capdf.csiro.au/aemvl-backend

URL_ROOT=$1

echo '' > cookies.txt

curl -s \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    -F "datafile=@../docs/AUS_10004_CSIRO_EM_HM_reduced.XYZ" \
    -F "configfile=@../docs/AUS_10004_CSIRO_SkyTem_EM.json" \
    "${URL_ROOT}/api/upload"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    "${URL_ROOT}/api/getLines"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "column_names=HM_Z,PLNI" \
    "${URL_ROOT}/api/getLine"

curl -s \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
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
    -H "Accept: text/csv" \
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
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "column_names=HM_Z,PLNI" \
    "${URL_ROOT}/api/getLine"

# Do a test to work out what is set for Access-Control-Allow-Origin:
curl -s \
    -i \
    -I \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    "${URL_ROOT}/api/getLines" > out

echo $'\nThe next line will show the value of Access-Control-Allow-Origin if it has been set:'
grep 'Access-Control-Allow-Origin' out
rm out

