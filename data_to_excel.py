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


def np_to_df(arr):
    y = arr
    x = np.fromiter(range(0, len(arr)), int)
    x=x*BIN_SIZE

    dx = np.full(arr.shape, BIN_SIZE / np.sqrt(12))
    dy = np.sqrt(y)


    df = pd.DataFrame({'x': x, 'y': y, 'dx': dx, 'dy': dy})
    return df


def get_peak_idx(arr):
    diff = np.abs(np.diff(arr))
    peak_idxs = np.argwhere(diff > DIFF_THRESH)
    if len(peak_idxs) == 0:
        peak_idxs = np.array([0,len(arr)])
    return np.min(peak_idxs), np.max(peak_idxs)


def process(file_name):
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
    df.to_excel(file_name.split('.')[0] + '.xlsx')


if __name__ == '__main__':
    files_dir = 're12_5_2020'
    start_file = None
    start_file='cs137gain100calibration19052000.mca'
    first_file_encountered = False

    for filename in os.listdir(files_dir):
        if filename.endswith(".mca"):
            if filename == start_file or start_file is None:
                first_file_encountered =True

            if first_file_encountered:
                process(files_dir + '/' + filename)

