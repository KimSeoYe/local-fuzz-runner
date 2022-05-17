import os

stream = os.popen("git log --oneline") 
logs = stream.read().split('\n')

curr_commit_id = logs[0].split(' ')[0]
prev_commit_id = logs[1].split(' ')[0]

git_diff_cmd = "git diff --function-context " + curr_commit_id + " " + prev_commit_id + " >> ./diff_log"
os.system(git_diff_cmd)

file = open("./diff_log", 'r')
for line in file.readlines():
    print(line)

os.system("rm ./diff_log")
