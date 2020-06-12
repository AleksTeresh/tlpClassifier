#!/usr/bin/python3
import sys, getopt
from Tools import edge_3_labelling,powerset
from Problem import Problem
from FileHelp import data_name, store
from joblib import Parallel, delayed
from problem_set import Problem_set
import time
import multiprocessing
DEBUG = True
#DEBUG = False

def store_RE_problem(problem,white_degree,black_degree):
        def mapping_function(configuration):
            return "A "*configuration[2]+"B "*configuration[1]+"C "*configuration[0]+"\n"
        w = "".join(map(mapping_function,problem.white_constraint))
        b = "".join(map(mapping_function,problem.black_constraint))
        
        def write_in_file_RE(name, active, passive):
            f= open(name,"w+")
            f.write(active + "\n" + passive + "\n")
            f.close()
        write_in_file_RE("data/problems_RE/" + str(white_degree) + "_" + str(black_degree) + "/" + str(hash(problem)) + "_w.txt",w,b)
        write_in_file_RE("data/problems_RE/" + str(white_degree) + "_" + str(black_degree) + "/" + str(hash(problem)) + "_b.txt",b,w)
        
# Return the set of all characteristics problems with the given degrees
def generate(white_degree, black_degree):
    white_configurations, black_configurations = edge_3_labelling(white_degree),edge_3_labelling(black_degree)
    white_constraints, black_constraints = powerset(white_configurations),powerset(black_configurations)
    problems_tuple = set([(frozenset(a),frozenset(b)) for a in white_constraints for b in black_constraints])
    problems = set([Problem(a,b,white_degree,black_degree) for (a,b) in problems_tuple if Problem(a,b,white_degree,black_degree).is_characteristic_problem()])
    number_of_problems = len(problems)
    problems_list = list(problems)
    if DEBUG:
        print("Number of White Configurations :",len(white_configurations))
        print("Number of Black Configurations :",len(black_configurations))
        print("Number of White Constraints :",len(white_constraints))
        print("Number of Black Constraints :",len(black_constraints))
    relaxations_dict, restrictions_dict = dict(),dict()

    #print("Storing the problems in the RE format ...")
    #for elem in tqdm(problems):
    #    store_RE_problem(elem)

    print("Computing relaxations and restrictions ...")
    #for elem in tqdm(problems):

    def processInput(elem):
        relaxations,restrictions = set(),set()
        equivalent_set = elem.equivalent_problems_instance()
        for other in problems:
            for x in equivalent_set:
                if elem != other :
                    if x.is_restriction(other):
                        relaxations.add(other)
                    if x.is_relaxation(other):
                        restrictions.add(other)
        return (relaxations,restrictions)
    


    t0= time.time()
    num_cores = multiprocessing.cpu_count()
    #values = Parallel(n_jobs=num_cores)(delayed(processInput)(problems_list[i]) for i in tqdm(range(len(problems_list))))
    values = [processInput(elem) for elem in problems_list]
    print(time.time()-t0)
    relaxations = [x for (x,y) in values]
    restrictions = [y for (x,y) in values]

    relaxations_dict = dict(zip(problems_list, relaxations))
    relaxations_dict = dict(zip(problems_list, restrictions))

    t0= time.time()
    #for elem in problems:
    #    processInput(elem)
    print(time.time()-t0)
    return (set(problems),relaxations_dict,restrictions_dict)

def main(argv):
    white_degree = -1
    black_degree = -1
    try:
        opts, args = getopt.getopt(argv,"hw:b:",["wdegree=","bdegree="])
    except getopt.GetoptError:
        print ('generator.py -w <whitedegree> -b <blackdegree>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('generator.py -w <whitedegree> -b <blackdegree>')
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

    if (white_degree <= 1 or black_degree <= 1):
        print("A degree must be superior or equal to 2")
        sys.exit(1)
        
    min_degree = min([white_degree,black_degree])
    max_degree = max([white_degree,black_degree])
    p = generate(min_degree,max_degree)
    store(min_degree,max_degree,p,Problem_set.Unclassified)

if __name__ == "__main__":
   main(sys.argv[1:])