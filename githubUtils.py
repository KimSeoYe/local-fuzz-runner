import os
import subprocess

import const

ISSUE_TITLE = "Automatically created issue from GitHub Action workflow"

def reproduce_crash (executable_path) :
    crash_path = "./" + const.OUT_DIR + "/default/crashes"

    crash_inputs = os.listdir(crash_path)

    if crash_inputs[0] != None :
        input = open(crash_path + "/" + crash_inputs[0])
        cmd = executable_path
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,stdin=input,stderr=subprocess.PIPE)
        proc.wait()

        (stdoutdata, stderrdata) = proc.communicate()
        print(stdoutdata)
        print(stderrdata)
        return stderrdata

'''
gh issue create --title "Issue title" --body "Issue body" --label "bug"  ...

* use [const.OUT_DIR]/default/crash/[seed_name]
'''
def report_issue (executable_path) :
    reproduce_crash(executable_path)
    return