CREATE TABLE `job` (
    `job_id`            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `job_number`        INTEGER NOT NULL
);

CREATE TABLE `flight` (
    `flight_id`         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `job_id`            INTEGER NOT NULL,
    `flight_number`     INTEGER NOT NULL,
    FOREIGN KEY(job_id) REFERENCES job(job_id)
);

CREATE TABLE `line` (
    `line_id`            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `flight_id`          INTEGER NOT NULL,
    `line_number`        INTEGER NOT NULL,
    FOREIGN KEY(flight_id) REFERENCES flight(flight_id)
);

CREATE TABLE `station` (
    `station_id`         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `line_id`            INTEGER NOT NULL,
    `fiducial_number`    REAL NOT NULL,
    `datetime`           REAL NOT NULL,
    `date`               INTEGER NOT NULL,
    `time`               REAL NOT NULL,
    `angle_x`            REAL NOT NULL,
    `angle_y`            REAL NOT NULL,
    `height`             REAL NOT NULL,
    `latitude`           REAL NOT NULL,
    `longitude`          REAL NOT NULL,
    `easting`            REAL NOT NULL,
    `northing`           REAL NOT NULL,
    `elevation`          REAL NOT NULL,
    `altitude`           REAL NOT NULL,
    `ground_speed`       REAL NOT NULL,
    `curr_1`             REAL NOT NULL,
    `plni`               REAL NOT NULL,
    FOREIGN KEY(line_id) REFERENCES line(line_id)
);

CREATE TABLE `measurement` (
    `measurement_id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `station_id`        INTEGER NOT NULL,
    `em_decay`          REAL,
    `em_decay_error`    REAL,
    `sequence`          INTEGER NOT NULL,
    FOREIGN KEY(station_id) REFERENCES station(station_id),
    UNIQUE(station_id, sequence)
);
