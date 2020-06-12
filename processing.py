# Writer: Gal Harari
# Date: 06/06/2020
from data_to_excel import *
from uncertainties import ufloat
import numpy as np
import matplotlib.pyplot as plt

photon_count_cracks = [0.02598898933151988,
                       1.1224744325268146,
                       2.690139975480036,
                       5.79865463557465,
                       13.434310818876527]
cracks_areas = [[0, 0],
                [0.3, 0.5],
                [0.7, 0.5],
                [1, 0.8],
                [1.6, 1.3]]

crack_measure_error = 0.2

detector_error = 0.5
N = ufloat(17.785, detector_error)

h = ufloat(47, 0.1)
d = ufloat(5, 0.1)


def calculate_detector_area(N_smallest_crack, smallest_crack_area):
    return ((h + d) / h) ** 2 * smallest_crack_area * N / N_smallest_crack


def calculate_crack_area(N_crack, S_detector):
    return S_detector * N_crack / (((h + d) / h) ** 2 * N)


def main():
    # crack areas
    u_x = [ufloat(x, crack_measure_error) * ufloat(y, crack_measure_error) for x,
                                                                               y in
           cracks_areas]
    # photon count
    u_y = [ufloat(val, detector_error) for val in photon_count_cracks]

    S_detector = calculate_detector_area(u_y[1], u_x[1])
    u_approx_x = [calculate_crack_area(u_N, S_detector) for u_N in u_y]

    x = [u.nominal_value for u in u_x]
    dx = [u.std_dev for u in u_x]
    y = [u.nominal_value for u in u_y]
    dy = [u.std_dev for u in u_y]
    approx_x = [u.nominal_value for u in u_approx_x]
    error_approx_x = [u.std_dev for u in u_approx_x]

    fig, ax = plt.subplots()

    ax.errorbar(x, y,
                xerr=dx,
                yerr=dy,
                fmt='-o')

    ax.set_xlabel('crack area [cm^2]')
    ax.set_ylabel('photon count in photoelectric peak')
    ax.set_title('photon count on photoelectric peak vs crack area')

    plt.show()

    # expected to see y=x line. evaluation of crack size
    fig, ax = plt.subplots()

    ax.errorbar(x, approx_x,
                xerr=dx,
                yerr=error_approx_x,
                fmt='-o', label='evaluation vs measuerd')
    ax.plot(x, x, label='the y=x line')
    ax.legend(loc='upper left')
    ax.set_xlabel('Crack area [cm^2]')
    ax.set_ylabel('Evaluation of crack area based on photon count [cm^2]')
    ax.set_title('Evaluation of the crack area vs the crack area area')

    plt.show()


if __name__ == '__main__':
    main()
