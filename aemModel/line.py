class Line:
    _line_number = None
    
    _soundings = dict()
    
    def __init__(self, line_number):
        self._line_number = line_number

    def get_line_number(self):
        return self._line_number
    
    def get_soundings(self):
        return self._soundings.values()

    def get_sounding(self, fiducial_number):
        return self._soundings[fiducial_number]
    
    def add_sounding(self, sounding):
        self._soundings[sounding.get_fiducial_number()] = sounding
    
    def get_extent(self):
        easting_min = float("inf")
        easting_max = float("-inf")
        northing_min = float("inf")
        northing_max = float("-inf")
        for sounding in self.get_soundings():
            easting_min = min(easting_min, sounding.get_easting())
            easting_max = max(easting_max, sounding.get_easting())
            northing_min = min(northing_min, sounding.get_northing())
            northing_max = max(northing_max, sounding.get_northing())
        
        return (easting_min, easting_max, northing_min, northing_max)
    
    def __str__(self):
        return "Not implemented."

    def to_json_friendly(self):
        soundings = []
        
        for sounding in self.get_soundings():
            soundings.append(sounding.to_json_friendly())
            
            #if len(soundings) == 100:
             #   break

        return {
            'line_number':  self.get_line_number(),
            'soundings':    soundings
        }