import random
import Graphing
# Note max number of periods is hard coded to size of market in the event of infinite convergence

maxN = 20
simNumber = 100
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

def firmOffers(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects):
    for firmIdx, firmRankings in enumerate(potential):  # Find out where each individual firm applies
        if firmIdx not in exitedFirms:  # The given firm has already left the market
            offerHeld = False
            for workersOffers in workerOffers:  # Iterate over each worker to ensure the firm does not currently have a held offer.
                if firmIdx in workersOffers:
                    offerHeld = True

            if offerHeld is False:  # If the firms offer is already held then move on to next firm
                topWorkerUtility, topWorkerIdx = -1, -1  # Given that the firms offer has not been held yet, find their top remaining worker
                for workerIdx, utility in enumerate(firmRankings):
                    if workerIdx not in firmRejects[firmIdx] and utility[0] > topWorkerUtility and workerIdx not in exitedWorkers:
                        topWorkerUtility, topWorkerIdx = utility[0], workerIdx

                workerOffers[topWorkerIdx].append(firmIdx)  # Fill in the firms offer to its top worker

    return workerOffers


def workerResponses(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects):
    newlyExitedFirms = []
    for workerIdx in range(len(potential)):  # Determine how each worker responds
        if workerIdx not in exitedWorkers:  # The worker has already left
            bestFirmUtility, bestFirmIdx = -1, -1
            for firmIdx, utility in enumerate(potential):  # Find the workers best remaining firm
                if utility[workerIdx][1] > bestFirmUtility and firmIdx not in exitedFirms:
                    bestFirmUtility, bestFirmIdx = utility[workerIdx][1], firmIdx

            if bestFirmIdx in workerOffers[workerIdx]:
                newlyExitedFirms.append(bestFirmIdx)
                exitedWorkers.append(workerIdx)

                for firmIdx in workerOffers[workerIdx]:  # reject all applying firms
                    firmRejects[firmIdx].append(workerIdx)
                workerOffers[workerIdx] = []
            elif workerOffers[workerIdx]:  # If at least one firm made an offer to the worker (but not its best)
                bestOfferUtility, bestOfferingFirmIdx = -1, -1
                for firmIdx, utility in enumerate(potential):  # Find the best such firm
                    if utility[workerIdx][1] > bestOfferUtility and firmIdx in workerOffers[workerIdx]:
                        bestOfferUtility, bestOfferingFirmIdx = utility[workerIdx][1], firmIdx

                for firmIdx in workerOffers[workerIdx]:  # For every firm which is not the worker's most preferred offering firm reject
                    if firmIdx != bestOfferingFirmIdx:
                        firmRejects[firmIdx].append(workerIdx)
                        workerOffers[workerIdx].remove(firmIdx)

    exitedFirms.extend(newlyExitedFirms)
    return exitedFirms, exitedWorkers, workerOffers, firmRejects


def period(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects):  # Run a single period of the DA mechanism
    workerOffers = firmOffers(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects)

    exitedFirms, exitedWorkers, workerOffers, firmRejects = workerResponses(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects)

    return exitedFirms, exitedWorkers, workerOffers, firmRejects


def simulation(potential):
    exitedFirms = []
    exitedWorkers = []  # Lists of players which have left the market
    workerOffers = [[] for worker in range(len(potential))]  # Lists by worker of firms which have made them offers
    firmRejects = [[] for worker in range(len(potential))]  # Lists by worker of firms they have rejected

    endPeriod = 0

    while len(exitedFirms) != len(potential) and endPeriod < len(potential):
        exitedFirms, exitedWorkers, workerOffers, firmRejects = period(potential, exitedFirms, exitedWorkers, workerOffers, firmRejects)
        endPeriod += 1

    return endPeriod


def main(start=1, end=None):
    if not end:
        end = maxN

    simPeriods = []
    for n in range(start, end+1):  # For each market size run simulations of random markets
        simPeriods.append([])

        for simI in range(simNumber):  # Given market size n, run a single simulation
            potential = generateMatrix(n)
            endPeriod = simulation(potential)
            simPeriods[n-1].append(endPeriod)

    return simPeriods

simPeriods = main()

Graphing.graphAvg95(simPeriods)