import os
import sys
import yaml
import pickle
import pathlib
from azure.iot.hub import IoTHubRegistryManager

config_para_path = None
azure_connection_path = None

event_hub_name = None
iothub_connection = None
event_hub_connection = None

def Save_Connection(connection):
    with open(azure_connection_path, mode='wb') as fp_1:
        pickle.dump(connection, fp_1)

def Get_Connection_String(device_ID):
    try:
        iothub_registry_manager = IoTHubRegistryManager(iothub_connection)
        device = iothub_registry_manager.get_device(device_ID)
        primary_key = device.authentication.symmetric_key.primary_key

        device_iothub_connection = 'HostName=thesisehealthcare.azure-devices.net;DeviceId={};SharedAccessKey={}'
        device_iothub_connection = device_iothub_connection.format(device_ID, primary_key)

        return 0, device_iothub_connection
    except Exception as ex:
        print ( "\tUnexpected error {0} while getting iothub_connection".format(ex))
        return -1, 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Invalid arguements")
        exit(-1)
    
    try:
        device_ID = int(sys.argv[1])
        config_para_path = pathlib.Path().absolute()
        config_para_path = os.path.join(config_para_path, 'config_para.yaml')

        with open(config_para_path, 'r') as file:
            documents = yaml.full_load(file)
            # print(documents)

            # Connection server
            event_hub_name = str(documents['azure']['eventhub_name'])
            event_hub_connection = str(documents['azure']['eventhub_connection'])
            iothub_connection = str(documents['azure']['iothub_connection'])

            azure_connection_path = str(documents['path']['azure_connection_path'])

        ret, device_iothub_connection = Get_Connection_String(device_ID)
        if ret == 0:
            conn = {'device_ID':device_ID, 'device_iothub_connection':device_iothub_connection, 'eventhub_connection':event_hub_connection, 'eventhub_name':event_hub_name}
            Save_Connection(conn)
            print("\tDevice ID is: {}".format(device_ID))
            print("\tDevice IOT hub connection is: {}".format(device_iothub_connection))
            print("\tEvent hub connection is: {}".format(event_hub_connection))
            print("\tEvent hub name is: {}".format(event_hub_name))

            exit(0)
    except Exception as ex:
        print ( "\tUnexpected error {0} while getting iothub_connection".format(ex))
        exit(-1)
