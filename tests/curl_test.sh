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

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F "datafile=@../data/AUS_10004_CSIRO_EM_HM_reduced.xyz" \
    -F "configfile=@../data/AUS_10004_CSIRO_EM_HM_reduced.json" \
    "${URL_ROOT}/api/upload"

curl -s \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -X POST \
    "${URL_ROOT}/api/getLines"

curl -s \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "component_name=HM_Z" \
    -X POST \
    "${URL_ROOT}/api/getLine"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F 'mask_details={"line_number": 200301,
        "component_names": ["HM_Z"], 
        "masks":
        [
            { "fid": 261069.7, "mask": [0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,-1,0,0,0,0,0,0,-1,0,0,-1,0]},
            { "fid": 261069.6, "mask": [0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,-1,0,0,0,0,0,0,-1,0,0,-1,0]}
        ]}' \
    "${URL_ROOT}/api/applyMaskToFiducials"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F 'mask_details={"line_number": 200301,
        "component_names": ["HM_Z"],
        "mask": -1,
        "range": [261348.0, 261348.5]}' \
    "${URL_ROOT}/api/applyMaskToAllChannelsBetweenFiducials"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F 'mask_details={"line_number": 200301,
        "component_names": ["HM_Z"],
        "mask": -1,
        "channels": [0,1,2,3,4]}' \
    "${URL_ROOT}/api/applyMaskToChannels"

curl -s \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "component_name=HM_Z" \
    -X POST \
    "${URL_ROOT}/api/getLine"

curl -s \
    -H "Accept: application/json" \
    -X POST \
    "${URL_ROOT}/api/listTestDatasets"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F "test_dataset_name=AUS_10004_CSIRO_EM_HM_reduced" \
    -F "override=False" \
    -X POST \
    "${URL_ROOT}/api/startTestSession"

curl -s \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F "line_number=200001" \
    -F "component_name=HM_Z" \
    -X POST \
    "${URL_ROOT}/api/getLine"

# Do a test to work out what is set for Access-Control-Allow-Origin:
TEMP=$(mktemp)
curl -s \
    -i \
    -I \
    -H "Accept: text/csv" \
    "${URL_ROOT}/api/getLines" > $TEMP

echo $'\nThe next line will show the value of Access-Control-Allow-Origin if it has been set:'
grep 'Access-Control-Allow-Origin' $TEMP
rm $TEMP

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F 'mask_details={"line_number": 200301,
        "component_names": ["HM_Z", "HM_X"],
        "mask": -1,
        "channels": [0,1,2,3,4]}' \
    "${URL_ROOT}/api/applyMaskToChannels"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F 'mask_details={"line_number": 200001,
        "component_names": ["HM_Z"],
        "mask": -1,
        "range": [194273.90, 194274.60]}' \
    "${URL_ROOT}/api/applyMaskToAllChannelsBetweenFiducials"

curl -s \
    -O \
    -H "Accept: text/csv" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -F "columns_to_export=JobNumber,Fiducial,DEM,HM_Z,HM_X" \
    -X POST \
    "${URL_ROOT}/api/export"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -X POST \
    "${URL_ROOT}/api/listProjects"
    
curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT" \
    -X POST \
    "${URL_ROOT}/api/deleteProject"

curl -s \
    -H "Accept: application/json" \
    -F "user_token=testuser" \
    -F "project_id=TESTPROJECT2" \
    -X POST \
    "${URL_ROOT}/api/deleteProject"

