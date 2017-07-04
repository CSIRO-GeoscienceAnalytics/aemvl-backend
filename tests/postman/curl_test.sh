#!/bin/bash

echo '' > cookies.txt

curl \
    -c cookies.txt \
    -F "datafile=@../../docs/ExampleTempestData.From.Client.xyz" \
    -F "configfile=@../../docs/AUS_10004_CSIRO_SkyTem_EM.json" \
    -F "project_id=TESTPROJECT" \
    -H "Accept: text/csv" \
    http://conda:8080/api/upload

curl \
    -b cookies.txt \
    -c cookies.txt \
    -F "project_id=TESTPROJECT" \
    -H "Accept: text/csv" \
    http://conda:8080/api/getLines

curl \
    -b cookies.txt \
    -c cookies.txt \
    -F "line_number=10030" \
    -F "column_names=HM_Z,PLNI" \
    -F "project_id=TESTPROJECT" \
    -H "Accept: text/csv" \
    http://conda:8080/api/getLine
