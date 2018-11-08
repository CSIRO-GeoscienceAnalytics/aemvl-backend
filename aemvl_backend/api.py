import os
import re
import math
import json
import glob
import sqlite3
from shutil import rmtree, copy
from flask import request, jsonify, redirect, Response, send_from_directory
from werkzeug.datastructures import FileStorage
import pandas
from app import app

# Bit of a hack to start the code splitting process
import database as db
from noise_detection import detect_noise_sections_for_line

# Bit of a hack but keeps the db module clean for testing
db.app = app

def human_readable_bytes(number_of_bytes):
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if number_of_bytes < 1024.0:
            return "%3.1f %s" % (number_of_bytes, x)
        number_of_bytes /= 1024.0


def generate_response(result_set):
    accept_headers = request.headers.get("Accept").split(",")

    if "text/csv" in accept_headers:
        return Response(result_set.to_csv(index=False), mimetype="text/csv")
    elif "text/html" in accept_headers:
        return Response(result_set.to_html(index=False), mimetype="text/html")
    else:
        return jsonify(
            {
                "response": "ERROR",
                "message": "Unsupported accept header provided: " + str(accept_headers),
            }
        )


@app.route("/api/listTestDatasets", methods=["POST"])
def list_test_datasets():
    file_names = glob.glob("data/*.xyz")

    return_value = []
    for file_name in file_names:
        file_size = os.stat(file_name).st_size
        file_name_no_extension = os.path.splitext(file_name)[0]
        return_value.append(
            {
                "file_name": file_name_no_extension[len("data/") :],
                "file_size_bytes": file_size,
                "file_size_readable": human_readable_bytes(file_size),
                "database_cached": os.path.isfile(file_name_no_extension + ".db"),
            }
        )

    return jsonify({"response": "OK", "return_value": return_value})


@app.route("/api/listProjects", methods=["POST"])
def list_projects():
    user_token = request.form["user_token"]
    users_path = os.path.join(app.config["UPLOAD_FOLDER"], user_token, "*")

    project_ids = glob.glob(users_path)
    project_ids = [
        project_id[len("./uploads/") + len(user_token) + 1 :]
        for project_id in project_ids
    ]

    return jsonify({"response": "OK", "return_value": project_ids})


@app.route("/api/deleteProject", methods=["POST"])
def delete_project():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    project_path = os.path.join(app.config["UPLOAD_FOLDER"], user_token, project_id)

    if os.path.isdir(project_path):
        try:
            rmtree(project_path)
            return jsonify(
                {"response": "OK", "message": "Deleted project " + project_id + "."}
            )
        except Exception as exception:
            return jsonify({"response": "ERROR", "message": str(exception)})
    else:
        return jsonify(
            {
                "response": "ERROR",
                "message": "Project with id, " + project_id + ", did not exist.",
            }
        )


@app.route("/api/startTestSession", methods=["POST"])
def start_test_session():
    test_dataset_name = request.form["test_dataset_name"]
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    override = request.form.get("override", "0").lower() in ["true", "1", "override"]
    with open("data/" + test_dataset_name + ".xyz", "rb") as datafile_handle:
        with open("data/" + test_dataset_name + ".json", "rb") as configfile_handle:
            return db.start_session(
                FileStorage(datafile_handle),
                FileStorage(configfile_handle),
                user_token,
                project_id,
                override,
            )


@app.route("/api/upload", methods=["POST"])
def api_upload():
    # check that the POST request is complete:
    if "datafile" not in request.files:
        return jsonify({"response": "ERROR", "message": "Datafile not provided"})

    if "configfile" not in request.files:
        return jsonify({"response": "ERROR", "message": "Config file not provided"})

    datafile_handle = request.files["datafile"]
    configfile_handle = request.files["configfile"]
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    override = request.form.get("override", "0").lower() in ["true", "1", "override"]

    return db.start_session(
        datafile_handle, configfile_handle, user_token, project_id, override
    )


# Used to create the map with all the flight lines:
@app.route("/api/getLines", methods=["POST"])
def get_lines():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    with sqlite3.connect(database_path) as connection:
        result_set = pandas.read_sql(
            """ SELECT  Fiducial AS fid,
                        LineNumber AS line,
                        FlightNumber AS flight,
                        LOCATION_4326 AS location
                FROM    dataframe""",
            connection,
        )

        return generate_response(result_set)


