import os, time

from utils.common_functions import LogMesssage

class ConnectWifi:
    def __init__(self):
        self.command_rescan_wifi = "echo 123 | sudo -S nmcli device wifi rescan"
        self.command_connect = "echo 123 | sudo -S nmcli d wifi connect {} password {}"
        self.command_check_status = "nmcli device status | grep wlan0"

        # os.system(self.command_rescan_wifi)
        LogMesssage("[ConnectWifi_init]: Scan the Wifi")
    
    def checkStatus(self):
        result = os.popen(self.command_check_status)
        result = [i for i in list(result)[0].split(" ") if (i != "" and i != '\n')]
        print(result[2])
    
    def connectWifi(self, ssid, password):
        result = os.popen(self.command_connect.format(ssid, password))
        result = list(result)
        print(result)
        if len(result) == 1:
            return -1
        else: return 0

# wifi = ConnectWifi()
# # wifi.checkStatus()
# print(wifi.connectWifi("KHOA", "Khoa9872134"))