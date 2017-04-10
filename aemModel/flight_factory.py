from aemModel.flight import Flight
from aemModel.line import Line
from aemModel.station import Station
from app import app

class FlightFactory:
    # Format of _headers is dict(key, value)
    _headers = dict()

    # Format of _lines is dict(line_number, Line())
    _lines = dict()

    def __init__(self):
        pass

    def register_header(self, key, value):
        self._headers[key] = value

    def register_station(self, line_number, fiducial_number, easting, northing, elevation, altitude, em_decay, em_decay_error):
        if line_number not in self._lines:
            self._lines[line_number] = Line(line_number)
            app.logger.error(line_number)

        self._lines[line_number].add_station(Station(
            fiducial_number,
            easting,
            northing,
            elevation,
            altitude,
            em_decay,
            em_decay_error
        ))

    def build_flight(self):
        return Flight(self._headers, self._lines)

    def __str__(self):
        return "Not implemented."