# Used to create the multi-line graph:
@app.route("/api/getLine", methods=["POST"])
def get_line():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    line_number = int(request.form["line_number"])
    component_name = request.form["component_name"]

    full_column_names = db.get_component_column_names(component_name, project_id)

    unmasked_column = ""
    masked_column = ""

    for full_column_name in full_column_names:
        unmasked_column = (
            unmasked_column
            + (" || ' ' || " if unmasked_column else "")
            + full_column_name
        )
        masked_column = (
            masked_column
            + (" || ' ' || " if masked_column else "")
            + full_column_name
            + "_mask"
        )

    with sqlite3.connect(database_path) as connection:
        sql = (
            """
            SELECT  Fiducial AS fid,
                    DigitalElevationModel as dem,
                    TxElevation as alt,
              """
            + unmasked_column
            + " AS em"
            + """,
              """
            + masked_column
            + " AS em_mask"
            + """
            FROM    dataframe
            WHERE   LineNumber = """
            + str(line_number)
        )

        result_set = pandas.read_sql(sql, connection)

        return generate_response(result_set)


# Used to create the multi-line graph:
@app.route("/api/detectNoise", methods=["POST"])
def get_noise():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    params = json.loads(request.form["params"])

    line_id = params["line_id"]
    component = params["component"]
    #algorithm = params["algorithm"]
    threshold = params["threshold"]
    window = params["window"] if params["window"] is not None else 20
    channels = params["channels"] if params["channels"] is not None else 4

    if line_id is not None:
        line_data = db.get_line_component_by_id(
            line_id, component, database_path, project_id
        )
        return jsonify([
            {
                "line_id": line_id,
                "noise": detect_noise_sections_for_line(
                    line_data,
                    float(threshold["from"]),
                    float(threshold["to"]),
                    int(window),
                    int(int(window) / 2),
                    channel_group_size=channels
                ),
            }]
        )
    else:
        print("Get all the lines")


@app.route("/api/getEMData", methods=["POST"])
def get_em_data():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    component_name = request.form["component_name"]
    apply_mask = request.form.get("apply_mask", "0").lower() in [
        "true",
        "1",
        "apply_mask",
    ]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    full_column_names = db.get_component_column_names(component_name, project_id)

    unmasked_column = ""
    for full_column_name in full_column_names:
        unmasked_column = (
            unmasked_column
            + (" || ' ' || " if unmasked_column else "")
            + "CASE WHEN "
            + full_column_name
            + "_mask THEN "
            + ("'null'" if apply_mask else full_column_name)
            + " ELSE "
            + full_column_name
            + " END"
        )

    with sqlite3.connect(database_path) as connection:
        sql = (
            """
            SELECT  LOCATION_4326 as location,
              """
            + unmasked_column
            + " AS em"
            + """
            FROM    dataframe"""
        )

        result_set = pandas.read_sql(sql, connection)
        return generate_response(result_set)


@app.route("/api/applyMaskToFiducials", methods=["POST"])
def apply_mask_to_fiducials():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    mask_details = json.loads(request.form["mask_details"])

    line_number = mask_details["line_number"]
    component_names = db.expand_component_names(
        project_id, mask_details["component_names"]
    )
    fiducials_and_masks = mask_details["masks"]

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        for fiducial_and_masks in fiducials_and_masks:
            sql = "UPDATE dataframe SET "

            fiducial = fiducial_and_masks["fid"]
            masks = fiducial_and_masks["mask"]

            first = True
            for component_name in component_names:
                sql = sql + ("" if first else ",")
                first = False
                index = 1
                for mask in masks:
                    sql = (
                        sql
                        + ("" if index == 1 else ",")
                        + " "
                        + component_name
                        + "_"
                        + str(index)
                        + "_mask = "
                        + str(mask)
                    )
                    index = index + 1

            sql = sql + " WHERE LineNumber = ? AND Fiducial = ?"

            cursor.execute(sql, (line_number, fiducial))

        return jsonify({"response": "OK", "message": "Changes applied"})


@app.route("/api/applyMaskToAllChannelsBetweenFiducials", methods=["POST"])
def apply_mask_to_all_channels_between_fiducials():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    mask_details = json.loads(request.form["mask_details"])

    line_number = mask_details["line_number"]
    component_names = db.expand_component_names(
        project_id, mask_details["component_names"]
    )

    full_component_names = []
    for component_name in component_names:
        full_component_names.append(
            db.get_component_column_names(component_name, project_id)
        )

    mask = mask_details["mask"]

    fiducial_min, fiducial_max = mask_details["range"]

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()

        for full_component_name in full_component_names:
            sql = (
                "UPDATE dataframe SET "
                + ("_mask = " + str(mask) + ",").join(full_component_name)
                + "_mask = "
                + str(mask)
                + " WHERE LineNumber = ? AND Fiducial BETWEEN ? AND ?"
            )

            cursor.execute(sql, (line_number, fiducial_min, fiducial_max))

    return jsonify({"response": "OK", "message": "Changes applied"})


