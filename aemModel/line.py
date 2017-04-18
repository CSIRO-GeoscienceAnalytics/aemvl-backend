class Line:
    _line_number = None
    
    # Format of _stations is dict(fiducial_number, Station())
    _stations = dict()
    
    def __init__(self, line_number):
        self._line_number = line_number

    def get_line_number(self):
        return self._line_number
    
    def get_stations(self):
        return self._stations.values()

    def get_station(self, fiducial_number):
        return self._stations[fiducial_number]
    
    def add_station(self, station):
        self._stations[station.get_fiducial_number()] = station