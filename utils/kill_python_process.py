import os
import subprocess

def KillPythonProcess():
    sub_proc = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    output, error = sub_proc.communicate()

    target_process = "python3"
    for line in output.splitlines():
        if target_process in str(line):
            pid = int(line.split(None, 1)[0])
            os.kill(pid, 9)
            # print(pid)
    
    os.system('echo 123 | sudo -S sudo systemctl restart nvargus-daemon.service')
