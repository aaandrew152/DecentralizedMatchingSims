import random
import numpy as np
from itertools import repeat
from Graphing import graphAvg95
from joblib import Parallel, delayed
import time


random.seed()
maxN = 10  # Maximal market size
simNumber = 1  # Number of simulations per market size
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
    assert worker.type == 0 and firm.type == 1, "worker should be entered first"
    worker.unmatchPartner(agentList)
    firm.unmatchPartner(agentList)
    worker.mv, firm.mv = repeat(value, 2)
    worker.partner = firm.id
    firm.partner = worker.id

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
        changed = onePeriod(potential, agentList)
        endPeriod += changed

    return endPeriod

def onePeriod(potential, agentList):
    chosenAgent = random.choice(agentList)
    changed = bestResponse(potential, agentList, chosenAgent)  # Can be swapped out for better response dynamics
    return changed

def bestResponse(potential, agentList, agent):  # Finds the best match that will accept
    BPvalue = agent.mv  # Current best BP value
    BPid = agent.partner

    if agent.type == 0:
        for firmNum, value in enumerate(potential[agent.id]):  # Find better possible matches
            if value > BPvalue and value > agentList[agent.numAgents + firmNum].mv:  # We are a better bp
                BPvalue = value
                BPid = firmNum
        if BPid != agent.partner:
            newPartner = agentList[BPid + agent.numAgents]  # Randomly choose one blocking pair involving this player
            match(agent, newPartner, agentList, potential[agent.id][newPartner.id])
            return 1
    else:
        for workerNum, workerVals in enumerate(potential):
            if workerVals[agent.id] > BPvalue and workerVals[agent.id] > agentList[workerNum].mv:
                BPvalue = workerVals[agent.id]
                BPid = workerNum
        if BPid != agent.partner:
            newPartner = agentList[BPid]  # Randomly choose one blocking pair involving this player
            match(newPartner, agent, agentList, potential[newPartner.id][agent.id])
            return 1
    return 0

def betterResponse(potential, agentList, agent):  # Uniformly selects any (better) match that will accept
    possBPs = []  # Set of possible blocking partners

    if agent.type == 0:
        for colNum, value in enumerate(potential[agent.id]):  # Find better possible matches
            if value > agent.mv and value > agentList[agent.numAgents + colNum].mv:  # We are a bp
                possBPs.append(colNum)
        if possBPs:
            newPartner = agentList[random.choice(possBPs) + agent.numAgents]  # Randomly choose one blocking pair involving this player
            match(agent, newPartner, agentList, potential[agent.id][newPartner.id])
            return 1
    else:
        for rowNum, workerVals in enumerate(potential):
            if workerVals[agent.id] > agent.mv and workerVals[agent.id] > agentList[rowNum].mv:
                possBPs.append(rowNum)
        if possBPs:
            newPartner = agentList[random.choice(possBPs)]  # Randomly choose one blocking pair involving this player
            match(newPartner, agent, agentList, potential[newPartner.id][agent.id])
            return 1

    return 0


class Agent:
    numAgents = None

    def __init__(self, id, type, numAgents):
        self.id = id
        self.type = type  # 0 if row agent, 1 if col agent
        self.mv = -1
        self.partner = -1
        self.stabPart = None
        self.numAgents = numAgents

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
    periods = main(start=3)
    toc = time.perf_counter()
    print(f"time required: {toc - tic:0.4f} seconds")
    graphAvg95(periods)