@app.route("/api/applyMaskToChannels", methods=["POST"])
def apply_mask_to_channels():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    db.read_config(user_token, project_id)

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )

    mask_details = json.loads(request.form["mask_details"])

    line_number = mask_details["line_number"]
    component_names = db.expand_component_names(
        project_id, mask_details["component_names"]
    )

    mask = mask_details["mask"]

    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()

        for component_name in component_names:
            component_name = [
                component_name + "_" + str(x + 1) + "_mask = " + str(mask)
                for x in mask_details["channels"]
            ]

            sql = (
                "UPDATE dataframe SET "
                + (",").join(component_name)
                + " WHERE LineNumber = ?"
            )

            cursor.execute(sql, [line_number])

    return jsonify({"response": "OK", "message": "Changes applied"})


def get_std_error(channel, channel_mask, additive_error, multiplicative_error):
    if channel_mask == -1:
        return 1e99

    if channel is None:
        return None

    return abs(
        math.sqrt(pow(additive_error, 2) + pow(multiplicative_error * channel, 2))
    )


@app.route("/api/export", methods=["POST"])
def export():
    regex = re.compile(r"_[A-Z]+$", re.IGNORECASE)

    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    # TODO: change to JSON?
    columns_to_export = request.form["columns_to_export"].split(",")
    db.read_config(user_token, project_id)

    fields_to_select = []
    valid_data_config = {}
    for column_to_export in columns_to_export:
        # Find out if column needs to be expanded:
        column_numbers = db.session["projects"][project_id]["data_definition"][
            column_to_export
        ]
        if isinstance(column_numbers, list):
            offset = column_numbers[0] - 1
            column_numbers = [
                column_number - offset for column_number in column_numbers
            ]

            channels = [
                column_to_export + "_" + str(column_number)
                for column_number in column_numbers
            ]

            additive_error = None
            multiplicative_error = None
            # Find the AdditiveError and MultiplicativeError from EMInfo
            for em_info in db.session["projects"][project_id]["em_info"]:
                for component in em_info["Components"]:
                    if component["Name"] == column_to_export:
                        additive_error = component["Descriptor"]["AdditiveError"]
                        multiplicative_error = component["Descriptor"][
                            "MultiplicativeError"
                        ]
                        break

                if additive_error:
                    break

            channels_masked = [
                "get_std_error("
                + column_to_export
                + "_"
                + str(column_number)
                + ", "
                + column_to_export
                + "_"
                + str(column_number)
                + "_mask, "
                + str(additive_error[column_number - 1])
                + ", "
                + str(multiplicative_error[column_number - 1])
                + ") AS "
                + column_to_export
                + "_"
                + str(column_number)
                + "_std"
                for column_number in column_numbers
            ]

            fields_to_select = fields_to_select + channels + channels_masked

            em_abbreviation = regex.sub("", column_to_export)
            if em_abbreviation not in valid_data_config:
                valid_data_config[em_abbreviation] = []

            valid_data_config[em_abbreviation] = valid_data_config[em_abbreviation] + [
                column_to_export + "_" + str(column_number) + "_mask"
                for column_number in column_numbers
            ]
        else:
            column_name = db.get_column_well_known_name(column_to_export, project_id)
            fields_to_select.append(column_name)

    for em_abbreviation, columns in valid_data_config.items():
        fields_to_select.append(
            " * ".join(columns) + " == 0 AS " + em_abbreviation + "_VALID_DATA"
        )

    database_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "database.db"
    )
    export_file_name = user_token + "_" + project_id + ".csv"
    download_path = os.path.join(app.config["DOWNLOAD_FOLDER"], export_file_name)
    with sqlite3.connect(database_path) as connection:
        connection.create_function("get_std_error", 4, get_std_error)
        result_set = pandas.read_sql(
            "SELECT " + ", ".join(fields_to_select) + " FROM dataframe", connection
        )

        result_set.to_csv(download_path, index=False)

        return send_from_directory(app.config["DOWNLOAD_FOLDER"], export_file_name)


@app.route("/api/getConfigFile", methods=["POST"])
def get_config_file():
    user_token = request.form["user_token"]
    project_id = request.form["project_id"]
    configfile_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "config.json"
    )

    with open(configfile_path) as json_file_handle:
        json_content = json.load(json_file_handle)

    return jsonify(
        {
            "response": "OK",
            "return_value": json_content,
            "message": "Config provided for " + project_id,
        }
    )
