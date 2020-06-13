#!/usr/bin/python3
import sys, getopt
from problem import Problem,Constraints,alpha_to_problem
from complexity import Complexity,complexity_name
from tqdm import tqdm
import pickle
from time import time
import tools
from algorithms import constraint_reduction,redundancy_algorithm, greedy4Coloring,cover_map_1, round_eliminator
from file_help import import_data_set, problems_to_file,add_degree_suffix,store
from bitarray import bitarray, util
from two_labels_classifier import get_complexity_of,constraints_to_bitvector_tuple
from input import ITERATED_LOGARITHMIC, LOGARITHMIC_UPPER_BOUND, LOGARITHMIC_TIGHT, LOGARITHMIC_LOWER_BOUND
from problem_set import Problem_set

LABELS = frozenset([0,1,2])

def compute_relaxations(problems, that, complexity,relaxations):
    for problem in that:
        for relax in relaxations[problem]:
            relax.set_upper_bound(complexity)
            if complexity == Complexity.Constant:
                relax.constant_upper_bound = min(relax.constant_upper_bound,problem.constant_upper_bound)

def compute_restrictions(problems, that, complexity,restrictions):
    for problem in that:
        for restr in restrictions[problem]:
            restr.set_lower_bound(complexity)

def propagate(problems,restrictions,relaxations):
    print("Propagating the lower and upper bounds")
    for complexity in tqdm(Complexity):
        if complexity != Complexity.Unclassified:
            if complexity != Complexity.Constant:
                LBSubset = {x for x in problems if x.lower_bound == complexity}
                compute_restrictions(problems, LBSubset,complexity,restrictions)
            UBSubset = {x for x in problems if x.upper_bound == complexity}
            compute_relaxations(problems, UBSubset,complexity,relaxations)
    
# Return the subset of unsolvable problems
def unsolvable_criteria(problem):
    if(len(problem.white_constraint)==0 or len(problem.black_constraint)==0):
        problem.set_complexity(Complexity.Unsolvable)
    else:
        problem.set_upper_bound(Complexity.Global)

def two_labels_criteria(problem):
    # Problems that are 2 labelling problems
    if len(problem.alphabet()) < 3 and len(problem.white_constraint) > 0 and len(problem.black_constraint) > 0:
        problem.set_complexity(get_complexity_of(*constraints_to_bitvector_tuple(problem.white_constraint,problem.black_constraint,problem.alphabet(),problem.white_degree,problem.black_degree)))
        return
    # Redundancy of a label
    if problem.alphabet_size() == 3:
        tmp = redundancy_algorithm(problem.white_constraint,problem.black_constraint)
        if tmp != None:
            problem.set_complexity(get_complexity_of(*constraints_to_bitvector_tuple(tmp[0],tmp[1],tmp[2],problem.white_degree,problem.black_degree)))

#def round_eliminator_lb_criteria(problem):
#    lower_bound = round_eliminator_lb(problem, 15, 5)

def greedy_4_coloring_test(problem):
    if greedy4Coloring(problem):
        problem.set_upper_bound(Complexity.Iterated_Logarithmic)

def cover_map_test(problem):
    if cover_map_1(problem.white_constraint,problem.black_constraint):
        problem.set_lower_bound(Complexity.Iterated_Logarithmic)
    
