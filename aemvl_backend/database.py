import os
import json
import uuid
import glob
import pathlib
from shutil import copy
import sqlite3
import pandas
from flask import jsonify
from osgeo import ogr, osr


outSpatialRef4326 = osr.SpatialReference()
outSpatialRef4326.ImportFromEPSG(4326)
# FIXME: Should be using flask session extension and not a global variable
session = {}
app = None


def get_line_component_by_id(line_number, component, database_path, project_id):
    """
    Gets the Fid and channel data for a given line and component
    """
    channel_columns = get_component_column_names(component, project_id)
    columns = ""
    if(isinstance(channel_columns, list)):
        for x in channel_columns:
            columns += ", " + x

    with sqlite3.connect(database_path) as connection:
        sql = (
            """
            SELECT  Fiducial AS fid """
            + columns
            + """
            FROM    dataframe
            WHERE   LineNumber = """
            + str(line_number)
        )

        result_set = pandas.read_sql(sql, connection)

    return result_set.values

def get_line_numbers(database_path):
    """
    Gets all the line numbers
    """
    with sqlite3.connect(database_path) as connection:
        sql = (
            "SELECT DISTINCT LineNumber FROM dataframe"
        )

        result_set = pandas.read_sql(sql, connection)
    # Return an array of line_numbers
    return result_set.values[:,0]

# Look up a DataDefinition column name in the FlightPlanInfo object to
# see if it is an alias of a well-known name. If it is we will return
# the well-known name, otherwise return the original name:
def get_column_well_known_name(column_name, project_id):
    for well_known_name, alias in session["projects"][project_id][
        "flight_plan_info"
    ].items():
        if column_name == alias:
            return well_known_name

    return column_name


def get_column_name_by_number(number, project_id):
    for column_name, column_number in session["projects"][project_id][
        "data_definition"
    ].items():
        if isinstance(column_number, int) and number == column_number:
            return get_column_well_known_name(column_name, project_id)
        if isinstance(column_number, list) and number in column_number:
            if (
                column_name
                not in session["projects"][project_id]["component_column_offsets"]
            ):
                # This has to be cast to a normal int otherwise it ends
                # up as numpy.int64 which can't be serialised into the
                # session:
                session["projects"][project_id]["component_column_offsets"][
                    column_name
                ] = int(number - 1)

            return (
                column_name
                + "_"
                + str(
                    number
                    - session["projects"][project_id]["component_column_offsets"][
                        column_name
                    ]
                )
            )


def get_component_column_names(component_name, project_id):
    if component_name in session["projects"][project_id]["flight_plan_info"]:
        return component_name

    if component_name in session["projects"][project_id]["data_definition"] and isinstance(
        session["projects"][project_id]["data_definition"][component_name], list
    ):
        column_suffixes = list(
            range(
                session["projects"][project_id]["data_definition"][component_name][0]
                - session["projects"][project_id]["component_column_offsets"][
                    component_name
                ],
                len(session["projects"][project_id]["data_definition"][component_name])
                + 1,
            )
        )
        return [component_name + "_" + str(n) for n in column_suffixes]
    else:
        return component_name


def create_location_4326(x_component, y_component, project_id):
    coordinateSystem = session["projects"][project_id]["flight_plan_info"][
        "CoordinateSystem"
    ]

    # If we're already using WGS84 / 4326 we don't need to perform a
    # conversion:
    if coordinateSystem in ["WGS84", 4326]:
        return str(y_component) + " " + str(x_component)
    else:
        # TODO: I'm assuming that flight_plan_info["CoordinateSystem"]
        # will be an EPSG number, not a name like GDA84, WGS84
        inputEPSG = coordinateSystem

        # create a geometry from coordinates
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x_component, y_component)

        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(inputEPSG)

        coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef4326)
        point.Transform(coordTransform)

        return str(point.GetY()) + " " + str(point.GetX())


def read_config(user_token, project_id):
    global session
    sessionfile_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "session.json"
    )

    if os.path.exists(sessionfile_path):
        with open(sessionfile_path) as json_file_handle:
            session = json.load(json_file_handle)

        if project_id in session["projects"]:
            return

    configfile_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "config.json"
    )

    json_content = None
    data_definition = None
    flight_plan_info = None

    with open(configfile_path) as json_file_handle:
        json_content = json.load(json_file_handle)

    data_definition = json_content["DataDefinition"]
    for column_name, column_number in data_definition.items():
        if isinstance(column_number, list):
            data_definition[column_name] = list(
                range(column_number[0], column_number[1] + 1)
            )

    flight_plan_info = json_content["FlightPlanInfo"]
    flight_plan_info["CoordinateSystem"] = (
        flight_plan_info["CoordinateSystem"].upper()
        if isinstance(flight_plan_info["CoordinateSystem"], str)
        else flight_plan_info["CoordinateSystem"]
    )

    # Create the session if it doesn't exist:
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid1())
        session["projects"] = {}

    session["projects"][project_id] = {}
    session["projects"][project_id]["csv_config"] = json_content["CSVConfig"]
    session["projects"][project_id]["flight_plan_info"] = flight_plan_info
    session["projects"][project_id]["em_info"] = json_content["EMInfo"]
    session["projects"][project_id]["export_for_inversion"] = json_content[
        "ExportForInversion"
    ]
    session["projects"][project_id]["data_definition"] = data_definition
    session["projects"][project_id]["component_column_offsets"] = {}

    with open(sessionfile_path, "w") as handle:
        json.dump(session, handle, ensure_ascii=False)


