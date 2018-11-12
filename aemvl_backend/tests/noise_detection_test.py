import os
import time
import numpy as np
import pandas as pd
import aemvl_backend.database as db
import aemvl_backend.noise_detection as nd

# Note: DB needs to exist and pytest needs to be run from project root
dirname = os.path.dirname(__file__)

def read_line(f):
    df = pd.read_csv(f, sep=",")
    return df.values

def test_noise_dections_on_line():
    # Test data set is representative of the return of get_line_component_by_id
    m = read_line(os.path.join(dirname, "data/200301_hmx.csv"))
    start = time.time()
    nd.detect_noise_sections_for_line(m, 0.003, 0.01, 20, 10, 2, 4)
    end = time.time()  
    print("Single Line took" + str(end - start))

def test_noise_dections_on_survey_non_par():
    # Test data set is representative of the return of get_line_component_by_id
    m = [read_line(os.path.join(dirname, "data/200101.csv")), 
        read_line(os.path.join(dirname, "data/200201.csv")),
        read_line(os.path.join(dirname, "data/200301.csv")),
        read_line(os.path.join(dirname, "data/200301_hmx.csv")),
        read_line(os.path.join(dirname, "data/200301_lmz.csv")),
        read_line(os.path.join(dirname, "data/200401.csv")),
        read_line(os.path.join(dirname, "data/200501.csv"))
        ]
    results = []
    
    start = time.time()  
    for x in range(len(m)):
        results.append(nd.detect_noise_sections_for_line(m[x], 0.003, 0.01, 20, 10, 2, 4))
    
    end = time.time()
    print("Non Paralel Survey took " + str(end - start))

def test_noise_dections_on_survey_pool():
    # Test data set is representative of the return of get_line_component_by_id
    m = [read_line(os.path.join(dirname, "data/200101.csv")), 
        read_line(os.path.join(dirname, "data/200201.csv")),
        read_line(os.path.join(dirname, "data/200301.csv")),
        read_line(os.path.join(dirname, "data/200301_hmx.csv")),
        read_line(os.path.join(dirname, "data/200301_lmz.csv")),
        read_line(os.path.join(dirname, "data/200401.csv")),
        read_line(os.path.join(dirname, "data/200501.csv"))
        ]
    line_numbers = [200101, 200201, 200301, 200302, 200303, 200401, 200501]
    start = time.time()
    results = nd.detect_noise_sections_for_survey_pool(line_numbers, m, 0.003, 0.01, 20, 10, 2, 4)
    end = time.time()
    print("Paralel Survey took " + str(end - start))
    print(results)


def test_get_line_numbers():
    line_numbers = db.get_line_numbers(os.path.join(dirname, "data/test.db"))

    assert(isinstance(line_numbers, np.ndarray))
    assert(len(line_numbers) > 1)

def test_noise_merging():
    noise_array = []
    noise_array.append(
        {
            "index_from": 0,
            "index_to": 8,
            "fid_from": "100",
            "fid_to": "150",
        })
    noise_array.append(
        {
            "index_from": 10,
            "index_to": 30,
            "fid_from": "100",
            "fid_to": "150",
        })
    noise_array.append(
        {
            "index_from": 30,
            "index_to": 50,
            "fid_from": "100",
            "fid_to": "150",
        })
    noise_array.append(
        {
            "index_from": 40,
            "index_to": 60,
            "fid_from": "100",
            "fid_to": "150",
        })
    noise_array.append(
        {
            "index_from": 65,
            "index_to": 80,
            "fid_from": "100",
            "fid_to": "150",
        })
    merged_ranges = nd.mergeRanges(noise_array)
    print(merged_ranges)
    assert(len(merged_ranges) == 3)

