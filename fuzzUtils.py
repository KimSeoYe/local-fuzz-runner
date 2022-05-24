from __future__ import print_function #for python 2.7

import os
import re
import sys
import random
import string
import shutil

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

    stream = os.popen("git log --oneline") 
    logs = stream.read().split('\n')

    curr_commit_id = logs[0].split(' ')[0]
    prev_commit_id = logs[1].split(' ')[0]

    git_diff_cmd = "git diff --function-context " + prev_commit_id + " " + curr_commit_id + " > ./diff_log"
    os.system(git_diff_cmd)

    func_names = set()

    f = open("./diff_log", 'r')
    for line in f.readlines():
        func_name = extract_func_name(line)
        if func_name != None and func_name != "main":
            func_names.add(func_name)

    os.system("rm ./diff_log")
    os.chdir(origin_workdir)
    
    # print("\n[DEBUG] FUNC NAMES ***")
    # for func_name in set(func_names):
    #     print(func_name)

    return func_names

def get_random_dirname(len):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(len))

def get_seeds_for_local_mode(origin_seed_dir, per_func_seed_dir, changed_funcs):
    new_seed_dir = get_random_dirname(8)
    os.mkdir(new_seed_dir)

    func_for_seed_lists = os.listdir(per_func_seed_dir)

    # print("\n[DEBUG] PER FUNC SEED DIR")
    # for f in func_for_seed_lists:
    #     print(f)

    # print("\n[DEBUG] CHANGED FUNS")
    files_to_read = []
    for changed_func in changed_funcs:
        if changed_func in func_for_seed_lists:
            files_to_read.append(os.path.join(per_func_seed_dir, changed_func))
            # print(os.path.join(per_func_seed_dir, changed_func))

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

    # Q. make tmp dir and copy the seeds?
    for i in range(len(selected_seeds)):
        shutil.copyfile(selected_seeds[i], copied_seeds[i])

    return new_seed_dir


