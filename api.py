import os
import sys
import sqlite3
import uuid
import pandas
from shutil import copyfile
from flask import request, session, redirect, url_for, send_from_directory, render_template, Response
from app import app
from werkzeug.utils import secure_filename
from osgeo import ogr, osr
import pathlib
import json

outSpatialRef4326 = osr.SpatialReference()
outSpatialRef4326.ImportFromEPSG(4326)
CSV_TYPE = 1
HTML_TYPE = 2
project_id = None

def get_preferred_output_type():
    accept_headers = request.headers.get('Accept').split(',')
    
    if 'text/csv' in accept_headers:
        return CSV_TYPE
    elif 'text/html' in accept_headers:
        return HTML_TYPE
    else:
        raise Exception("Unsupported accept header provided: " + str(accept_headers))

# Look up a DataDefinition column name in the FlightPlanInfo object to see if it is
# an alias of a well-known name. If it is we will return the well-known name, otherwise
# return the original name:
def getColumnWellKnownName(column_name):
    for well_known_name, alias in session['projects'][project_id]['flight_plan_info'].items():
        if column_name == alias:
            return well_known_name

    return column_name        

def getColumnNameByNumber(number):
    for column_name, column_number in session['projects'][project_id]['data_definition'].items():
        if isinstance(column_number, int) and number == column_number:
            return getColumnWellKnownName(column_name)
        if isinstance(column_number, list) and number in column_number:
            if column_name not in session['projects'][project_id]['component_column_offsets']:
                # This has to be cast to a normal int otherwise it ends up as numpy.int64 which can't be serialised into the session:
                session['projects'][project_id]['component_column_offsets'][column_name] = int(number - 1)

            return column_name + "_" + str(number - session['projects'][project_id]['component_column_offsets'][column_name])

def createLocation4326(x_component, y_component):
    # If we're already using WGS84 / 4326 we don't need to perform a conversion:
    if session['projects'][project_id]['flight_plan_info']["CoordinateSystem"] in ['WGS84', 4326]:
        return str(x_component) + " " + str(y_component)
    else:
        # TODO: I'm assuming that flight_plan_info["CoordinateSystem"] will be an EPSG number, not a name like GDA84, WGS84
        inputEPSG = session['projects'][project_id]['flight_plan_info']["CoordinateSystem"]

        # create a geometry from coordinates
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x_component, y_component)

        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(inputEPSG)

        coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef4326)
        point.Transform(coordTransform)

        return str(point.GetX()) + " " + str(point.GetY())

def getComponentColumnNames(component_name):
    if isinstance(session['projects'][project_id]['data_definition'][component_name], list):
        column_suffixes = list(range(session['projects'][project_id]['data_definition'][component_name][0] - session['projects'][project_id]['component_column_offsets'][component_name], 
            len(session['projects'][project_id]['data_definition'][component_name]) + 1))
        return [component_name + "_" + str(n) for n in column_suffixes]
    else:
        return component_name

