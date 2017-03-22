import sys
import pprint
from aemModel.flight_factory import FlightFactory

class Parse:
    flight_factory = None

    def __init__(self):
        self.flight_factory = FlightFactory()

    def parse_file(self, path):
        has_header = None
        header = dict()
        current_header_key = None

        with open(path, 'r') as file_handle:
            line = file_handle.readline().strip()
            while line:
                ## Deal with parsing the header information if it is available:

                # If has_header is None it means we don't know yet whether or not the Header was present.
                if has_header == None:
                    has_header = line == '/HEADER:'
                elif has_header == True:
                    # If this file has a header we need to alternate reading in their keys and values line-by-line.
                    if current_header_key == None:
                        # If we've reached the column names we will ignore this line and stop parsing the header.
                        if '/   LINE' in line:
                            has_header = False
                            del current_header_key
                        else:
                            current_header_key = line[1:]
                    else:
                        self.flight_factory.register_header(
                            current_header_key, 
                            line[1:].split() if current_header_key == 'X VALUES' else line[1:])
                        current_header_key = None
                elif has_header == False:
                    ## If the header is not present, or it has already been parsed, then parse the data itself:
                    fields = line.split()
                    
                    ## TODO: FIX THIS
                    if len(fields) < 5:
                        line = file_handle.readline().strip()
                        continue
                        

                    self.flight_factory.register_sounding(
                        line_number =       int(fields[0]),                                     # LINE
                        fiducial_number =   int(fields[3]),                                     # FID
                        easting =           float(fields[1]),                                   # X
                        northing =          float(fields[2]),                                   # Y
                        elevation =         float(fields[5]),                                   # TOPO
                        altitude =          float(fields[6]),                                   # ALT
                        em_decay =          [float(x) for x in fields[18:46] if x != 'NaN'],    # DATA_0    ... DATA_28
                        em_decay_error =    [float(x) for x in fields[47:75] if x != 'NaN']     # DATASTD_0 ... DATASTD_28
                    )

                line = file_handle.readline().strip()

        return self.flight_factory.build_flight()
