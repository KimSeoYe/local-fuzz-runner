from __future__ import print_function

import os
import shutil
import argparse

import fuzzUtils as utils
import githubUtils as gh
import const

def main () :

    # Get arguments
    parser = argparse.ArgumentParser()  
    parser.add_argument("-w", help="path of working dir", required=True)
    parser.add_argument("-a", help="path of afl++", required=True) # Suppose : afl++ is already exist
    parser.add_argument("-x", help="path of executable (from working directory)", required=True)
    parser.add_argument("-o", help="path of origin seed dir", required=True)
    parser.add_argument("-p", help="path of per function seed dir", required=True)
    
    args = parser.parse_args()

    wkdir_path = os.path.realpath(args.w)
    aflpp_path = os.path.realpath(args.a)
    # executable_path = args.x  # executable must be under the workdir
    origin_seed_dir = os.path.realpath(args.o)
    per_func_seed_dir = os.path.realpath(args.p)
    
    os.chdir(wkdir_path)
    
    # Build fuzzers
    build_cmd = "CC=" + aflpp_path + "/afl-cc make"
    os.system(build_cmd)
    executable_path = os.path.realpath(args.x) # TODO check if correct

    # Get a new seed directory
    changed_funcs = utils.get_changed_func_names(wkdir_path)
    local_seeddir_path = utils.get_seeds_for_local_mode(origin_seed_dir, per_func_seed_dir, changed_funcs)
    
    # Run afl++ and monitoring crash directory
    exit_cond = utils.execute_aflpp(aflpp_path, executable_path, local_seeddir_path, False) # TODO get is_file as an argument
    
    if exit_cond == const.ExitCond.TIMEOUT :
        print("TIMEOUT")
    elif exit_cond == const.ExitCond.CRASH :
        gh.report_issue(executable_path)
    
    # Remove new seed directory and output directory
    shutil.rmtree(local_seeddir_path)
    shutil.rmtree(const.OUT_DIR)



if __name__ == "__main__":
    main()