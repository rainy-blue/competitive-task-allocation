import networkx as nx
import numpy as np
import copy
from random import choice, random, sample, randrange, randint
import sys

from agent import Agent, euclidean
from gameloop import GameLoop
import matplotlib.pyplot as plt
import params

class Allocator:
    def __init__(self, graph=None, popsize=params.POPSIZE, num_agents=params.NUM_AGENTS, num_elite=params.NUM_ELITE, metric=params.METRIC):
        self.graph = graph
        self.popsize = popsize
        self.num_agents = num_agents
        self.num_elite = num_elite
        self.metric = metric
        # initialize the gameloop
        self.gameloops = []
        for i in range(0, self.popsize):
            gameloop = GameLoop(graph=self.graph, num_agents=self.num_agents, id=i)
            self.gameloops.append(gameloop)

        # initialie the GA class

    def allocate(self):
        # randomly initialize nodeweights
        nodeweights_pop = self.init_nodeweights()
        scores = np.zeros(self.popsize)

        # in a loop until convergence:
        for iter in range(0, params.MAX_ITER):
            print('allocator iteration {}'.format(iter))
            # run the game loop n number of times to get n matrices of nodeweights
            for i, gameloop in enumerate(self.gameloops):
                gameloop.set_nodeweights(nodeweights_pop[gameloop.id])
                gameloop.reset()
                gameloop.loop()

                # calculate score based on metric
                if (self.metric == 'total'):
                    scores[i] = gameloop.total_cost()
                elif (self.metric == 'minmax'):
                    scores[i] = gameloop.minmax()
                print(gameloop.total_cost())
                print(gameloop.minmax())

                sys.stdout.flush()

            # run GA to get new nodeweights


            print(list(nodeweights_pop.values())[0].shape)
            #print(list(nodeweights_pop.values())[0]) # 1 game 2 agents 5 weight nodes each agent
            print(scores.shape)

            elites  = self.selection_pair(nodeweights_pop,scores) # elites survive
            new_population = [elites]
            while len(new_population) <= params.POPSIZE:
                operator = 0.9#random()
                if operator < params.OPERATOR_THRESHOLD:
                    parent_a, parent_b = sample(elites, k=2)     # only elites chosen as parents, change later
                    #parents = np.array([parent_a, parent_b])
                    # print('parentA', parent_a)
                    # print('parentB', parent_b)
                    child = self.crossover(parent_a, parent_b)
                    # print(child)
                    new_population.append(child)
                else:
                    parent = choice(elites)
                    # print(parent.shape)
                    child = self.mutation(parent)
                    new_population.append(child)
                    # print(parent)
                    # print(child)
            print(np.array(new_population))
            return new_population
            '''
            sort scores and the highest two scores (of games) are kept, others discarded
            until rest of discarded games (len scores - 2) are filled, crossover the two games until only 1 empty game left
            for last game, mutation
            '''
            # inputs: dictionary of 2d np array of weights, 1d np array of scores

    def init_nodeweights(self):
        nodeweights_pop = {}
        interval = int(len(list(self.graph.nodes))/self.num_agents)
        for gameloop in self.gameloops:
            nodeweights_pop[gameloop.id] = np.random.rand(self.num_agents, len(list(self.graph.nodes)))
            if (params.START_WEIGHT != 1):
                nodeweights_pop[gameloop.id][:,gameloop.start] = params.START_WEIGHT
        return nodeweights_pop

    # select agents that survive to next generation based on fitness, number based on num_elite parameter
    # explore: roulette, fittest half, random
    # Returns: list of surviving agents
    def selection_pair(self, pop_weights, scores):
        ranked_scores = [sorted(scores).index(x) for x in scores]
        elite_agents = []
        for _ in range(self.num_elite):
            elite_idx = ranked_scores.index(max(ranked_scores))
            ranked_scores[elite_idx] = -1
            elite_agents.append(pop_weights[elite_idx])

        return elite_agents

    # def single_point_crossover(self, node_a, node_b):
    #     length = len(node_a)
    #     if length < 2:
    #         return node_a, node_b

    #     p = randint(1, length - 1)
    #     return node_a[0:p] + node_b[p:], node_b[0:p] + node_a[p:]
    def crossover(self, parentA, parentB):
        sz = parentA.shape
        # helper arrays for coordinate system
        x = np.ones(sz)
        print(x.shape)
        print(sz[0])
        x[:,:] = np.arange(sz[0])

        y = np.ones(sz)
        y[:,:] = sz[1]-np.arange(sz[1]).reshape(sz[1],1) # 100- to invert y-axis

        # linear function
        def linfunc(x, m, n):
            return x*m + n

        #ab_mean = (parentA+parentB)/2
        test_line = linfunc(x, -4, 150) #  y = {2nd argument}x + {3rd argument}
        output = np.zeros_like(parentA)
        output[y>test_line] = parentA[y>test_line] # assign above line to a
        output[y<test_line] = parentB[y<test_line] # assign below line to b
        output[y==test_line] = parentA[y==test_line] # assign coords on line to a
        #output[y==test_line] = ab_mean[y==test_line] # assign coords on line to "interpolation"
        return output


    def mutation(self, parent):
        # A function to be applied to the array
        def mutate(gene):
            temp = random()
            if temp < params.MUTATION_RATE:
                return random()
            else:
                return gene
        mute = np.vectorize(mutate)
        child = mute(parent)
        return child
