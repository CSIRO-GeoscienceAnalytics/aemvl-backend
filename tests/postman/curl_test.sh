#!/bin/bash

echo '' > cookies.txt

curl \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    -F "datafile=@../../docs/AUS_10004_CSIRO_EM_HM_reduced.XYZ" \
    -F "configfile=@../../docs/AUS_10004_CSIRO_SkyTem_EM.json" \
    http://conda:8080/api/upload

curl \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    http://conda:8080/api/getLines

curl \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "column_names=HM_Z,PLNI" \
    http://conda:8080/api/getLine

curl \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "component_name=HM_Z" \
    -F "fiducials_and_masks=[[261069.7,[0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,-1,0,0,0,0,0,0,-1,0,0,-1,0]],[261069.6,[0,-1,0,0,0,-1,0,0,0,-1,0,0,0,-1,0,-1,0,0,0,0,0,0,-1,0,0,-1,0]]]" \
    http://conda:8080/api/applyMask

curl \
    -b cookies.txt \
    -c cookies.txt \
    -H "Accept: text/csv" \
    -F "project_id=TESTPROJECT" \
    -F "line_number=200301" \
    -F "column_names=HM_Z,PLNI" \
    http://conda:8080/api/getLine