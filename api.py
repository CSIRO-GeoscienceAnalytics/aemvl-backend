import os
import json
import sys
from aemModel.parse import Parse
from flask import request, session, redirect, url_for, send_from_directory
from app import app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
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

            app.logger.debug(sys.getsizeof(flight.get_line(100101).to_json_friendly()))
            try:
                session['test'] = flight.get_line(100101).to_json_friendly()
                session.modified = True
            except Exception as e:
                app.logger.debug(e)

            return redirect(url_for('show_session'))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

## TODO: Don't need this unless we want users to be able to download files.
#@app.route('/uploads/<filename>')
#def uploaded_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#return redirect(url_for('uploaded_file', filename = filename))
@app.route('/clean')
def clean_session():
    session.clear()
    return "clean"
    
    
@app.route('/session')
def show_session():
    return str(session['test'])
