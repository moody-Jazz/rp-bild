import subprocess
import os
import sys
import shutil
import stat
from sys import argv

platform_name   = ''
primary_lang    = ''
allowed_langs   = ['c', 'cpp']
compiler_list   = []
compiler_name   = ''
linker_flags    = ['-lraylib', '-Llib']
compiler_flags  = ['-Wall', '-Og', '-std={}17', '-Iinclude']

root_dir            = os.getcwd()
raylib_dir          = "raylib"
build_raylib_cmd    = ['make', 'PLATFORM=PLATFORM_DESKTOP']
static_raylib_name  = "libraylib.a"
raylib_header_name  = "raylib.h"
example_dir         = os.path.join(raylib_dir, 'examples', 'core')
example_name        = 'core_basic_window.c'

# =================================================================================================
#                          Helper functions 
# =================================================================================================

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

# =================================================================================================
#                          get the values related to system 
# =================================================================================================

def config_env():
    global primary_lang, compiler_name, compiler_list, extension
    global platform_name, raylib_dir, linker_flags, compiler_flags

    # Figure out the primary language
    src_list = []
    try:
        src_list = os.listdir(os.path.join(root_dir, 'src'))
    except:
        print("couldn't find the src directory, initialize the project first")
        exit(1)

    main_candidates = [src for src in src_list if src.startswith('main.')]
    if not main_candidates:
        print("Error: couldn't find main.c or main.cpp in src/")
        exit(1)
    src = main_candidates[0]
    primary_lang = src.split('.')[1]

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


# =================================================================================================
#                    clone and build raylib and create the project structure
# =================================================================================================

def init_project():
    global primary_lang, compiler_name, compiler_flags, linker_flags, root_dir
    dir_list = os.listdir()

    # find out whether the project will be written in c or c++ 
    print("which will be your primary language C or CPP?")
    while primary_lang not in allowed_langs:
        primary_lang = input('> ').lower()
        if primary_lang not in allowed_langs:
            print('unexpected input either enter C or CPP')

    clone_repo = ['git', 'clone', "https://github.com/raysan5/raylib"]
    subprocess.run(clone_repo)
    raylib_src = os.path.join(raylib_dir, 'src')

    os.chdir(raylib_src)
    print('building static library libraylib...........')
    print(build_raylib_cmd)
    subprocess.run(' '.join(build_raylib_cmd))

    staticlib_src       = os.path.join(raylib_src, static_raylib_name)
    staticlib_dest      = 'lib'
    raylibheader_src    = os.path.join(raylib_src, raylib_header_name)
    raylibheader_dest   = 'include'
    example_src         = os.path.join(example_dir, example_name)
    example_dest        = os.path.join('src', 'main.{}'.format(primary_lang))
    
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
    print(f'{compiler_name} found on your system')

    cmd = generate_execution_cmd(
        compiler_name, compiler_flags, 
        ['-o', 'main', os.path.join('src', f'main.{primary_lang}')], linker_flags
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

# =================================================================================================
#            compile/recompile all the files which are not-compiled/modified
# =================================================================================================

def compile():
    config_env()
    global root_dir, compiler_name, compiler_flags, linker_flags
    root_dir_list = os.listdir()

    if 'obj' not in root_dir_list:
        print('obj direcotry not found')
        print('creating obj.........')
        os.makedirs(name='obj')
    
    src_dir_list = os.listdir(f'{root_dir}/src') 
    src_list, obj_list = [], []
   
    for src in src_dir_list:
        obj = src.split('.')[0] + '.o'
        obj_list.append(os.path.join('obj', obj))
        # add files for recompilation if either its .o doesn't exist or is older than the file itself
        if (
            not os.path.exists(os.path.join('obj', obj)) or 
            os.path.getmtime(os.path.join('src', src)) > os.path.getmtime(os.path.join('obj', obj))
        ):
            src_list.append(os.path.join('src', src))
        
            other_flags = ['-c']
            other_flags.append(os.path.join('src', src))
            other_flags.append('-o')
            other_flags.append(os.path.join('obj', obj))
            cmd = generate_execution_cmd(compiler_name, compiler_flags, other_flags, [])
     
            try:
                print('compiling with the command', ' '.join(cmd), sep='\n')
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                print("GCC compilation failed!")
        
    if len(src_list) < 1:
        print('Nothing to recompile, try compiling after modification')
        exit(1)

    # link and generate the executable file
    obj_list.extend(['-o', 'main'])
    cmd = generate_execution_cmd(compiler_name, compiler_flags, obj_list, linker_flags)

    try:
        print('Trying to create executable with command', ' '.join(cmd), sep='\n')
        subprocess.run(cmd, check=True)
        print('compilation succesful')
    except subprocess.CalledProcessError as e:
        print('Failed to create executable')

# =================================================================================================
#                        Dlete all the obj files and directory 
# =================================================================================================

def clean():
    print('this action will delete all the obj file and obj directory')
    choice = input('y/n: ')
    if choice == 'y':
        print('deleting obj directory........')
        rmtree('obj')
    
# =================================================================================================
#               main function to take cl-arguments and call appropriate functions
# =================================================================================================

def main():
    args = argv[1:]
    
    if len(args) <= 0 or args[0] == 'compile':
        compile()
    elif len(args) > 0 and args[0] == 'init':
        init_project()
    elif len(args) > 0 and args[0] == 'clean':
        clean()

if __name__ == "__main__":
    main()
    