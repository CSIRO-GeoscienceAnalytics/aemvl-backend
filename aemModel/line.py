class Line:
    _line_number = None
    
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
    
    def get_extent(self):
        easting_min = float("inf")
        easting_max = float("-inf")
        northing_min = float("inf")
        northing_max = float("-inf")
        for station in self.get_stations():
            easting_min = min(easting_min, station.get_easting())
            easting_max = max(easting_max, station.get_easting())
            northing_min = min(northing_min, station.get_northing())
            northing_max = max(northing_max, station.get_northing())
        
        return (easting_min, easting_max, northing_min, northing_max)
    
    def __str__(self):
        return "Not implemented."

    def to_json_friendly(self):
        stations = []
        
        for station in self.get_stations():
            stations.append(station.to_json_friendly())
            
            #if len(stations) == 100:
             #   break

        return {
            'line_number':  self.get_line_number(),
            'stations':    stations
        }