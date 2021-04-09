import hid
import time, sys
import statistics
import random

sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')
from utils.parameters import *
from utils.common_functions import LogMesssage

# enumerate USB devices

# for d in hid.enumerate():
#     keys = list(d.keys())
#     keys.sort()
#     for key in keys:
#         print("%s : %s" % (key, d[key]))
#     print()

# try opening a device, then perform write and read

# [79, TH_OFFSET, HR, 0, x, x, TD0, TD1, TS_OFFSET, 0, SPO2, 0, PI0, PI1]
# def getSensorData():
#     try:
#         print("Opening the device")

#         h = hid.device()
#         h.open(1155, 22320)  # TREZOR VendorID/ProductID
#         print("Manufacturer: %s" % h.get_manufacturer_string())
#         print("Product: %s" % h.get_product_string())
#         print("Serial No: %s" % h.get_serial_number_string())

#         # enable non-blocking mode
#         h.set_nonblocking(1)

#         # read data from device
#         print("Reading the data")
#         start = time.time()
#         HexString = []
#         dataString = []

#         while (time.time() - start) < 20:
#             d = h.read(64)
#             if d:
#                 dataString.append(d)
#                 hexString = ""
#                 subStrSet = []
#                 for n in d:
#                     hexString += hex(n)
#                 hexString = hexString.replace('x', '')
#                 subStrSet = hexString.split('0a0d')
#                 subStrSet = subStrSet[:-1]
#                 HexString.append(subStrSet)

#         print("Closing the device")
#         h.close()
#         print('LEN:')
#         # print(dataStr)
#         print(len(HexString))
#         # print(HexString[len(HexString) - 1])
#         print(len(dataString))

#         spo2List = []
#         heartRateList = []

#         for subStrSet in HexString:
#             for subStr in subStrSet:
#                 if (subStr[:3] == '04f'):
#                     OFFSET = subStrSet.index(subStr) * 16
#                     hrIdx = OFFSET + 2
#                     spo2Idx = OFFSET + 10
#                     dataIdx = HexString.index(subStrSet)
#                     hrData = dataString[dataIdx][hrIdx]
#                     heartRateList.append(hrData)
#                     print('HR:')
#                     print(hrData)
#                     spo2Data = dataString[dataIdx][spo2Idx]
#                     spo2List.append(spo2Data)
#                     print('SPO2:')
#                     print(spo2Data)

#         spo2 = statistics.mean(spo2List)
#         heartRate = statistics.mean(heartRateList)
#         print(spo2)
#         print(heartRate)

#     except IOError as ex:
#         print(ex)
#         print("You probably don't have the hard-coded device.")
#         print("Update the h.open() line in this script with the one")
#         print("from the enumeration list output above and try again.")

#     print("Done")

def testReadSensor():
    LogMesssage('[testReadSensor]: Start capture spo2 and heart rate')
    list_spo2 = []
    list_hr = []

    for i in range(20):
        hr = random.randint(60,110)
        spo2 = random.randint(90,100)
        
        glo_va.temp_sensor['hr'] = hr
        glo_va.temp_sensor['spo2'] = spo2
        
        print(glo_va.temp_sensor['hr'])
        print(glo_va.temp_sensor['spo2'])

        list_hr.append(hr)
        list_spo2.append(spo2)

        time.sleep(1)
    
    glo_va.temp_sensor['hr'] = statistics.mean(list_spo2)
    glo_va.temp_sensor['spo2'] = statistics.mean(list_hr)

    LogMesssage('[testReadSensor]: Done capture spo2 and heart rate')
    return


# getSensorData()