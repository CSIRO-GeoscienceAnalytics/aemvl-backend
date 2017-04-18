from aemModel.line import Line
from aemModel.station import Station

class Flight:
    _flight_number = None
    
    # Format of _lines is dict(line_number, Line())
    _lines = dict()

    def __init__(self, flight_number):
        self._flight_number = flight_number
        
    def get_flight_number(self):
        return self._flight_number

    def get_lines(self):
        return self._lines.values()

    def get_line(self, line_number):
        return self._lines[line_number]
    
    def register_row(
        self,
        line_number,
        fiducial_number,
        datetime,
        date,
        time,
        angle_x,
        angle_y,
        height,
        latitude,
        longitude,
        easting,
        northing,
        elevation,
        altitude,
        ground_speed,
        curr_1,
        plni,
        em_decay,
        em_decay_error):
            
        if line_number not in self._lines:
            self._lines[line_number] = Line(line_number)
        
        self._lines[line_number].add_station(Station(
            fiducial_number,
            datetime,
            date,
            time,
            angle_x,
            angle_y,
            height,
            latitude,
            longitude,
            easting,
            northing,
            elevation,
            altitude,
            ground_speed,
            curr_1,
            plni,
            em_decay,
            em_decay_error)
        )