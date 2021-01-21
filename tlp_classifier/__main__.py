import sys, getopt
from .problem_set import Problem_set
from .file_help import import_data_set
from .classifier import classify

def main(argv):
    white_degree = -1
    black_degree = -1
    s = False
    try:
        opts, args = getopt.getopt(argv,"hw:b:",["wdegree=","bdegree="])
    except getopt.GetoptError:
        print ('classifier.py -w <whitedegree> -b <blackdegree>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('classifier.py -w <whitedegree> -b <blackdegree>')
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

    problems,relaxations,restrictions = import_data_set(min_degree,max_degree,Problem_set.Unclassified)
    classify(problems,relaxations,restrictions, min_degree, max_degree)

    store(min_degree,max_degree,(problems,relaxations,restrictions),Problem_set.Classified)

    json_dict = dict()
    for complexity in Complexity:
        classifiedSubset = [x.to_tuple() for x in problems if x.get_complexity() == complexity]
        print (complexity_name[complexity] + " : " + str(len(classifiedSubset)), " problems")            
        json_dict[complexity_name[complexity]] = classifiedSubset

    with open("output/" + str(min_degree) + "_" + str(max_degree) + ".json", "w") as write_file:
        json.dump(json_dict,write_file,indent=4)

if __name__ == "__main__":
   main(sys.argv[1:])
