from __future__ import print_function
from asyncio.subprocess import PIPE #for python 2.7

import os
import sys
import shutil
import argparse
import subprocess
from threading import Timer

import fuzzUtils as utils


def execute_aflpp (aflpp_path, executable_name, local_seeddir_path, is_file_mode) :

    afl_fuzz_path = aflpp_path + "/afl-fuzz"
    cmd = [afl_fuzz_path, "-i", local_seeddir_path, "-o", "local_out", executable_name]
    if is_file_mode == True:
        cmd.append("@@")

    env_var = os.environ.copy()
    env_var["AFL_SKIP_CPUFREQ"] = "1"
    env_var["AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES"] = "1"
    
    if (sys.version_info < (3,3)):
        proc = subprocess.Popen(cmd, env=env_var)
        timer = Timer(5, proc.kill) # TODO. set timeout value (sec)
        try:
            timer.start()
            proc.wait()
        finally:
            timer.cancel()
    else:
        proc = subprocess.Popen(cmd, env=env_var, stderr=PIPE, stdout=PIPE)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    

    return proc.returncode


def main () :

    # Get arguments
    parser = argparse.ArgumentParser()  
    parser.add_argument("-w", help="path of working dir", required=True)
    parser.add_argument("-a", help="path of afl++", required=True) # TODO build afl++ in python script
    parser.add_argument("-x", help="name of executable", required=True)
    parser.add_argument("-o", help="path of origin seed dir", required=True)
    parser.add_argument("-p", help="path of per function seed dir", required=True)
    
    args = parser.parse_args()

    wkdir_path = os.path.realpath(args.w)
    aflpp_path = os.path.realpath(args.a)
    executable_name = args.x  # executable must be under the workdir...
    origin_seed_dir = os.path.realpath(args.o)
    per_func_seed_dir = os.path.realpath(args.p)
    
    os.chdir(wkdir_path)
    
    # Build fuzzers
    build_cmd = "CC=" + aflpp_path + "/afl-cc make"
    os.system(build_cmd)

    # Get a new seed directory
    changed_funcs = utils.get_changed_func_names(wkdir_path)
    local_seeddir_path = utils.get_seeds_for_local_mode(origin_seed_dir, per_func_seed_dir, changed_funcs)
    
    # Run afl++ using process
    return_code = execute_aflpp(aflpp_path, executable_name, local_seeddir_path, False) # TODO get is_file as an argument
    print("RETURN CODE = ", return_code, type(return_code))
    '''
    TODO use a return code?
    return code
    1 => afl-fuzz fail
    -N => timeout(?)

    TODO how to detect crash?
    '''

    # Remove new seed directory and output directory
    shutil.rmtree(local_seeddir_path)
    shutil.rmtree("local_out")



if __name__ == "__main__":
    main()