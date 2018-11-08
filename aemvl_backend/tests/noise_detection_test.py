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
    m = read_line(os.path.join(dirname, "data/200101.csv"))
    nd.detect_noise_sections_for_line(m, 0.003, 0.01, 20, 10, 2, 4)

def test_noise_dections_on_survey_par():
    # Test data set is representative of the return of get_line_component_by_id
    m = [read_line(os.path.join(dirname, "data/200101.csv")), read_line(os.path.join(dirname, "data/200201.csv"))]
    line_numbers = [200101, 200201]
    start = time.time()
    results = nd.detect_noise_sections_for_survey_par(line_numbers, m, 0.003, 0.01, 20, 10, 2, 4)
    end = time.time()
    print(end - start)

    print(results)


def test_get_line_numbers():
    line_numbers = db.get_line_numbers(os.path.join(dirname, "data/test.db"))

    assert(isinstance(line_numbers, np.ndarray))
    assert(len(line_numbers) > 1)
