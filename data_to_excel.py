import numpy as np
import pandas as pd
import xlsxwriter
import matplotlib.pyplot as plt
import os

ROWS = 8248
LIVE_TIME = 7
REAL_TIME = 8
FIRST_CHANNEL = 12
LAST_CHANNEL = 8203
VOLT = 10
ESTIMATED_MAX_PEAK_WIDTH = 250
DIFF_THRESH = 10
BINS = LAST_CHANNEL - FIRST_CHANNEL + 1
BIN_SIZE = VOLT / BINS

X_TO_E_A = 1
X_TO_E_B = 0

CS_PHOTOPEAK_MIN_BIN = 7250
CS_PHOTOPEAK_MAX_BIN = 7317


def mca_to_numpy(file_name):
    arr = np.zeros((LAST_CHANNEL - FIRST_CHANNEL + 1,))
    data_str = ''
    with open(file_name, 'r') as f:
        for i in range(ROWS):
            if i < FIRST_CHANNEL:
                data_str += f.readline() + '\n'
                continue
            elif i > LAST_CHANNEL:
                break
            arr[i - FIRST_CHANNEL] = int(f.readline())

    return arr, data_str


def x_to_energy(x, a, b=0):
    """

    :param x: ndarray
    :param a: scalar
    :param b: scalar
    :return:
    """
    return a * x + b


def y_to_N(y, x_min, x_max):
    """
    sums the N particles in the range given
    :param y:
    :param x_min: the lower limit of the photopeak in which we want tp sum
    :param x_max: the upper limit of the photopeak
    :return:
    """
    return np.sum(y[x_min:x_max])


def arr_to_crack_N(arr, live_time):
    N = y_to_N(arr, CS_PHOTOPEAK_MIN_BIN, CS_PHOTOPEAK_MAX_BIN)
    N_normalized = N / live_time
    print(f"N:{N_normalized} | Error:", photons_count_errors(arr, live_time,
                                                             CS_PHOTOPEAK_MIN_BIN,
                                                             CS_PHOTOPEAK_MAX_BIN))
    return N_normalized


def extract_live_time(data_str):
    return float(data_str.split('\n\n')[LIVE_TIME].split('-')[-1].strip())


def np_to_df(arr):
    y = arr
    x = np.fromiter(range(0, len(arr)), int)
    x = x * BIN_SIZE

    dx = np.full(arr.shape, BIN_SIZE / np.sqrt(12))
    dy = np.sqrt(y)

    df = pd.DataFrame({
        'x': x, 'y': y, 'dx': dx, 'dy': dy,
        'E': x_to_energy(x, X_TO_E_A, X_TO_E_B)
    })
    return df


def get_peak_idx(arr):
    diff = np.abs(np.diff(arr))
    peak_idxs = np.argwhere(diff > DIFF_THRESH)
    if len(peak_idxs) == 0:
        peak_idxs = np.array([0, len(arr)])
    return np.min(peak_idxs), np.max(peak_idxs)


def photons_count_errors(arr, live_time, min_bin, max_bin):
    return np.sum(np.sqrt(arr)[min_bin: max_bin]) / live_time


def process_some_files(filter_func, files_dir, process_func,
                       process_name_func=lambda x: x):
    """

    :param filter_func: function to filter the relevant files. recommended to use
    function in function for that
    :param dir: dir for the measurments
    :param process_func: function to run on the data
    :return:
    """

    result_dict = {}
    for filename in os.listdir(files_dir):
        if filename.endswith(".mca"):
            if filter_func(filename):
                arr, additional_data = mca_to_numpy(files_dir + '/' + filename)

                result_dict[process_name_func(filename)] = process_func(arr,
                                                                        extract_live_time(
                                                                            additional_data))

    print(result_dict)
    return {k: v for k, v in sorted(result_dict.items(), key=lambda item: item[1])}


def process_each_mca_file(file_name, to_excel=True):
    arr, additional_data = mca_to_numpy(file_name)
    print(f'Peak in {arr.argmax()}')
    peak_start, peak_end = get_peak_idx(arr)
    print(f"Peak starts at {peak_start} and Ends in {peak_end}")
    plt.figure(figsize=(8, 3))
    plt.subplot(121)
    plt.plot(arr)
    line_color = 'r'
    plt.axvline(peak_start, color=line_color)
    plt.axvline(peak_end, color=line_color)
    plt.subplot(122)
    plt.plot(arr)
    addon = 20
    plt.xlim(peak_start - addon, peak_end + addon)
    plt.suptitle(file_name.split('/')[1])
    plt.draw()
    plt.waitforbuttonpress(0)

    df = np_to_df(arr)
    print(df.describe())

    if to_excel:
        df.to_excel(file_name.split('.')[0] + '.xlsx')

    return df


def filter_pass_all(_, __):
    return True


def filter_by_prefix(file_name, prefix):
    return file_name.startswith(prefix)


def observe_file(file_name):
    process_each_mca_file(file_name, False)


def main(files_dir):
    start_file = None
    # start_file='cs137gain100calibration19052000.mca'
    filter_func = filter_pass_all
    data_to_filter_func = None

    iterate_dir(data_to_filter_func, files_dir, filter_func, start_file)


def iterate_dir(data_to_filter_func, files_dir, filter_func, start_file):
    first_file_encountered = False
    for filename in os.listdir(files_dir):
        if filename.endswith(".mca"):
            if filename == start_file or start_file is None:
                first_file_encountered = True

            if first_file_encountered and filter_func(filename, data_to_filter_func):
                process_each_mca_file(files_dir + '/' + filename)


def get_crack_alphas(files_dir):
    def filter_relevant_files(file_name):
        return filter_by_prefix(file_name, 'hole') or file_name == \
               'no_block_470mm_19092020_sameButLonger.mca' or file_name == \
               'absorbtion_3brick.mca'


    alpha_dict = process_some_files(filter_relevant_files, files_dir, arr_to_crack_N)

    print(alpha_dict, sep='\n')
    plt.title('crack N by file')

    files_names, N_values = list(alpha_dict.keys()), list(alpha_dict.values())
    x = [i for i in range(len(N_values))]
    plt.xticks(x, files_names)
    plt.plot(x, N_values)
    plt.show()
    print("Errors: ")


def get_distance_power(files_dir):
    def filter_relevant_files(file_name):
        return filter_by_prefix(file_name, 'cs137gain100') and file_name != \
               'cs137gain100calibration19052000.mca'


    def process_name_func(file_name):
        return file_name.split('mm')[0].split('100')[-1]


    alpha_dict = process_some_files(filter_relevant_files, files_dir, np.max,
                                    process_name_func)

    print(alpha_dict, sep='\n')
    plt.title('photopeak by file')

    files_names, N_values = list(alpha_dict.keys()), list(alpha_dict.values())
    x = [i for i in range(len(N_values))]
    plt.xticks(x, files_names)
    plt.plot(x, N_values)
    plt.show()


if __name__ == '__main__':
    files_dir = 'מדידות'

    # get_distance_power(files_dir)
    get_crack_alphas(files_dir)
    # observe_file(files_dir + '/hole_3on5mm.mca')
    # main(files_dir)
