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
photon_count_errors = [0.02598898933151988,
                       0.6095476976856005,
                       1.0930794057043447,
                       1.6504136340715696,
                       2.612809218446254
                       ]

# photon_count_errors = [0.002 for i in range(len(photon_count_cracks))]
cracks_areas = [[0, 0],
                [0.3, 0.5],
                [0.7, 0.5],
                [1, 0.8],
                [1.6, 1.3]]

crack_measure_error = 0.1

# detector_error = 0.5


N = ufloat(17.785, 1.1201709964411966)

h = ufloat(47, 0.1)
d = ufloat(2.3, 0.14)


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
    u_y = [ufloat(photon_count_cracks[i], photon_count_errors[i]) for i in
           range(len(photon_count_cracks))]

    S_detector = calculate_detector_area(u_y[-1], u_x[-1])
    print("the assesment of the detector area is:", S_detector)

    u_approx_x = [calculate_crack_area(u_N, S_detector) for u_N in u_y]

    # real_crack area
    measured_crack_areas = [u.nominal_value for u in u_x]
    d_measured_crack_areas = [u.std_dev for u in u_x]

    # photon counts
    y = [u.nominal_value for u in u_y]
    dy = [u.std_dev for u in u_y]

    # assesment of crack area
    approx_crack_areas = [u.nominal_value for u in u_approx_x]
    error_approx_crack_areas = [u.std_dev for u in u_approx_x]

    measured_idxs = list(range(len(measured_crack_areas)))

    # plot_photon_count_vs_creack_area(d_measured_crack_areas, dy,
    # measured_crack_areas, y)
    #
    # plot_assesment_vs_real_value(approx_crack_areas, d_measured_crack_areas,
    # error_approx_crack_areas, measured_crack_areas)

    fig, ax = plt.subplots()
    ax.errorbar(measured_idxs, approx_crack_areas,
                yerr=error_approx_crack_areas, label='Evaluation of crack area')
    ax.errorbar(measured_idxs, measured_crack_areas, yerr=d_measured_crack_areas,
                label='Measured crack area')
    ax.legend(loc='upper left')
    ax.set_xlabel('Measurement Number [no units]')
    ax.set_ylabel('Crack Area[cm^2]')
    ax.set_title('Evaluation of the crack area against the measured crack area')
    plt.show()

    print("Largest relevant hole is:",calculate_crack_area(N,S_detector) )


def plot_assesment_vs_real_value(approx_x, dx, error_approx_x, x):
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


def plot_photon_count_vs_creack_area(dx, dy, x, y):
    fig, ax = plt.subplots()
    ax.errorbar(x, y,
                xerr=dx,
                yerr=dy,
                fmt='-o')
    ax.set_xlabel('crack area [cm^2]')
    ax.set_ylabel('photon count in photoelectric peak')
    ax.set_title('photon count on photoelectric peak vs crack area')
    plt.show()


if __name__ == '__main__':
    main()
