from joblib import Parallel, delayed
import random
import Graphing
# Note max number of periods is hard coded to size of market in the event of infinite convergence

#SEVERAL ERRORS: Fix exit time and don't remove elements while list is iterating

maxN = 200
simNumber = 12500
random.seed()

def generateMatrix(n):
    potential = [[[0, 0] for firm in range(n)] for worker in range(n)]
    values = [value for value in range(int(pow(n, 2)))]
    values2 = [value for value in range(int(pow(n, 2)))]

    random.shuffle(values)
    random.shuffle(values2)
    i = 0

    for firmId in range(n):
        for workerId in range(n):
            potential[firmId][workerId] = [values[i], values2[i]]
            i += 1

    return potential

def firmOffers(potential, workerOffers, firmRejects):
    for firmIdx, firmRankings in enumerate(potential):
        offerHeld = False
        for workersOffers in workerOffers:
            if firmIdx in workersOffers:
                offerHeld = True

        if not offerHeld:
            topWorkerUtility, topWorkerIdx = -1, -1
            for workerIdx, utility in enumerate(firmRankings):
                if workerIdx not in firmRejects[firmIdx] and utility[0] > topWorkerUtility:
                    topWorkerUtility, topWorkerIdx = utility[0], workerIdx

            workerOffers[topWorkerIdx].append(firmIdx)

    return workerOffers

def workerResponses(potential, workerOffers, firmRejects):
    for workerIdx in range(len(potential)):  # Determine how each worker responds
        if workerOffers[workerIdx]:  # If at least one firm made an offer to the worker
            bestOfferUtility, bestOfferingFirmIdx = -1, -1
            for firmIdx, utility in enumerate(potential):  # Find the best such firm
                if utility[workerIdx][1] > bestOfferUtility and firmIdx in workerOffers[workerIdx]:
                    bestOfferUtility, bestOfferingFirmIdx = utility[workerIdx][1], firmIdx

            for firmIdx in workerOffers[workerIdx]:  # For every firm which is not the worker's most preferred offering firm reject
                if firmIdx != bestOfferingFirmIdx:
                    firmRejects[firmIdx].append(workerIdx)
                    workerOffers[workerIdx].remove(firmIdx)

    return workerOffers, firmRejects

def period(potential, workerOffers, firmRejects):  # Run a single period of the DA mechanism
    workerOffers = firmOffers(potential, workerOffers, firmRejects)

    workerOffers, firmRejects = workerResponses(potential, workerOffers, firmRejects)

    for worker in workerOffers:
        if len(worker) > 1:
            return 0, workerOffers, firmRejects

    return 1, workerOffers, firmRejects

def simulation(potential):
    workerOffers = [[] for worker in range(len(potential))]  # Lists by worker of firms which have made them offers
    firmRejects = [[] for worker in range(len(potential))]  # Lists by worker of firms they have rejected

    endPeriod = 0
    allWorkersHaveOffers = 0
    while not allWorkersHaveOffers:
        allWorkersHaveOffers, workerOffers, firmRejects = period(potential, workerOffers, firmRejects)
        endPeriod += 1

    return endPeriod

def runSim(n):
    potential = generateMatrix(n)
    endPeriod = simulation(potential)
    return endPeriod

def main(start=1, end=None):
    if not end:
        end = maxN

    simPeriods = []
    for n in range(start, end+1):  # For each market size run simulations of random markets
        print(n)

        nPeriodResults = Parallel(n_jobs=2)(delayed(runSim)(n) for i in range(simNumber))

        simPeriods.append(nPeriodResults)
    return simPeriods

simPeriods = main()

Graphing.graphAvg95(simPeriods)