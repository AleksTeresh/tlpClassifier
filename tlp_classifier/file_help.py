import os, json
from .problem_set import Problem_set, problem_set_name

def add_degree_suffix(name, white_degree, black_degree):
    suffix = "_" + str(white_degree) + "_" + str(black_degree)
    return name + suffix

def data_name(white_degree,black_degree):
    return add_degree_suffix("data/problemSet",white_degree,black_degree)

def import_data_set(white_degree, black_degree,classified):
    problems = (set(), dict(), dict())
    min_degree = min([white_degree,black_degree])
    max_degree = max([white_degree,black_degree]) 

    curr_file_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(curr_file_path)
    local_data_file_path = data_name(min_degree,max_degree) + '_' + problem_set_name[classified]
    full_path = os.path.join(dir_path, local_data_file_path)

    with open(full_path, 'rb') as problem_file:
        problems = json.load(problem_file)
    return problems

# Store the given problem set in the file with the given name
def store(white_degree,black_degree,problems,classified):
    with open(data_name(white_degree,black_degree) + '_' + problem_set_name[classified], 'wb') as problem_file:
        json.dump(problems, problem_file, ensure_ascii=False, indent=2)

# Store a given set of problems in a file
def problems_to_file(name, that):
    f= open(name,"w+")
    for elem in that:
        elem.write_in_file(f)
    f.close()
