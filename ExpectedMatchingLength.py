from math import pow
import random
import Graphing
from joblib import Parallel, delayed

random.seed()
maxN = 100  # Maximal market size
simNumber = 5000  # Number of simulations per market size


def generateMatrix(n):  # Generate a random potential by pulling values from ${1, ..., n^2}$
    potential = [[0 for firm in range(n)] for worker in range(n)]
    values = [value for value in range(int(pow(n, 2)))]
    random.shuffle(values)
    i = 0

    for firmId in range(n):
        for workerId in range(n):
            potential[firmId][workerId] = values[i]
            i += 1

    return potential

def period(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects):  # Run a single period of the DA mechanism
    workerOffers = firmOffers(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects)

    exitedFirms, exitedWorkers, workerOffers, firmRejects = workerResponses(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects)

    return exitedFirms, exitedWorkers, workerOffers, firmRejects

def firmOffers(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects):
    for firmIdx, firmRankings in enumerate(potential):  # Find out where each individual firm applies
        if firmIdx not in exitedFirms:  # The given firm has already left the market
            offerHeld = False
            for workersOffers in workerOffers:  # Iterate over each worker to ensure the firm does not currently have a held offer.
                if firmIdx in workersOffers:
                    offerHeld = True

            if offerHeld is False:  # If the firms offer is already held then move on to next firm
                topWorker, topWorkerIdx = -1, -1  # Given that the firms offer has not been held yet, find their top remaining worker
                for workerIdx, worker in enumerate(firmRankings):
                    if workerIdx not in firmRejects[firmIdx] and worker > topWorker and workerIdx not in exitedWorkers:
                        topWorker, topWorkerIdx = worker, workerIdx

                workerOffers[topWorkerIdx].append(firmIdx)  # Fill in the firms offer to its top worker

    return workerOffers

def workerResponses(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects):
    newlyExitedFirms = []
    for workerIdx in range(len(potential)):  # Determine how each worker responds
        if workerIdx not in exitedWorkers:  # The worker has already left
            bestFirm, bestFirmIdx = -1, -1
            for firmIdx, firm in enumerate(potential):  # Find the workers best remaining firm
                if firm[workerIdx] > bestFirm and firmIdx not in exitedFirms:
                    bestFirm, bestFirmIdx = firm[workerIdx], firmIdx

            if bestFirmIdx in workerOffers[workerIdx]:
                newlyExitedFirms.append(bestFirmIdx)
                exitedWorkers.append(workerIdx)

                for firmIdx in workerOffers[workerIdx]:  # reject all applying firms
                    firmRejects[firmIdx].append(workerIdx)
                workerOffers[workerIdx] = []
            elif workerOffers[workerIdx]:  # If at least one firm made an offer to the worker (but not its best)
                bestOfferingFirm, bestOfferingFirmIdx = -1, -1
                for firmIdx, firm in enumerate(potential):  # Find the best such firm
                    if firm[workerIdx] > bestOfferingFirm and firmIdx in workerOffers[workerIdx]:
                        bestOfferingFirm, bestOfferingFirmIdx = firm[workerIdx], firmIdx

                toRemove = []
                for firmIdx in workerOffers[workerIdx]:  # For every firm which is not the worker's most preferred offering firm reject
                    if firmIdx != bestOfferingFirmIdx:
                        firmRejects[firmIdx].append(workerIdx)
                        toRemove.append(firmIdx)

                for removal in toRemove:
                    workerOffers[workerIdx].remove(removal)

    exitedFirms.extend(newlyExitedFirms)
    return exitedFirms, exitedWorkers, workerOffers, firmRejects

def simulation(n):
    potential = generateMatrix(n)
    exitedFirms = []
    exitedWorkers = []  # Lists of players which have left the market
    workerOffers = [[] for worker in range(len(potential))]  # Lists by worker of firms which have made them offers
    firmRejects = [[] for worker in range(len(potential))]  # Lists by worker of firms they have rejected

    endPeriod = 0

    while len(exitedFirms) != len(potential):
        exitedFirms, exitedWorkers, workerOffers, firmRejects = period(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects)
        endPeriod += 1

    return endPeriod


def displayMatrix(matrix):
    for firm in matrix:
        print(firm)


def sampleSimulation(n):
    potential = generateMatrix(n)
    displayMatrix(potential)

    print(simulation(potential))


def main(start=1, end=None):
    if not end:
        end = maxN

    simPeriods = []
    for n in range(start, end+1):  # For each market size run simulations of random markets
        print(n)

        nPeriodResults = Parallel(n_jobs=2)(delayed(simulation)(n) for i in range(simNumber))

        simPeriods.append(nPeriodResults)

    return simPeriods


periods = main()

Graphing.graphAvg95(periods)


