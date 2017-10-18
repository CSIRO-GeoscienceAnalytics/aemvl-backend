import os
import sqlite3
import uuid
import pandas
from flask import request, session, redirect, Response, send_from_directory
from app import app
from osgeo import ogr, osr
from werkzeug.datastructures import FileStorage
import pathlib
import json
import glob

outSpatialRef4326 = osr.SpatialReference()
outSpatialRef4326.ImportFromEPSG(4326)


def generateResponse(result_set):
    accept_headers = request.headers.get('Accept').split(',')

    if 'text/csv' in accept_headers:
        return Response(
            result_set.to_csv(index=False),
            mimetype='text/csv')
    elif 'text/html' in accept_headers:
        return Response(
            result_set.to_html(index=False),
            mimetype='text/html')
    else:
        raise Exception(
            "Unsupported accept header provided: " +
            str(accept_headers))


# Look up a DataDefinition column name in the FlightPlanInfo object to
# see if it is an alias of a well-known name. If it is we will return
# the well-known name, otherwise return the original name:
def getColumnWellKnownName(column_name, project_id):
    for well_known_name, alias in session['projects'][project_id]['flight_plan_info'].items():
        if column_name == alias:
            return well_known_name

    return column_name


def getColumnNameByNumber(number, project_id):
    for column_name, column_number in session['projects'][project_id]['data_definition'].items():
        if isinstance(column_number, int) and number == column_number:
            return getColumnWellKnownName(column_name, project_id)
        if isinstance(column_number, list) and number in column_number:
            if column_name not in session['projects'][project_id]['component_column_offsets']:
                # This has to be cast to a normal int otherwise it ends
                # up as numpy.int64 which can't be serialised into the
                # session:
                session['projects'][project_id]['component_column_offsets'][column_name] = int(number - 1)

            return column_name + "_" + str(number - session['projects'][project_id]['component_column_offsets'][column_name])


def createLocation4326(x_component, y_component, project_id):
    coordinateSystem = session['projects'][project_id]['flight_plan_info']["CoordinateSystem"]

    # If we're already using WGS84 / 4326 we don't need to perform a
    # conversion:
    if coordinateSystem in ['WGS84', 4326]:
        return str(x_component) + " " + str(y_component)
    else:
        # TODO: I'm assuming that flight_plan_info["CoordinateSystem"]
        # will be an EPSG number, not a name like GDA84, WGS84
        inputEPSG = coordinateSystem

        # create a geometry from coordinates
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x_component, y_component)

        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(inputEPSG)

        coordTransform = osr.CoordinateTransformation(
            inSpatialRef,
            outSpatialRef4326)
        point.Transform(coordTransform)

        return str(point.GetX()) + " " + str(point.GetY())


def getComponentColumnNames(component_name, project_id):
    if isinstance(session['projects'][project_id]['data_definition'][component_name], list):
        column_suffixes = list(
                                range(session['projects'][project_id]['data_definition'][component_name][0] - session['projects'][project_id]['component_column_offsets'][component_name],
                                      len(session['projects'][project_id]['data_definition'][component_name]) + 1))
        return [component_name + "_" + str(n) for n in column_suffixes]
    else:
        return component_name


@app.route('/api/list_test_datasets', methods=['GET'])
def list_test_datasets():
    file_names = glob.glob('data/*')
    file_names = set([os.path.splitext(file_name)[0] for file_name in file_names])

    return str([file_name[len('data/'):] for file_name in file_names])


@app.route('/api/start_test_session', methods=['POST'])
def start_test_session():
    test_dataset_name = request.form["test_dataset_name"]

    with open('data/' + test_dataset_name + '.XYZ', 'rb') as datafile_handle:
        with open('data/' + test_dataset_name + '.json', 'rb') as configfile_handle:
            return start_session(FileStorage(datafile_handle), FileStorage(configfile_handle))


@app.route('/api/upload', methods=['POST'])
def api_upload():
    # check that the POST request is complete:
    if 'datafile' not in request.files:
        return "error: datafile not provided"

    if 'configfile' not in request.files:
        return "error: configfile not provided"

    datafile_handle = request.files['datafile']
    configfile_handle = request.files['configfile']

    return start_session(datafile_handle, configfile_handle)


def start_session(datafile_handle, configfile_handle):
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]

    # Create the session if it doesn't exist:
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid1())
        session['projects'] = {}

    project_path = os.path.join(app.config['UPLOAD_FOLDER'], user_token, project_id)
    
    if os.path.exists(project_path):
        return Response(json.dumps({'response': 'ERROR', 'message': project_path + " already exists."}), mimetype='application/json') 
    
    pathlib.Path(project_path).mkdir(parents=True)

    session['projects'][project_id] = {}

    datafile_path = os.path.join(project_path, 'data.xyz')
    datafile_handle.save(datafile_path)

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
    dataframe.rename(columns=lambda old_column_number: getColumnNameByNumber(old_column_number+1, project_id), inplace=True)
    dataframe['LOCATION_4326'] = dataframe.apply(lambda row: createLocation4326(row['XComponent'], row['YComponent'], project_id), axis=1)

    # Add a '_mask' column for every column that was generated from a
    # list in the DataDefinition:
    for key, value in session['projects'][project_id]['data_definition'].items():
        if isinstance(value, list):
            for column_number in value:
                dataframe[key + "_" + str(column_number - session['projects'][project_id]['component_column_offsets'][key]) + "_mask"] = False

    with sqlite3.connect(os.path.join(project_path, 'database.db')) as connection:
        dataframe.to_sql("dataframe", connection, index=False, if_exists='replace')

    return Response(json.dumps({'response': 'OK', 'message': None}), mimetype='application/json')