def classify(problems,relaxations,restrictions):
    print("Starting classification (" + str(len(problems)) + " problems)...")
    
    def unclassified_problems(problems):
        return {problem for problem in problems if problem.get_complexity() == Complexity.Unclassified}
    def solvable_problems(problems):
        return {problem for problem in problems if problem.get_complexity() != Complexity.Unsolvable}

    def partially_classify(function):
        for problem in tqdm(unclassified_problems(problems)):
            function(problem)

    def partially_classify_RE():
        iter_label = [(20,3),(10,4),(3,5)]
        for i in range(len(iter_label)):
            n = 0
            print("Running the round eliminator with the following parameters : iterations = " + str(iter_label[i][0]) + ", labels = " + str(iter_label[i][1]))
            for problem in tqdm({x for x in problems if x.lower_bound == Complexity.Constant and x.constant_upper_bound > 200}):
                ub = round_eliminator(problem,'autoub', iter_label[i][0], iter_label[i][1])
                if ub >= 0:
                    problem.set_complexity(Complexity.Constant)
                    problem.constant_upper_bound = min(problem.constant_upper_bound,ub)
                    n+=1
                    if i >= 5:
                        print(problem)
                        print("with a ub of : ",ub)
            print(n," problems classified as constant")
            propagate(problems,restrictions,relaxations)
    
    def partially_classify_debug(function):
        for problem in tqdm(solvable_problems(problems)):
            function(problem)

    print("Checking the solvability of the problems")
    partially_classify(unsolvable_criteria)
    print("Running the binary labelling classifier on binary problems and redundant ternary problems")
    partially_classify(two_labels_criteria)
    print("Running algorithm for iterated logarithmic lower bounds using cover map")
    partially_classify(cover_map_test)
    print("Running the algorithm for iterated logarithmic upper bounds using greedy 4 coloring")
    partially_classify(greedy_4_coloring_test)
    #partially_classify(round_eliminator_lb_criteria)
    
    for problem in problems:
        if any([problem == alpha_to_problem(elem) for elem in LOGARITHMIC_UPPER_BOUND]):
            problem.set_upper_bound(Complexity.Logarithmic)
        if any([problem == alpha_to_problem(elem) for elem in LOGARITHMIC_TIGHT]):
            problem.set_complexity(Complexity.Logarithmic)
        if any([problem == alpha_to_problem(elem) for elem in LOGARITHMIC_LOWER_BOUND]):
            problem.set_lower_bound(Complexity.Logarithmic)
        if any([problem == alpha_to_problem(elem) for elem in ITERATED_LOGARITHMIC]):
            problem.set_complexity(Complexity.Iterated_Logarithmic)
    
    propagate(problems,restrictions,relaxations)
    partially_classify_RE()
    propagate(problems,restrictions,relaxations)

def main(argv):
    white_degree = -1
    black_degree = -1
    s = False
    try:
        opts, args = getopt.getopt(argv,"hw:b:s",["wdegree=","bdegree=",'store'])
    except getopt.GetoptError:
        print ('classifier.py -w <whitedegree> -b <blackdegree>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('classifier.py -w <whitedegree> -b <blackdegree>')
            print('-s to store the differents ')
            sys.exit()
        elif opt in ("-w", "--wdegree"):
            try :
                white_degree = int(arg)
            except ValueError:
                print("The white degree is not an int")
                sys.exit(1)
        elif opt in ("-b", "--bdegree"):
            try :
                black_degree = int(arg)
            except ValueError:
                print("The black degree is not an int")
                sys.exit(1)
        elif opt in ("-s","--store"):
            s = True
            print("aaa")

    if (white_degree <= 1 or black_degree <= 1):
        print("A degree must be superior or equal to 2")
        sys.exit(1)
        
    min_degree = min([white_degree,black_degree])
    max_degree = max([white_degree,black_degree])

    problems,relaxations,restrictions = import_data_set(min_degree,max_degree,Problem_set.Unclassified)
    classify(problems,relaxations,restrictions)

    #store(min_degree,max_degree,(problems,relaxations,restrictions),Problem_set.Classified)

    for complexity in Complexity:
        classifiedSubset = {x for x in problems if x.get_complexity() == complexity}
        print(complexity_name.get(complexity)+ " problems :",len(classifiedSubset))
        if s:
            problems_to_file("output/" + str(min_degree) + "_" + str(max_degree) + "/" + complexity_name.get(complexity) + ".txt", classifiedSubset)


if __name__ == "__main__":
   main(sys.argv[1:])