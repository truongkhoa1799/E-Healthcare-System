import sys
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')
import pickle
from azure.iot.hub import IoTHubRegistryManager
from utils.parameters import *

def Save_Connection(connection):
    with open(CONNECTION_LIST_PATH, mode='wb') as fp_1:
        pickle.dump(connection, fp_1)

def Get_Connection_String(device_ID):
    try:
        iothub_registry_manager = IoTHubRegistryManager(IOT_HUB_CONNECTION)
        device = iothub_registry_manager.get_device(device_ID)
        print("hello")
        primary_key = device.authentication.symmetric_key.primary_key

        iothub_connection = RESPONSE_IOTHUB_CONNECTION.format(device_ID, primary_key)

        return 0, iothub_connection
    except Exception as ex:
        print ( "\tUnexpected error {0} while getting iothub_connection".format(ex))
        return -1, 0

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Invalid arguements")
        exit(-1)
    
    try:
        device_ID = int(sys.argv[1])
        event_hub_connection = str(sys.argv[2])
        event_hub_name = str(sys.argv[3])

        ret, iothub_connection = Get_Connection_String(device_ID)
        if ret == 0:
            conn = {'device_ID':device_ID, 'device_iothub_connection':iothub_connection, 'eventhub_connection':event_hub_connection, 'eventhub_name':event_hub_name}
            Save_Connection(conn)
            print("\tDEVICEID is: {}".format(device_ID))
            print("\tDEVICE_IOT_HUB_CONNECTION is: {}".format(iothub_connection))
            print("\tEVENT Hub connection is: {}".format(event_hub_connection))
            print("\tEVENT Hub name is: {}".format(event_hub_name))

            exit(0)
    except Exception as ex:
        print ( "\tUnexpected error {0} while getting iothub_connection".format(ex))
        exit(-1)