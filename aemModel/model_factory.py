from aemModel.job import Job
from app import app

class ModelFactory:
    # Format of _jobs is dict(job_number, Job())
    _jobs = dict()

    def __init__(self):
        pass

    def register_row(
        self,
        job_number,
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

        if job_number not in self._jobs:
            self._jobs[job_number] = Job(job_number)

        self._jobs[job_number].register_row(
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
            em_decay_error
        )

    def build_model(self):
        return self._jobs.values()

    def __str__(self):
        return "Not implemented."
