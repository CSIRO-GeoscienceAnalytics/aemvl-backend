from aemModel.flight import Flight

class Job:
    _job_number = None
    
    # Format of _flights is dict(flight_number, Flight())
    _flights = dict()

    def __init__(self, job_number):
        self._job_number = job_number

    def get_job_number(self):
        return self._job_number

    def get_flights(self):
        return self._flights.values()
    
    def register_row(
        self,
        flight_number,
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
            
        if flight_number not in self._flights:
            self._flights[flight_number] = Flight(flight_number)
        
        self._flights[flight_number].register_row(
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
            em_decay_error
        )