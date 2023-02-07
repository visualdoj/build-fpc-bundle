import sys
import argparse
import json

def generate_matrix(host, cross, matrix_filename):
    with open(matrix_filename, 'r') as f:
        contents = f.read()

    matrix = json.loads(contents)

    include_list = matrix.get('include',[])
    if include_list:
        if cross == "all":
            pass
        elif cross == '':
            matrix['include'] = []
        else:
            configs = cross.split(',')
            for include in include_list[:]:
                if  include.get('cpu','') + '-' + include.get('os','') not in configs \
                and include.get('cpu','') not in configs \
                and include.get('os','') not in configs:
                    include_list.remove(include)

    print(json.dumps(matrix))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--cross")
    parser.add_argument("--matrix")
    
    args = parser.parse_args()
    generate_matrix(args.host, args.cross, args.matrix)