# Used to create the map with all the flight lines:
@app.route('/api/getLines', methods=['GET'])
def getLines():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]

    database_path = os.path.join(app.config['UPLOAD_FOLDER'], user_token, project_id, 'database.db')

    with sqlite3.connect(database_path) as connection:
        result_set = pandas.read_sql(
            ''' SELECT  LineNumber,
                        Fiducial,
                        LOCATION_4326
                FROM    dataframe''',
            connection)

        return generateResponse(result_set)


# Used to create the multi-line graph:
@app.route('/api/getLine', methods=['GET'])
def getLine():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]

    database_path = os.path.join(app.config['UPLOAD_FOLDER'], user_token, project_id, 'database.db')

    line_number = int(request.form["line_number"])
    column_names = request.form["column_names"].split(',')

    first = True
    select_sql = ''
    for column_name in column_names:
        select_sql = select_sql + ('' if first else ',')
        full_column_names = getComponentColumnNames(column_name, project_id)

        if isinstance(full_column_names, list):
            unmasked_column = ''
            masked_column = ''

            for full_column_name in full_column_names:
                unmasked_column = unmasked_column + (' || \' \' || ' if unmasked_column else '') + full_column_name
                masked_column = masked_column + (' || \' \' || ' if masked_column else ',') + full_column_name + "_mask"

            # TODO: These need to be consitently named as em and
            # em_mask. The abilitiy to download lots of columns is
            # apparently not needed...
            unmasked_column = unmasked_column + " AS " + column_name
            masked_column = masked_column + " AS " + column_name + "_mask"

            select_sql = select_sql + unmasked_column + masked_column

        else:
            select_sql = select_sql + full_column_names

        first = False

    with sqlite3.connect(database_path) as connection:
        sql = '''SELECT  Fiducial,''' + select_sql + '''
                FROM    dataframe
                WHERE   LineNumber = ''' + str(line_number)

        result_set = pandas.read_sql(sql, connection)

        return generateResponse(result_set)


@app.route('/api/applyMaskToFiducials', methods=['POST'])
def applyMaskToFiducials():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]

    database_path = os.path.join(app.config['UPLOAD_FOLDER'], user_token, project_id, 'database.db')

    mask_details = json.loads(request.form["mask_details"])

    line_number = mask_details['line_number']
    component_name = mask_details['component_name']
    fiducials_and_masks = mask_details['masks']

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        for fiducial_and_masks in fiducials_and_masks:
            sql = 'UPDATE dataframe SET '

            fiducial = fiducial_and_masks['fid']
            masks = fiducial_and_masks['mask']
            index = 1
            for mask in masks:
                sql = sql + ('' if index == 1 else ',') + ' ' + component_name + '_' + str(index) + '_mask = ' + str(mask)
                index = index + 1

            sql = sql + ' WHERE LineNumber = ? AND Fiducial = ?'

            # TODO: do I need to send flight number as well because line
            # number could be non-unique
            cursor.execute(sql, (line_number, fiducial))

    return Response(json.dumps({'response': 'OK',
                                'message': 'changes applied'}),
                    mimetype='application/json')


@app.route('/api/applyMaskToAllChannelsBetweenFiducials', methods=['POST'])
def applyMaskToAllChannelsBetweenFiducials():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]

    database_path = os.path.join(app.config['UPLOAD_FOLDER'], user_token, project_id, 'database.db')

    mask_details = json.loads(request.form["mask_details"])

    line_number = mask_details['line_number']
    component_names = getComponentColumnNames(mask_details['component_name'], project_id)
    mask = mask_details['mask']

    fiducial_min, fiducial_max = mask_details['range']

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        sql = 'UPDATE dataframe SET ' + \
            ("_mask = " + str(mask) + ",").join(component_names) + "_mask = " + str(mask) + \
            ' WHERE LineNumber = ? AND Fiducial BETWEEN ? AND ?'

        # TODO: do I need to send flight number as well because line
        # number could be non-unique
        cursor.execute(sql, (line_number, fiducial_min, fiducial_max))

    return Response(json.dumps({'response': 'OK',
                                'message': 'changes applied'}),
                    mimetype='application/json')


@app.route('/api/export', methods=['GET'])
def export():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]

    database_path = os.path.join(app.config['UPLOAD_FOLDER'], user_token, project_id, 'database.db')
    export_file_name = user_token + '_' + project_id + '.csv'
    download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], export_file_name)
    with sqlite3.connect(database_path) as connection:
        result_set = pandas.read_sql('SELECT * FROM dataframe', connection)
        result_set.to_csv(download_path)
        
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], export_file_name)