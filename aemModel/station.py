class Station:
    _fiducial_number = None
    _easting = None
    _northing = None
    _elevation = None
    _altitude = None
    _em_decay = None
    _em_decay_error = None
    
    def __init__(
        self, 
        fiducial_number,
        easting,
        northing,
        elevation,
        altitude,
        em_decay,
        em_decay_error):

        self._fiducial_number = fiducial_number
        self._easting = easting
        self._northing = northing
        self._elevation = elevation
        self._altitude = altitude
        self._em_decay = em_decay
        self._em_decay_error = em_decay_error
        
    def get_fiducial_number(self):
        return self._fiducial_number
        
    def get_easting(self):
        return self._easting
    
    def get_northing(self):
        return self._northing
    
    def get_elevation(self):
        return self._elevation
    
    def get_altitude(self):
        return self._altitude
    
    def get_em_decay(self):
        return self._em_decay
    
    def get_em_decay_error(self):
        return self._em_decay_error
    
    def __str__(self):
        return "Not implemented."
    
    def to_json_friendly(self):
        return {
            'fiducial_number':  self.get_fiducial_number(),
            'easting':          self.get_easting(),
            'northing':         self.get_northing(),
            'elevation':        self.get_elevation(),
            'altitude':         self.get_altitude(),
            'em_decay':         self.get_em_decay(),
            'em_decay_error':   self.get_em_decay_error()
        }
