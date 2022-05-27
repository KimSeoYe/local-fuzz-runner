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


def report_issue (executable_path) :
    stderr_data = reproduce_crash(executable_path)
    
    cmd = "curl --request POST \\\n"
    cmd += "--url https://api.github.com/repos/${{github.repository}}/issues \\\n"
    cmd += "--header 'authorization: Bearer ${{secrets.TOKEN}}' \\\n"   # TODO TOKEN : user dependent name
    cmd += "--header 'content-type: application/json' \\\n"
    cmd += "--data \'{ \"title\": \"" + ISSUE_TITLE + ": ${{github.run_id}} \""
    cmd += "\"body\": \"" + stderr_data + "\" }\'"

    proc = subprocess.Popen(cmd)
    proc.wait()

    print("\nISSUE REPORT IS PUBLISHED")
    return