import os
import subprocess

from utils.parameters import glo_va
from signal import signal, SIGINT, SIGTERM

def KillPythonProcess():
    if glo_va.flg_init_camera == True:
        print('Clear cam CSI')
        os.system('echo 123 | sudo -S sudo systemctl restart nvargus-daemon.service')
        glo_va.flg_init_camera = False

    sub_proc = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    output, error = sub_proc.communicate()

    target_process = "python3"
    for line in output.splitlines():
        if target_process in str(line):
            pid = int(line.split(None, 1)[0])
            # print(pid)
            os.kill(pid, SIGTERM)

# KillPythonProcess()