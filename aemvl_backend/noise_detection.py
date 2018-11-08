import numpy as np
import multiprocessing as mp


def detect_noise_sections_for_survey_pool(
    line_numbers,
    data: np.ndarray,
    low_threshold: float = 0.003,
    high_threshold: float = 0.01,
    windsize: int = 20,
    step: int = 10,
    channel_step: int = 2,
    channel_group_size: int = 4,):
    """
    Whole survey noise detection with paralel processing
    """
    pool = mp.Pool(4)

    results = [pool.apply_async(detect_noise_sections_for_line_par, args=(line_numbers[i], data[i], low_threshold, high_threshold, windsize, step, channel_step, channel_group_size)) for i in range(len(data))]

    # Get process results from the output queue
    results = [p.get() for p in results]

    return results

def detect_noise_sections_for_line_par(
    line_number,
    data,
    low_threshold: float = 0.003,
    high_threshold: float = 0.01,
    windsize: int = 20,
    step: int = 10,
    channel_step: int = 2,
    channel_group_size: int = 4
    ):

    result = detect_noise_sections_for_line(data, low_threshold, high_threshold, windsize, step, channel_step, channel_group_size)
    
    return (line_number, result)



def detect_noise_sections_for_line(
    data,
    low_threshold: float = 0.003,
    high_threshold: float = 0.01,
    windsize: int = 20,
    step: int = 10,
    channel_step: int = 2,
    channel_group_size: int = 4
):
    
    fid = data[:, 0]
    sig = np.arcsinh(data[:, 1:])

    delta_matrix = get_deltas_from_matrix(sig)
    columns = delta_matrix.shape[0]
    rows = delta_matrix.shape[1]

    # Array of noise index ranges
    noise_array = []

    noise_start = None
    noise_end = None

    for j in range(0, columns, int(step)):
        if (j + windsize) > columns:
            break

        cgs = channel_group_size
        noise = False
        for i in range(0, rows, channel_step):

            if (i + channel_group_size) > rows:
                cgs = rows - i
                # ignore the orphaned channels on the end
                break

            delta_window = delta_matrix[j : j + windsize, i : i + cgs]
            avgsd = np.mean(delta_window.std(axis=1))

            # If window is noisey
            if avgsd > high_threshold or (
                avgsd > low_threshold
                and has_channel_cross_over(sig[j : j + windsize, i : i + cgs])
            ):

                noise = True
                if noise_start is None:
                    noise_start = j

                noise_end = j + windsize
                break

        # Record noise from previous window(s) if this window is not noisy or it is the last window
        if noise_start is not None and (
            noise is False or (j + windsize + step > columns)
        ):
            noise_array.append(
                {
                    "index_from": noise_start,
                    "index_to": noise_end,
                    "fid_from": fid[noise_start],
                    "fid_to": fid[noise_end],
                }
            )
            noise_start = None
            noise_end = None

    return noise_array


def get_deltas_from_matrix(matrix):
    if matrix.shape[0] < 2:
        raise ValueError

    delta_matrix = np.zeros((matrix.shape[0] - 1, matrix.shape[1]))

    for j in range(matrix.shape[1]):
        for i in range(matrix.shape[0] - 1):
            delta_matrix[i][j] = matrix[i][j] - matrix[i + 1][j]

    return delta_matrix


def has_channel_cross_over(matrix):
    if matrix.shape[0] < 2:
        raise ValueError

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1] - 1, 1, -1):
            if matrix[i][j] > matrix[i][j - 1]:
                return True

    return False
