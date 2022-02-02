import numpy as np
import scipy.stats
from math import sqrt
import matplotlib.pyplot as plt


avgPeriods = []
upperConf = []
lowerConf = []
maxes = []


def mean_confidence_interval(data, confidence=0.99):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., sqrt(n-1))

    return m, m-h, m+h


def percentiles(data, bound=0.05):
    data.sort()

    lowerBound = int(len(data) * bound)
    if lowerBound == 0:
        upperBound = len(data) - 1
    else:
        upperBound = len(data) - lowerBound

    return data[lowerBound], data[upperBound]


def graphAvg95(simPeriods):
    for nSims in simPeriods:
        meanConf = mean_confidence_interval(nSims)
        avgPeriods.append(meanConf[0])

        lowerBounded, upperBounded = percentiles(nSims)
        lowerConf.append(lowerBounded)
        upperConf.append(upperBounded)

    xGrid = [x+1 for x in range(len(simPeriods))]
    plt.plot(xGrid, upperConf, 'k--', label='95th Percentile')
    plt.plot(xGrid, avgPeriods, 'k', label='Average Number of Periods')
    plt.plot(xGrid, lowerConf, 'k--', label='5th Percentile')
    plt.tick_params(labelsize='20')
    plt.xlabel("Market Size", fontsize='20')
    plt.ylabel("Periods", fontsize='20')
    legend = plt.legend(loc='upper left', shadow=True, fontsize='x-large')
    plt.show()