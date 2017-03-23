CREATE TABLE `line` (
    `line_id`            INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `line_number`        INTEGER NOT NULL
);

CREATE TABLE `station` (
    `station_id`         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `line_id`            INTEGER NOT NULL,
    `fiducial_number`    INTEGER NOT NULL,    
    `easting`            REAL NOT NULL,
    `northing`           REAL NOT NULL,
    `elevation`          REAL NOT NULL,
    `altitude`           REAL NOT NULL,
    FOREIGN KEY(line_id) REFERENCES line(line_id)
);

CREATE TABLE `measurement` (
    `measurement_id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    `station_id`        INTEGER NOT NULL,
    `em_decay`          REAL,
    `em_decay_error`    REAL,
    `sequence`          INTEGER NOT NULL,
    FOREIGN KEY(station_id) REFERENCES station(station_id)
);