def start_session(datafile_handle, configfile_handle, user_token, project_id, override):

    project_path = os.path.join(app.config["UPLOAD_FOLDER"], user_token, project_id)

    if os.path.exists(project_path):
        if override:
            files = glob.glob(os.path.join(project_path, "*"))
            for f in files:
                os.remove(f)
        else:
            return jsonify(
                {"response": "ERROR", "message": project_path + " already exists."}
            )
    else:
        pathlib.Path(project_path).mkdir(parents=True)

    datafile_path = os.path.join(project_path, "data.xyz")
    datafile_handle.save(datafile_path)

    configfile_path = os.path.join(project_path, "config.json")
    configfile_handle.save(configfile_path)

    cached_database_name = (
        os.path.splitext(datafile_handle.filename)[0][len("data/") :] + ".db"
    )
    cached_database_path = os.path.join("data", cached_database_name)

    db_path = os.path.join(project_path, "database.db")
    cached_component_column_offsets_path = os.path.join(
        "data",
        os.path.splitext(datafile_handle.filename)[0][len("data/") :]
        + ".component_column_offsets.json",
    )

    read_config(user_token, project_id)

    is_test_dataset = datafile_handle.filename.startswith("data")
    if is_test_dataset and os.path.isfile(cached_database_path):
        # There is a cached version of the database availble.
        copy(os.path.join("data", cached_database_name), db_path)

        with open(cached_component_column_offsets_path) as json_file_handle:
            session["projects"][project_id]["component_column_offsets"] = json.load(
                json_file_handle
            )

    else:
        # There was no cached version available, or the user has uploaded their own file:
        separator = (
            "\s+"
            if session["projects"][project_id]["csv_config"]["Separator"] == "w"
            else session["projects"][project_id]["csv_config"]["Separator"]
        )
        header = (
            None
            if session["projects"][project_id]["csv_config"]["HeaderLine"] is False
            else 0
        )
        datafile_path = os.path.join(
            app.config["UPLOAD_FOLDER"], user_token, project_id, "data.xyz"
        )

        number_of_lines = 100000
        new_column_names = []
        for dataframe_chunk in pandas.read_csv(
            datafile_path, sep=separator, header=header, chunksize=number_of_lines
        ):

            # On the first iteration create the sqlite file and indices.
            if not new_column_names:
                for i in range(1, dataframe_chunk.shape[1] + 1):
                    new_column_names.append(get_column_name_by_number(i, project_id))

            dataframe_chunk.columns = new_column_names
            dataframe_chunk["LOCATION_4326"] = dataframe_chunk.apply(
                lambda row: create_location_4326(
                    row["XComponent"], row["YComponent"], project_id
                ),
                axis=1,
            )

            # Add a '_mask' column for every column that was generated from a
            # list in the DataDefinition:
            for key, value in session["projects"][project_id][
                "data_definition"
            ].items():
                if isinstance(value, list):
                    for column_number in value:
                        dataframe_chunk[
                            key
                            + "_"
                            + str(
                                column_number
                                - session["projects"][project_id][
                                    "component_column_offsets"
                                ][key]
                            )
                            + "_mask"
                        ] = False

            if not new_column_names:
                with sqlite3.connect(db_path) as connection:
                    dataframe_chunk.to_sql(
                        "dataframe", connection, index=False, if_exists="replace"
                    )
                    cursor = connection.cursor()
                    cursor.execute(
                        "CREATE INDEX `ix_JobNumber` ON `dataframe` (`JobNumber`)"
                    )
                    cursor.execute(
                        "CREATE INDEX `ix_Fiducial` ON `dataframe` (`Fiducial`)"
                    )
                    cursor.execute(
                        "CREATE INDEX `ix_LineNumber` ON `dataframe` (`LineNumber`)"
                    )
                    cursor.execute(
                        "CREATE INDEX `ix_FlightNumber` ON `dataframe` (`FlightNumber`)"
                    )
                    cursor.execute(
                        "CREATE UNIQUE INDEX `ix_unique_JobNumber_Fiducial_LineNumber_LineNumber` ON `dataframe` (`JobNumber`, `Fiducial`, `LineNumber`, `LineNumber`)"
                    )

            # Now just insert all the new lines to the SQL file
            else:
                with sqlite3.connect(db_path) as connection:
                    dataframe_chunk.to_sql(
                        "dataframe", connection, index=False, if_exists="append"
                    )

        # Populate cache:
        if is_test_dataset:
            cached_database_name = (
                os.path.splitext(datafile_handle.filename)[0][len("data/") :] + ".db"
            )
            copy(db_path, os.path.join("data", cached_database_name))

            with open(cached_component_column_offsets_path, "w") as handle:
                json.dump(
                    session["projects"][project_id]["component_column_offsets"],
                    handle,
                    ensure_ascii=False,
                )

    sessionfile_path = os.path.join(
        app.config["UPLOAD_FOLDER"], user_token, project_id, "session.json"
    )
    with open(sessionfile_path, "w") as handle:
        json.dump(session, handle, ensure_ascii=False)

    return jsonify({"response": "OK", "message": "Started project " + project_id + "."})


def expand_component_names(project_id, component_names):
    """
    Takes a list of component_names and adds any required cascade targets.
    For example: if HM_Z is provided and the config file indicates that
    HM_Z should CascadeMaskingTo HM_X then ["HM_Z", "HM_X"] will be returned. 
    """
    cascade_rules = {}
    for em_info in session["projects"][project_id]["em_info"]:
        for component in em_info["Components"]:
            if "CascadeMaskingTo" in component:
                cascade_rules[component["Name"]] = component["CascadeMaskingTo"]

    new_component_names = []
    for component_name in component_names:
        new_component_names.append(component_name)
        if component_name in cascade_rules:
            for cascade_target in cascade_rules[component_name]:
                if cascade_target not in component_names:
                    new_component_names.append(cascade_target)

    return new_component_names
