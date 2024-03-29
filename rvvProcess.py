import random
import numpy as np
from itertools import repeat
from Graphing import graphAvg95
from joblib import Parallel, delayed
import time


random.seed()
maxN = 100  # Maximal market size
simNumber = 5000  # Number of simulations per market size
tic = time.perf_counter()


def generateMatrix(n):
    potential = np.arange(pow(n, 2))
    np.random.shuffle(potential)
    potential = np.reshape(potential, (n, n))
    return potential

def setStableMatchPartners(potential, agentList):  # Sets each agent's stable match partner to unadjusted IDs
    numAgents = agentList[0].numAgents
    reducedPot = np.array(potential)

    for i, _ in enumerate(potential):
        indices = np.unravel_index(np.argmax(reducedPot, axis=None), reducedPot.shape)

        originalInd = np.where(potential == reducedPot[indices])
        agentList[originalInd[0][0]].stabPart = originalInd[1][0]
        agentList[originalInd[1][0] + numAgents].stabPart = originalInd[0][0]

        reducedPot = np.delete(np.delete(reducedPot, indices[0], 0), indices[1], 1)

def notStableMatch(agentList):  # Returns true if some agent isn't matched to their stable partner
    for agent in agentList[:int(1/2 * len(agentList))]:  # Only need to check one side of the market
        if agent.notStabMatched():
            return True
    return False

def match(worker, firm, agentList, value):
    assert worker.type == 1 and firm.type == 0, "worker should be entered first"
    worker.unmatchPartner(agentList)
    firm.unmatchPartner(agentList)
    worker.mv, firm.mv = repeat(value, 2)
    worker.partner = firm.id
    firm.partner = worker.id
    worker.topOffer = None

def simulation(n):
    agentList = []
    potential = generateMatrix(n)

    for i, _ in enumerate(potential):  # Set up list of agents
        agentList.append(Agent(i, 0, len(potential)))

    for i, _ in enumerate(potential):  # Firms have len(pot) added to their index
        agentList.append(Agent(i, 1, len(potential)))

    setStableMatchPartners(potential, agentList)

    endPeriod = 0

    while notStableMatch(agentList):  # While the current matches do not contain the stable match
        onePeriod(potential, agentList)
        endPeriod += 1

    return endPeriod

def onePeriod(potential, agentList):
    for firm in agentList[:agentList[0].numAgents]:
        betterResponse(potential, agentList, firm)  # firm randomly selects someone they like to make an offer to

    for worker in agentList[agentList[0].numAgents:]:
        if worker.topOffer:
            firm = agentList[worker.topOffer[0]]
            match(worker, firm, agentList, potential[firm.id][worker.id])

def betterResponse(potential, agentList, firm):  # Uniformly selects any (better) possible partner
    possParts = []  # Set of possible partners

    assert firm.type == 0, "Only firms allowed to make offers"

    for workerNum, value in enumerate(potential[firm.id]):  # Find better possible matches
        if value > firm.mv:  # I like them
            possParts.append(workerNum)

    if possParts:  # As long as there is someone I like
        newPartner = agentList[random.choice(possParts) + firm.numAgents]  # Randomly choose one preferred worker
        newPartner.considerOffer(firm.id, potential[firm.id][newPartner.id])


class Agent:
    numAgents = None

    def __init__(self, id, type, numAgents):
        self.id = id
        self.type = type  # 0 if firm (row agent), 1 if worker (col agent)
        self.mv = -1
        self.partner = -1
        self.stabPart = None
        self.numAgents = numAgents
        self.topOffer = None

    def notStabMatched(self):
        if self.partner == self.stabPart:
            return False
        return True

    def unmatchPartner(self, agentList):
        unmatchedAgents = []

        if self.type == 0:
            if self.partner is not -1:
                unmatchedAgents.append(agentList[self.numAgents + self.partner])
        else:
            if self.partner is not -1:
                unmatchedAgents.append(agentList[self.partner])

        for agent in unmatchedAgents:
            agent.mv = -1
            agent.partner = -1

    def considerOffer(self, firmId, mv):
        if self.topOffer:
            if self.topOffer[1] < mv:
                self.topOffer = (firmId, mv)
        else:
            if self.mv < mv:
                self.topOffer = (firmId, mv)

def main(start=1, end=None):
    if not end:
        end = maxN

    simPeriods = []
    for n in range(start, end+1):  # For each market size run simulations of random markets
        print(n)

        nPeriodResults = Parallel(n_jobs=2)(delayed(simulation)(n) for i in range(simNumber))
        simPeriods.append(nPeriodResults)

    return simPeriods

if __name__ == '__main__':
    periods = main()
    toc = time.perf_counter()
    print(f"time required: {toc - tic:0.4f} seconds")
    graphAvg95(periods)
