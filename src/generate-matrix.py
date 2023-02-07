import sys
import argparse
import json

def generate_matrix(host, cross, matrix_filename):
    with open(matrix_filename, 'r') as f:
        contents = f.read()

    matrix = json.loads(contents)

    include_list = matrix.get('include',[])
    if include_list:
        if cross in ["all", "schedule"]:
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
            elif cross in ['supported', 'push']:
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
                    "macOS->i386-linux",
                    "macOS->i386-go32v2",
                    "macOS->i386-win32",
                    "macOS->i386-os2",
                    "macOS->i386-freebsd",
                    "macOS->i386-beos",
                    "macOS->i386-haiku",
                    "macOS->i386-netbsd",
                    "macOS->i386-solaris",
                    "macOS->i386-netware",
                    "macOS->i386-openbsd",
                    "macOS->i386-wdosx",
                    "macOS->i386-darwin",
                    "macOS->i386-emx",
                    "macOS->i386-watcom",
                    "macOS->i386-netwlibc",
                    "macOS->i386-wince",
                    "macOS->i386-embedded",
                    "macOS->i386-symbian",
                    "macOS->i386-nativent",
                    "macOS->i386-iphonesim",
                    "macOS->i386-android",
                    "macOS->i386-aros",
                    "macOS->m68k-linux",
                    "macOS->m68k-netbsd",
                    "macOS->m68k-amiga",
                    "macOS->m68k-atari",
                    "macOS->m68k-palmos",
                    "macOS->m68k-macosclassic",
                    "macOS->m68k-embedded",
                    "macOS->m68k-sinclairql",
                    "macOS->powerpc-linux",
                    "macOS->powerpc-netbsd",
                    "macOS->powerpc-amiga",
                    "macOS->powerpc-macosclassic",
                    "macOS->powerpc-darwin",
                    "macOS->powerpc-morphos",
                    "macOS->powerpc-embedded",
                    "macOS->powerpc-wii",
                    "macOS->powerpc-aix",
                    "macOS->sparc-linux",
                    "macOS->sparc-netbsd",
                    "macOS->sparc-solaris",
                    "macOS->sparc-embedded",
                    "macOS->x86_64-linux",
                    "macOS->x86_64-freebsd",
                    "macOS->x86_64-haiku",
                    "macOS->x86_64-netbsd",
                    "macOS->x86_64-solaris",
                    "macOS->x86_64-openbsd",
                    "macOS->x86_64-darwin",
                    "macOS->x86_64-win64",
                    "macOS->x86_64-embedded",
                    "macOS->x86_64-iphonesim",
                    "macOS->x86_64-android",
                    "macOS->x86_64-aros",
                    "macOS->x86_64-dragonfly",
                    "macOS->arm-linux",
                    "macOS->arm-netbsd",
                    "macOS->arm-palmos",
                    "macOS->arm-wince",
                    "macOS->arm-gba",
                    "macOS->arm-nds",
                    "macOS->arm-embedded",
                    "macOS->arm-symbian",
                    "macOS->arm-android",
                    "macOS->arm-aros",
                    "macOS->arm-freertos",
                    "macOS->arm-ios",
                    "macOS->powerpc64-linux",
                    "macOS->powerpc64-darwin",
                    "macOS->powerpc64-embedded",
                    "macOS->powerpc64-aix",
                    "macOS->avr-embedded",
                    "macOS->armeb-linux",
                    "macOS->armeb-embedded",
                    "macOS->mips-linux",
                    "macOS->mipsel-linux",
                    "macOS->mipsel-embedded",
                    "macOS->mipsel-android",
                    "macOS->mips64-linux",
                    "macOS->mips64el-linux",
                    "macOS->jvm-java",
                    "macOS->jvm-android",
                    "macOS->i8086-embedded",
                    "macOS->i8086-msdos",
                    "macOS->i8086-win16",
                    "macOS->aarch64-linux",
                    "macOS->aarch64-freebsd",
                    "macOS->aarch64-darwin",
                    "macOS->aarch64-win64",
                    "macOS->aarch64-embedded",
                    "macOS->aarch64-android",
                    "macOS->aarch64-ios",
                    "macOS->wasm32-embedded",
                    "macOS->wasm32-wasi",
                    "macOS->sparc64-linux",
                    "macOS->riscv32-linux",
                    "macOS->riscv32-embedded",
                    "macOS->riscv32-freertos",
                    "macOS->riscv64-linux",
                    "macOS->riscv64-embedded",
                    "macOS->xtensa-linux",
                    "macOS->xtensa-embedded",
                    "macOS->xtensa-freertos",
                    "macOS->z80-embedded",
                    "macOS->z80-zxspectrum",
                    "macOS->z80-msxdos",
                    "macOS->z80-amstradcpc",
                    "macOS->loongarch64-linux",
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