@app.route('/api/upload', methods=['POST'])
def api_upload():
    global project_id
    project_id = request.form["project_id"]
    
    # TODO: Use output_type
    output_type = get_preferred_output_type()

    # check that the POST request is complete:
    if 'datafile' not in request.files:
        return "error: datafile not provided"

    if 'configfile' not in request.files:
        return "error: configfile not provided"

    if 'project_id' not in request.form:
        return "error: project_id not provided"
    
    # Create the session if it doesn't exist:
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid1())
        session['projects'] = {}

    project_path = os.path.join(app.config['UPLOAD_FOLDER'], session['session_id'], project_id)
    pathlib.Path(project_path).mkdir(parents=True)
    
    session['projects'][project_id] = {'project_path': project_path}

    datafile_handle = request.files['datafile']
    datafile_path = os.path.join(project_path, 'data.xyz')
    datafile_handle.save(datafile_path)

    configfile_handle = request.files['configfile']
    configfile_path = os.path.join(project_path, 'config.json')
    configfile_handle.save(configfile_path)
    
    json_content = None
    data_definition = None
    flight_plan_info = None

    with open(configfile_path) as json_file_handle:
        json_content = json.load(json_file_handle)

    data_definition = json_content["DataDefinition"]
    for column_name, column_number in data_definition.items():
        if isinstance(column_number, list):
            data_definition[column_name] = list(range(column_number[0], column_number[1]+1))

    flight_plan_info = json_content["FlightPlanInfo"]
    flight_plan_info["CoordinateSystem"] = flight_plan_info["CoordinateSystem"].upper() if isinstance(flight_plan_info["CoordinateSystem"], str) else flight_plan_info["CoordinateSystem"]

    session['projects'][project_id]['flight_plan_info'] = flight_plan_info
    session['projects'][project_id]['em_info'] = json_content["EMInfo"]
    session['projects'][project_id]['export_for_inversion'] = json_content["ExportForInversion"]
    session['projects'][project_id]['data_definition'] = data_definition
    session['projects'][project_id]['component_column_offsets'] = {}

    dataframe = pandas.read_csv(datafile_path, header=None, delim_whitespace=True)

    # Apply the names to the columns:
    dataframe.rename(columns=lambda old_column_number: getColumnNameByNumber(old_column_number+1), inplace=True)
    dataframe['LOCATION_4326'] = dataframe.apply(lambda row: createLocation4326(row['XComponent'], row['YComponent']), axis=1)

    # Add a '_mask' column for every column that was generated from a list in the DataDefinition:
    for key, value in session['projects'][project_id]['data_definition'].items():
        if isinstance(value, list):
            for column_number in value:
                dataframe[key + "_" + str(column_number - session['projects'][project_id]['component_column_offsets'][key]) + "_mask"] = False

    with sqlite3.connect(os.path.join(session['projects'][project_id]['project_path'], 'database.db')) as connection:
        dataframe.to_sql("dataframe", connection, index=False, if_exists='replace')

    return Response(project_id, mimetype = 'text/plain')

# Used to create the map with all the flight lines:
@app.route('/api/getLines', methods=['POST'])
def getLines():
    global project_id
    project_id = request.form["project_id"]
    
    # TODO: Use output_type
    output_type = get_preferred_output_type()

    with sqlite3.connect(os.path.join(session['projects'][project_id]['project_path'], 'database.db')) as connection:
        result_set = pandas.read_sql(
            ''' SELECT  LineNumber,
                        Fiducial,
                        LOCATION_4326
                FROM    dataframe''',
            connection)

        return Response(result_set.to_csv(index = False), mimetype = 'text/plain')

# Used to create the multi-line graph:
@app.route('/api/getLine', methods=['POST'])
def getLine():
    global project_id
    project_id = request.form["project_id"]
    line_number = int(request.form["line_number"])
    column_names = request.form["column_names"].split(',')
    
    
    #column_names = column_names if isinstance(column_names, list) else [column_names]
    
    # TODO: Use output_type
    output_type = get_preferred_output_type()

    first = True
    select_sql = ''
    for column_name in column_names:
        select_sql = select_sql + ('' if first else ',')
        full_column_names = getComponentColumnNames(column_name)
        
        if isinstance(full_column_names, list):
            format_string = "printf('" + " ".join(['%g'] * len(full_column_names)) + "'," 
            
            select_sql = select_sql + format_string + ",".join(full_column_names) + ") AS " + column_name
            
            # If we have a list we'll also fetch the mask back:
            select_sql = select_sql + ", " + format_string + "_mask,".join(full_column_names) + "_mask) AS " + column_name + "_mask"
        else:
            select_sql = select_sql + full_column_names

        first = False

    with sqlite3.connect(os.path.join(session['projects'][project_id]['project_path'], 'database.db')) as connection:
        sql = '''SELECT  ''' + select_sql + '''
                FROM    dataframe
                WHERE   LineNumber = ''' + str(line_number)

        result_set = pandas.read_sql(sql, connection)

        return Response(result_set.to_csv(index = False), mimetype = 'text/plain')

    
    
    