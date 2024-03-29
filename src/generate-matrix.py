import sys
import argparse
import json

COMMON = [
    "Linux->i386-win32",
    "Linux->x86_64-win64",
    "Windows->x86_64-linux",
    "Windows->x86_64-win64",
]

REGULAR = COMMON + [
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
    "macOS->aarch64-darwin",
    "macOS->aarch64-ios",
    "macOS->arm-wince",
    "macOS->i386-embedded",
    "macOS->i386-nativent",
    "macOS->i386-win32",
    "macOS->i386-wince",
    "macOS->i8086-embedded",
    "macOS->x86_64-win64",
]

SUPPORTED = REGULAR + [
    "Windows->powerpc-netbsd", # compiles more than hour
]

PLANNED = [
    "Linux->aarch64-android",
    "Windows->aarch64-android",
]

def generate_matrix(host, cross, matrix_filename):
    with open(matrix_filename, 'r') as f:
        contents = f.read()

    matrix = json.loads(contents)

    include_list = matrix.get('include', [])
    if include_list:
        cross_list = cross.split(',')
        if "all" in cross_list or "schedule" in cross_list:
            pass
        elif cross == '':
            matrix['include'] = []
        else:
            if 'common' in cross_list:
                cross_list += COMMON
            if 'supported' in cross or 'push' in cross:
                cross_list += REGULAR
            if 'planned' in cross or 'push' in cross:
                cross_list += PLANNED
            for include in include_list[:]:
                if  host + '->' + include.get('cpu','') + '-' + include.get('os','') not in cross_list \
                and include.get('cpu','') + '-' + include.get('os','') not in cross_list \
                and include.get('cpu','') not in cross_list \
                and include.get('os','') not in cross_list:
                    include_list.remove(include)

    print(json.dumps(matrix), end='')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",  default="")
    parser.add_argument("--cross", default="")
    parser.add_argument("--matrix")
    
    args = parser.parse_args()
    generate_matrix(args.host, args.cross, args.matrix)
