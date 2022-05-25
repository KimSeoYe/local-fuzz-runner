from __future__ import print_function
from ast import Or #for python 2.7

import os
import re
from socket import timeout
import sys
import time
import random
import string
import shutil
from tkinter.tix import Tree
import psutil
import subprocess
from threading import Timer
# from multiprocessing import Process
import threading
from torch import cartesian_prod

# TODO. need to install watchdog at GitHub Action Workflow
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import const

def is_valid_name(name):
    if re.match("[a-zA-Z_][a-zA-Z0-9_]*", name) == None:
        return False
    return True

def is_not_ctl_statement(name):
    if name == "if" or name == "while" or name == "for" or name == "switch":
        return False
    return True

def trim_prefix(name):
    if name[0] == '+' or name[0] == '-':
        return name[1:]
    else:
        return name

def extract_func_name(line):
#int, __int64, void, char*, char *, struct Node, long long int, (void *)
#int func(int a, int *b, (char *) c)
    line = line.strip()
    if len(line) < 2:
        return None
# Rule 1: assume the function name line must ends with ) or {;
    if line[-1] != ')' and line[-1] != '{':
        return None
# Rule 2: (*) must in
    if '(' not in line or ')' not in line:
        return None
# Rule 3: # stands for #include or other primitives; / start a comment
    if line[0] == '#' or line[0] == '/':
        return None

# replace pointer * and & as space
    line = re.sub('\*', ' ', line)
    line = re.sub('\&', ' ', line)

# replace '(' as ' ('
    #re.sub('(', ' ( ', line)
    line = re.sub('\(', ' \( ', line)
    line_split = line.split()

    if len(line_split) < 2:
        return None

    bracket_num = 0
    for ch in line:
        if ch == '(':
            bracket_num += 1

    if bracket_num == 1:
        for index in range(len(line_split)):
            if '(' in line_split[index]:
                if is_not_ctl_statement(line_split[index - 1]):
                    return trim_prefix(line_split[index - 1])
                else:
                    return None
    else:
        line = re.sub('\(', ' ', line)
        line = re.sub('\)', ' ', line)
        line_split = line.split()
        index = 0
        for one in line_split:
            if is_valid_name(one):
                index += 1
                if index == 2:
                    if is_not_ctl_statement(one):
                        return trim_prefix(one)
        return None

def get_changed_func_names(path_for_git):

    origin_workdir = os.getcwd()
    os.chdir(path_for_git)

    stream = os.popen("git log --oneline") # TODO. only for source files
    logs = stream.read().split('\n')

    curr_commit_id = logs[0].split(' ')[0]
    prev_commit_id = logs[1].split(' ')[0]

    # git_diff_cmd = "git diff --function-context " + prev_commit_id + " " + curr_commit_id + " > ./diff_log"
    git_diff_cmd = "git diff --function-context HEAD^ HEAD > ./diff_log"
    os.system(git_diff_cmd)

    func_names = set()

    f = open("./diff_log", 'r')
    for line in f.readlines():
        func_name = extract_func_name(line)
        if func_name != None and func_name != "main":
            func_names.add(func_name)

    os.system("rm ./diff_log")
    os.chdir(origin_workdir)
    
    if const.DEBUG == True:
        print("\n[DEBUG] FUNC NAMES FROM GIT DIFF")
        for func_name in set(func_names):
            print(func_name)

    return func_names

def get_random_dirname(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(len))

def get_seeds_for_local_mode(origin_seed_dir, per_func_seed_dir, changed_funcs):
    new_seed_dir = get_random_dirname(8)
    os.mkdir(new_seed_dir)

    func_for_seed_lists = os.listdir(per_func_seed_dir)

    if const.DEBUG == True:
        print("\n[DEBUG] PER FUNC SEED DIR")
        for f in func_for_seed_lists:
            print(f)

        print("\n[DEBUG] CHANGED FUNS")
    files_to_read = []
    for changed_func in changed_funcs:
        if changed_func in func_for_seed_lists:
            files_to_read.append(os.path.join(per_func_seed_dir, changed_func))
            if const.DEBUG == True:
                print(os.path.join(per_func_seed_dir, changed_func))

    selected_names = set()   
    for fname in files_to_read:
        f = open(fname)
        for line in f.readlines():
            selected_names.add(line.strip()) 

    selected_seeds = []
    copied_seeds = []

    for name in selected_names:
        selected_seeds.append(os.path.join(origin_seed_dir, name))
        copied_seeds.append(os.path.join(new_seed_dir, name))

    for i in range(len(selected_seeds)):
        shutil.copyfile(selected_seeds[i], copied_seeds[i])

    return new_seed_dir

# class CrashOccured (Exception) :
#     def __init__(self, message) :
#         super().__init__(message)

crash_occured = threading.Event()
timeout_occured = threading.Event()

def on_created (event) :
    print(event.src_path, "has created")
    # raise CrashOccured(event.src_path)
    crash_occured.set()

def monitor_crash_dir (proc_pid) :
    
    event_handler = FileSystemEventHandler()
    event_handler.on_created = on_created

    path = "./" + const.OUT_DIR + "/default/crashes"
    path = os.path.realpath(path)

    while os.path.isdir(path) == False : # polling...
        time.sleep(1)

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    while True :
        time.sleep(1)
        if crash_occured.is_set() or timeout_occured.is_set():
                break
            
    if const.DEBUG == True :
        print("\n[DEBUG] TURN OFF THE OBSERVER")
    
    observer.stop()
    observer.join()
    proc = psutil.Process(proc_pid)
    proc.kill()
    return

'''
    TODO use a return code?
    return code
    1 => afl-fuzz fail
    -N => timeout or signal

    TODO how to detect crash? : monitoring crash directory
'''
def execute_aflpp (aflpp_path, executable_name, local_seeddir_path, is_file_mode) :

    afl_fuzz_path = aflpp_path + "/afl-fuzz"
    cmd = [afl_fuzz_path, "-i", local_seeddir_path, "-o", const.OUT_DIR, executable_name]
    if is_file_mode == True:
        cmd.append("@@")

    env_var = os.environ.copy()
    env_var["AFL_SKIP_CPUFREQ"] = "1"
    env_var["AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES"] = "1"
     
    try:
        proc = subprocess.Popen(cmd, env=env_var)
        observer_thread = threading.Thread(target=monitor_crash_dir, args=(proc.pid))
        observer_thread.daemon = True
        observer_thread.start()
        proc.wait(timeout=const.TIMEOUT)
    except subprocess.TimeoutExpired:
        timeout_occured.set()
        proc.kill()

    observer_thread.join()

    return proc.returncode

