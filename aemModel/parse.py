import sys
import pprint
from app import app
from aemModel.model_factory import ModelFactory
import pandas
import re

class Parse:
    model_factory = None

    def __init__(self):
        self.model_factory = ModelFactory()

    def parse_file(self, path):
        column_aliases = {
            # Key name          # Array of acceptable names for this column (they get turned into regular expressions)
            'job_number':       ['Job_No'],
            'flight_number':    ['Flight'],
            'line_number':      ['Line'],
            'fiducial_number':  ['Fid'],
            'datetime':         ['DateTime'],
            'date':             ['Date'],
            'time':             ['Time'],
            'angle_x':          ['AngleX'],
            'angle_y':          ['AngleY'],
            'height':           ['Height'],
            'latitude':         ['Lat'],
            'longitude':        ['Lon'],
            'easting':          ['E_MGA54'],
            'northing':         ['N_MGA54'],
            'elevation':        ['DEM_AHD'],
            'altitude':         ['Alt_AHD'],
            'ground_speed':     ['GdSpeed'],
            'curr_1':           ['Curr_1'],
            'plni':             ['PLNI'],
            # TODO: Are hm_z and em_decay really the same thing? Probably not. Check with Aaron.
            'em_decay':         ['HM_Z_\[([0-9]+)\]'],
            'em_decay_error':   ['HM_X_\[([0-9]+)\]']
        }

        # Turn all aliases into regular expressions:
        for key in column_aliases:
            for i in range(len(column_aliases[key])):
                column_aliases[key][i] = re.compile(column_aliases[key][i])

        columns_dict = {
            'em_decay': [],
            'em_decay_error': []
        }
        
        em_decay_format = None
        em_decay_error_format = None
        
        # Map columns from file to columns_dict:
        dataframe = pandas.read_csv(path, delim_whitespace=True)
        for file_column in dataframe.columns:
            for key, alias_regexes in column_aliases.items():
                for alias_regex in alias_regexes:
                    result = alias_regex.match(file_column)
                    if result:
                        if key in ('em_decay', 'em_decay_error'):
                            index = int(result.groups()[0])
                            columns_dict[key].append(index)
                            
                            if not em_decay_format and key == 'em_decay':
                                em_decay_format = file_column.replace(str(index), '*')
                            elif not em_decay_error_format and key == 'em_decay_error':
                                em_decay_error_format = file_column.replace(str(index), '*')
                        else:
                            columns_dict[key] = file_column
        
        for column, row in dataframe.iterrows():
            em_decay = []
            for i in columns_dict['em_decay']:
                em_decay.append(float(row[em_decay_format.replace('*', str(i))]))

            em_decay_error = []
            for i in columns_dict['em_decay_error']:
                em_decay_error.append(float(row[em_decay_error_format.replace('*', str(i))]))

            self.model_factory.register_row(
                job_number =        int(row[columns_dict['job_number']]),
                flight_number =     float(row[columns_dict['flight_number']]),
                line_number =       int(row[columns_dict['line_number']]),
                fiducial_number =   float(row[columns_dict['fiducial_number']]),
                datetime =          float(row[columns_dict['datetime']]),
                date =              int(row[columns_dict['date']]),
                time =              float(row[columns_dict['time']]),
                angle_x =           float(row[columns_dict['angle_x']]),
                angle_y =           float(row[columns_dict['angle_y']]),
                height =            float(row[columns_dict['height']]),
                latitude =          float(row[columns_dict['latitude']]),
                longitude =         float(row[columns_dict['longitude']]),
                easting =           float(row[columns_dict['easting']]),
                northing =          float(row[columns_dict['northing']]),
                elevation =         float(row[columns_dict['elevation']]),
                altitude =          float(row[columns_dict['altitude']]),
                ground_speed =      float(row[columns_dict['ground_speed']]),
                curr_1 =            float(row[columns_dict['curr_1']]),
                plni =              float(row[columns_dict['plni']]),
                em_decay =          em_decay,
                em_decay_error =    em_decay_error
            )

        return self.model_factory.build_model()
