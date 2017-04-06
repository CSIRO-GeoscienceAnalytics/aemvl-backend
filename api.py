import os
import json
import sys
import sqlite3
import uuid
import pandas
from shutil import copyfile
from aemModel.parse import Parse
from flask import request, session, redirect, url_for, send_from_directory, render_template, Response
from app import app
from werkzeug.utils import secure_filename

DB_FILE_PATH = 'session/'
CSV_TYPE = 1
HTML_TYPE = 2

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_preferred_output_type():
    accept_headers = request.headers.get('Accept').split(',')
    
    if 'text/csv' in accept_headers:
        return CSV_TYPE
    elif 'text/html' in accept_headers:
        return HTML_TYPE
    else:
        return None

@app.route("/")
def hello():
    return redirect(url_for("api")) 

@app.route("/api")
def api():
    return render_template("api.html")

@app.route('/api/upload', methods=['GET', 'POST'])
def api_upload():
    output_type = get_preferred_output_type()
    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file_handle = request.files['file']
        
        # if user does not select file, browser also
        # submit a empty part without filename
        if file_handle.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file_handle and allowed_file(file_handle.filename):
            filename = secure_filename(file_handle.filename)

            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_handle.save(path)
            flight = Parse().parse_file(path)

            try:
                session['database_guid'] = str(uuid.uuid1())

                copyfile('skeleton.db', DB_FILE_PATH + session['database_guid'])
                with sqlite3.connect(DB_FILE_PATH + session['database_guid']) as connection:
                    cursor = connection.cursor()

                    for line in flight.get_lines():
                        cursor.execute('''
                            INSERT INTO line (line_number) VALUES(?)''', (line.get_line_number(),))
                        line_id = cursor.lastrowid
                        
                        for station in line.get_stations():
                            cursor.execute('''
                                INSERT INTO station (
                                    line_id,
                                    fiducial_number,
                                    easting,
                                    northing,
                                    elevation,
                                    altitude) VALUES(?, ?, ?, ?, ?, ?)''', (
                                    line_id,
                                    station.get_fiducial_number(),
                                    station.get_easting(),
                                    station.get_northing(),
                                    station.get_elevation(),
                                    station.get_altitude()
                                )
                            )
                            
                            station_id = cursor.lastrowid
                            
                            em_decay = station.get_em_decay()
                            em_decay_error = station.get_em_decay_error()
                            
                            measurements = []
                            for i in range(len(em_decay)):
                                measurements.append((station_id, em_decay[i], em_decay_error[i], i + 1))
                            
                            cursor.executemany('''
                                INSERT INTO measurement (
                                    station_id,
                                    em_decay,
                                    em_decay_error,
                                    sequence) VALUES(?, ?, ?, ?)''', measurements
                            )

                    connection.commit()
            except Exception as e:
                app.logger.error(e)
            finally:
                pass
                # file_handle.unlink() TODO: remove the uploaded file.

            if output_type == HTML_TYPE:
                return redirect(url_for('api'))
            elif output_type == CSV_TYPE:
                return "file uploaded"            

    return render_template("upload.html")

@app.route('/api/getLines', methods=['GET', 'POST'])
def get_lines():
    output_type = get_preferred_output_type()
    
    with sqlite3.connect(DB_FILE_PATH + session['database_guid']) as connection:
        result_set = pandas.read_sql(
            'SELECT 1 as id, line_id, line_number FROM line',
            connection,
            index_col = 'id')

        if output_type == HTML_TYPE:
            return render_template(
                "dataframe_to_table.html",
                title = 'Lines',
                html = result_set.to_html(
                    index = False,
                    formatters = [
                        lambda line_id: "<a href='{}'>{}</a>".format(url_for('get_stations', line_id = line_id), line_id),
                        str],
                        escape = False))
        elif output_type == CSV_TYPE:
            return Response(result_set.to_csv(index = False), mimetype = 'text/plain')
        else:
            return 'Unsupported output type specified: ' + str(output_type)

@app.route('/api/getStations', defaults={'line_id': None}, methods=['POST'])
@app.route('/api/getStations/<line_id>')
def get_stations(line_id):
    output_type = get_preferred_output_type()
    
    if request.method == 'POST':
        line_id = request.form['line_id']
    
    with sqlite3.connect(DB_FILE_PATH + session['database_guid']) as connection:
        result_set = pandas.read_sql('''
            SELECT  1 as id,
                    station_id,
                    fiducial_number,
                    easting,
                    northing,
                    elevation,
                    altitude
            FROM    station
            WHERE   line_id = ?''',
            connection,
            params = [line_id],
            index_col = 'id')
            
        if output_type == HTML_TYPE:
            return render_template(
                "dataframe_to_table.html",
                title = 'Stations',
                html = result_set.to_html(
                    index = False,
                    formatters = [
                        lambda station_id: "<a href='{}'>{}</a>".format(url_for('get_measurements', station_id = station_id), station_id),
                        str,
                        str,
                        str,
                        str,
                        str],
                        escape = False))
        elif output_type == CSV_TYPE:
            return Response(result_set.to_csv(index = False), mimetype = 'text/plain')
        else:
            return 'Unsupported output type specified: ' + str(output_type)

@app.route('/api/getMeasurements', defaults={'station_id': None}, methods=['POST'])
@app.route('/api/getMeasurements/<station_id>')
def get_measurements(station_id):
    output_type = get_preferred_output_type()
    
    if request.method == 'POST':
        station_id = request.form['station_id']
    
    with sqlite3.connect(DB_FILE_PATH + session['database_guid']) as connection:
        result_set = pandas.read_sql('''
            SELECT  em_decay,
                    em_decay_error
            FROM    measurement
            WHERE   station_id = ?
            ORDER BY sequence''',
            connection,
            params = [station_id])

        if output_type == HTML_TYPE:
            return render_template(
                "dataframe_to_table.html",
                title = 'Measurements',
                html = result_set.to_html(
                    index = False,
                    escape = False))
        elif output_type == CSV_TYPE:
            return Response(result_set.to_csv(index = False), mimetype = 'text/plain')
        else:
            return 'Unsupported output type specified: ' + str(output_type)

@app.route('/api/clean_session')
def clean_session():
    session.clear()
    return "clean"

@app.route('/api/show_session')
def show_session():
    return_value = str(session['database_guid']) if ('database_guid' in session) else ''
    return render_template("show_session.html", session = return_value)