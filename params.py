# problem size
NUM_NODES = 10
NUM_AGENTS = 10
NUM_ELITE = 5
POPSIZE = 10

# observability params
GLOBAL_DONES = False # set to true: all agents update their done_tasks list from global information
SEE_DONES = False # set to true: an agent will not select a goal if it is already done, must have GLOBAL_DONES=True
GLOBAL_INTENT = False # set to true: an agent will not select a goal if another is already moving towards it

# obstacles
EDGE_MULT = 2 # randomly multiply edge weight by up to this amount

# agent params
EPSILON = 0 # epsilon-greedy
GAMMA = 1 # weight decay
WEIGHT_ALPHA = 0 # distance score weight
WEIGHT_BETA = 1 # node score weight
START_WEIGHT = 0 # initial nodeweight for returning to start. Set to 1 to make it random

# GA hyperparams
MAX_ITER = 20
OPERATOR_THRESHOLD = 0.7 # crossover for less than threshold, mutation for >=
MUTATION_RATE = 0.2 # note this and operator threshold DO NOT NEED TO ADD TO 1
METRIC = 'total' # total or minmax
INCOMPLETE_PENALTY = -1e10