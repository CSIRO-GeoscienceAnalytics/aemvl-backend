class Station:
    _fiducial_number = None
    _datetime = None
    _date = None
    _time = None
    _angle_x = None
    _angle_y = None
    _height = None
    _latitude = None
    _longitude = None
    _easting = None
    _northing = None
    _elevation = None
    _altitude = None
    _ground_speed = None
    _curr_1 = None
    _plni = None
    _em_decay = None
    _em_decay_error = None
    
    def __init__(
        self,
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

        self._fiducial_number = fiducial_number
        self._datetime = datetime
        self._date = date
        self._time = time
        self._angle_x = angle_x
        self._angle_y = angle_y
        self._height = height
        self._latitude = latitude
        self._longitude = longitude
        self._easting = easting
        self._northing = northing
        self._elevation = elevation
        self._altitude = altitude
        self._ground_speed = ground_speed
        self._curr_1 = curr_1
        self._plni = plni
        self._em_decay = em_decay
        self._em_decay_error = em_decay_error
        
    def get_fiducial_number(self):
        return self._fiducial_number

    def get_datetime(self):
        return self._datetime

    def get_date(self):
        return self._date

    def get_time(self):
        return self._time

    def get_angle_x(self):
        return self._angle_x

    def get_angle_y(self):
        return self._angle_y

    def get_height(self):
        return self._height

    def get_latitude(self):
        return self._latitude

    def get_longitude(self):
        return self._longitude

    def get_easting(self):
        return self._easting

    def get_northing(self):
        return self._northing

    def get_elevation(self):
        return self._elevation

    def get_altitude(self):
        return self._altitude

    def get_ground_speed(self):
        return self._ground_speed

    def get_curr_1(self):
        return self._curr_1

    def get_plni(self):
        return self._plni

    def get_em_decay(self):
        return self._em_decay

    def get_em_decay_error(self):
        return self._em_decay_error