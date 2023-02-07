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
            if cross == 'common':
                configs = [
                    "Linux->i386-win32",
                    "Linux->x86_64-win64",
                    "Windows->x86_64-linux",
                    "Windows->x86_64-win64",
                ]
            elif cross == 'supported':
                configs = [
                    "Linux->i386-win32",
                    "Linux->i386-linux",
                    "Linux->i386-wince",
                    "Linux->i386-embedded",
                    "Linux->i386-nativent",
                    "Linux->x86_64-win64",
                    "Linux->x86_64-embedded",
                    "Linux->arm-wince",
                    "Linux->i8086-embedded",
                    "Windows->i386-linux",
                    "Windows->i386-go32v2",
                    "Windows->i386-freebsd",
                    "Windows->i386-wince",
                    "Windows->i386-embedded",
                    "Windows->i386-nativent",
                    "Windows->powerpc-linux",
                    "Windows->powerpc-netbsd",
                    "Windows->sparc-linux",
                    "Windows->x86_64-linux",
                    "Windows->x86_64-freebsd",
                    "Windows->x86_64-win64",
                    "Windows->x86_64-embedded",
                    "Windows->arm-linux",
                    "Windows->arm-wince",
                    "Windows->powerpc64-linux",
                    "Windows->avr-embedded",
                    "Windows->mips-linux",
                    "Windows->mipsel-linux",
                    "Windows->i8086-embedded",
                    "Windows->aarch64-linux",
                    "Windows->sparc64-linux",
                ]
            else:
                configs = cross.split(',')
            for include in include_list[:]:
                if  host + '->' + include.get('cpu','') + '-' + include.get('os','') not in configs \
                and include.get('cpu','') + '-' + include.get('os','') not in configs \
                and include.get('cpu','') not in configs \
                and include.get('os','') not in configs:
                    include_list.remove(include)

    print(json.dumps(matrix), end='')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",  default="")
    parser.add_argument("--cross", default="")
    parser.add_argument("--matrix")
    
    args = parser.parse_args()
    generate_matrix(args.host, args.cross, args.matrix)
