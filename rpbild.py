import subprocess
import os
import sys
import shutil
import stat

platform_name   = ''
primary_lang    = ''
allowed_langs   = ['c', 'cpp']
compiler_list   = []
compiler_name   = ''
linker_flags    = ['-lraylib', '-Llib']
compiler_flags  = ['-Wall', '-Og', '-std={}17', '-Iinclude']

root_dir            = os.getcwd()
raylib_dir          = "/raylib/"
build_raylib_cmd    = ['make', 'PLATFORM=PLATFORM_DESKTOP']
static_raylib_name  = "libraylib.a"
raylib_header_name  = "raylib.h"
example_dir         = "examples/core/"
example_name        = "core_basic_window.c"

def rmtree(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            filename = os.path.join(root, name)
            os.chmod(filename, stat.S_IWUSR)
            os.remove(filename)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(top)  


def generate_execution_cmd(compiler_name, compiler_flags, other_flags, linker_flags):
    res = [compiler_name]
    res.extend(compiler_flags)
    res.extend(other_flags)
    res.extend(linker_flags)
    return res


def config_env():
    global primary_lang, compiler_name, compiler_list, extension
    global platform_name, raylib_dir, linker_flags, compiler_flags

    # Figure out the primary language
    src_list = os.listdir(f'{root_dir}/src')
    for src in src_list:
        if 'main' in src:
            primary_lang = src.split('.')[1]
        else:
            print("Error: couldn't find main")
            exit(1)

    # Figure out the operating system
    if sys.platform == 'darwin':
        linker_flags.extend(['-framework OpenGL', '-framework Cocoa', '-framework CoreAudio'])
        linker_flags.extend(['-framework IOKit', '-framework CoreVideo', '-framework AVFoundation'])
    elif 'win' in sys.platform:
        linker_flags.extend(['-lgdi32', '-lwinmm'])
    elif 'linux' in sys.platform:    
        linker_flags.extend(['-lGL', '-lm', '-lpthread', '-ldl', '-lrt'])
    else:
        print('this script is only to meant for linux/windows/macos')
        exit(1)

    # Find out if system has make
    try:
        subprocess.run(['make', '--version'], check=True, stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        print('no make found')
        exit(1)
    except subprocess.CalledProcessError:
        print('unexpected error occured while running make --version')
        exit(1)

    if primary_lang == 'c':
        compiler_list = ['gcc', 'clang']
        compiler_flags[2] = compiler_flags[2].format('c')
    else :
        compiler_list = ['g++', 'clang++']
        compiler_flags[2] = compiler_flags[2].format('c++')

    # Figure out which compiler the system have
    for compiler in compiler_list:
        try:
            subprocess.run([compiler, '--version'], check=True, stdout=subprocess.DEVNULL)
            compiler_name = compiler
            break
        except FileNotFoundError:
            continue
        except subprocess.CalledProcessError:
            print(f'error occuring while running {compiler} --version')
            continue

    if compiler_name == '':
        print("no c/c++ compiler found, download one of the below", compiler_list)
        exit(1)


def init_project():
    global primary_lang, compiler_name, compiler_flags, linker_flags, root_dir
    dir_list = os.listdir()

    # find out whether the project will be written in c or c++ 
    print("which will be your primary language C or CPP?")
    while primary_lang not in allowed_langs:
        primary_lang = input('> ').lower()
        if primary_lang not in allowed_langs:
            print('unexpected input either enter C or CPP')
    print(f'{compiler_name} found on your system')

    clone_repo = ['git', 'clone', "https://github.com/raysan5/raylib"]
    subprocess.run(clone_repo)

    os.chdir(os.getcwd() + raylib_dir + 'src/')
    print('building static library libraylib...........')
    subprocess.run(build_raylib_cmd)
    raylib_src = raylib_dir + 'src/'

    staticlib_src       = raylib_src + static_raylib_name
    staticlib_dest      = "lib/"
    raylibheader_src    = raylib_src + raylib_header_name
    raylibheader_dest   = "include/"
    example_src         = raylib_dir + example_dir + example_name
    example_dest        = 'src/main.{}'.format(primary_lang)
    
    os.chdir(root_dir)
    print('copying the header file and static library................')
    if 'include' not in dir_list:
        os.makedirs(name = 'include')
    if 'src' not in dir_list:
        os.makedirs(name = 'src')
    if 'lib' not in dir_list:
        os.makedirs(name = 'lib')

    shutil.copy(staticlib_src, staticlib_dest)
    shutil.copy(raylibheader_src, raylibheader_dest)
    shutil.copy(example_src, example_dest)
    
    print('Deleting raylib...............')
    rmtree('raylib')

    config_env()

    cmd = generate_execution_cmd(
        compiler_name, compiler_flags, ['-o', 'main', 'src/main.{}'.format(primary_lang)], linker_flags
        )

    print('Compiling the src', ' '.join(cmd), sep='\n')

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print(f'main.{primary_lang} not found')
    except subprocess.CalledProcessError:
        print(f'error occured while running main.{primary_lang}')

    print(f'Running test main.{primary_lang}')
    try:
        subprocess.run(['main'], check=True)
    except:
        print("couldn't run the executable")
