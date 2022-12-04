import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import argparse
import glob
import os
import datetime

from gameloop import GameLoop
from agent import euclidean
from allocator import Allocator
from graph_generator import read_graph
import params

def test_run(fname, num_agents, testname):
    G = read_graph(fname)
    allocator = Allocator(graph=G, num_agents=num_agents)
    score, best_total, best_minmax, elapsed = allocator.allocate()

    # plot the first gameloop in the allocator
    plot_name = os.path.join(testname, '{}agents_{}.jpg'.format(num_agents, os.path.basename(fname)[0:-5]))
    allocator.gameloops[0].plot_graph(plot_name)
    # plot_score_name = os.path.join(testname, 'scorehist_{}agents_{}.jpg'.format(num_agents, os.path.basename(fname)[0:-5]))
    # allocator.plot_data(plot_score_name)

    return score, best_total, best_minmax, elapsed, allocator.get_min_score_hist()

def test_files(files, agents, testname):
    metrics_dict = {
        'score': {},
        'total_cost': {},
        'minmax': {},
        'elapsed': {},
    }

    best_scores_hist = {}
    for fname in files:
            for num_agents in agents:
                score, best_total, best_minmax, elapsed, min_score_hist = test_run(fname, num_agents, testname)
                print('file: {}, agents: {}, score: {}, elapsed: {}'.format(fname, num_agents, score, elapsed))

                # get the number of nodes from the filename so we can keep track of scores
                basename = os.path.basename(fname)
                ind = basename.index('nodes')
                num_nodes = int(basename[0:ind])

                # keep track of scores
                # calculate total cost and minmax as well
                config_key = (num_nodes, num_agents)
                if (config_key not in metrics_dict['score']):
                    metrics_dict['score'][config_key] = [score]
                    metrics_dict['total_cost'][config_key] = [best_total]
                    metrics_dict['minmax'][config_key] = [best_minmax]
                    metrics_dict['elapsed'][config_key] = [elapsed]
                else:
                    metrics_dict['score'][config_key].append(score)
                    metrics_dict['total_cost'][config_key].append(best_total)
                    metrics_dict['minmax'][config_key].append(best_minmax)
                    metrics_dict['elapsed'][config_key].append(elapsed)

                # keep track of convergence data
                if (config_key not in best_scores_hist):
                    best_scores_hist[config_key] = [min_score_hist]
                else:
                    best_scores_hist[config_key].append(min_score_hist)

    # calculate average scores at the end
    for key in metrics_dict:
        for config_key in metrics_dict[key]:
            metrics_dict[key][config_key] = np.mean(metrics_dict[key][config_key])

    # plot average convergence at the end
    for config_key in best_scores_hist:
        plot_name = os.path.join(testname, '{}agents_{}nodes_convergence.jpg'.format(config_key[1], config_key[0]))
        plot_score_convergence(np.array(best_scores_hist[config_key]), plot_name)

    return metrics_dict

def plot_score_convergence(best_scores, fname):
    mean_scores = np.mean(best_scores, axis=0)
    max_scores = np.max(best_scores, axis=0)
    min_scores = np.min(best_scores, axis=0)

    plt.figure()
    plt.plot(mean_scores)
    plt.fill_between(np.arange(min_scores.size), min_scores, max_scores, alpha=.3)
    plt.xlabel('iteration')
    plt.savefig(fname)
    plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--agents', type=int, nargs='+', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--all', action='store_true', help='run test on all graphs in graphs directory')
    group.add_argument('--file', type=str, help='txt file containing graphs to test')
    parser.add_argument('--testname', type=str, required=True)

    args = parser.parse_args()

    stamp = datetime.datetime.now()
    testname = args.testname + '_' + stamp.strftime('%m-%d_%H_%M_%S')
    os.mkdir(testname)

    if (args.file):
        with open(args.file, 'r') as f:
            lines = f.readlines()

        for i in range(len(lines)):
            lines[i] = lines[i].strip()
        metrics_dict = test_files(lines, args.agents, testname)
        print('metrics:', metrics_dict)

    elif (args.all):
        files = glob.glob('graphs/*.json')
        files.sort()

        metrics_dict = test_files(files, args.agents, testname)
        print('metrics:', metrics_dict)