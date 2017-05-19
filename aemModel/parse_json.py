import json
import sys
import pandas
from pprint import pprint

path = '/home/adamlocal/Projects/aemvl-backend/docs/ExampleTempestData.From.Client.xyz'

with open('/home/adamlocal/Projects/aemvl-backend/docs/AUS_10004_CSIRO_SkyTem_EM.json') as json_file_handle:
    json_content = json.load(json_file_handle)

dataframe = pandas.read_csv(path, delim_whitespace = True)

def getFlightPlanInfo():
    return json_content["FlightPlanInfo"]

def getDataDefinition():
    return json_content["DataDefinition"]

def getColumnNumbersByName(column_names):
    column_names = column_names if isinstance(column_names, list) else [column_names]
    return [item for sublist in list(list(range(v[0], v[1])) if isinstance(v, list) else [v] for k, v in getDataDefinition().items() if k in column_names) for item in sublist]

def getColumnsByName(column_names):
    return getColumnsByNumber(getColumnNumbersByName(column_names))

def getColumnsByNumber(column_numbers):
    for row in dataframe.itertuples():
        for column_number in column_numbers:
            print(row[column_number])

#print(getFlightPlanInfo())
#print(getDataDefinition())
#print(getColumnsByName('Date'))

getColumnsByName(['LineNumber', 'FlightNumber', 'LM_Z'])

#print(json_content["EMInfo"])
#print(json_content["ExportForInversion"])