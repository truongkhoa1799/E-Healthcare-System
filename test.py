import threading, time

def printText():
    print("Hello")
    time.sleep(1)

main_thread = threading.Thread(target=printText, args=())
main_thread.daemon = True
main_thread.start()

time.sleep(2)
print(main_thread.is_alive())