import os
import re

def is_valid_name(name):
    if re.match("[a-zA-Z_][a-zA-Z0-9_]*", name) == None:
        return False
    return True

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
                return line_split[index - 1]
    else:
        line = re.sub('\(', ' ', line)
        line = re.sub('\)', ' ', line)
        line_split = line.split()
        index = 0
        for one in line_split:
            if is_valid_name(one):
                index += 1
                if index == 2:
                    return one
        return None



stream = os.popen("git log --oneline") 
logs = stream.read().split('\n')

curr_commit_id = logs[0].split(' ')[0]
prev_commit_id = logs[1].split(' ')[0]

git_diff_cmd = "git diff --function-context " + curr_commit_id + " " + prev_commit_id + " >> ./diff_log"
os.system(git_diff_cmd)

file = open("./diff_log", 'r')
for line in file.readlines():
    func_name = extract_func_name(line)
    if func_name != None:
        print(func_name)

os.system("rm ./diff_log")