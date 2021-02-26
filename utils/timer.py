from utils.parameters import *
from threading import Timer
import time
import uuid
CYCLE_TIMER_PERIOD = 1

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Timer:
    def __init__(self):
        # opt: 0 timer for request validate user
        self.__timeout_validate = 0
        self.__flg_timeout_validate = False
        glo_va.current_timer_id_validation = str(uuid.uuid4())

        self.__counter=RepeatTimer(CYCLE_TIMER_PERIOD, self.Update_Timer)
        self.__counter.start()
    
    def Update_Timer(self):
        if self.__flg_timeout_validate:
            self.__timeout_validate = self.__timeout_validate + 1

        if self.__timeout_validate == TIMEOUT_VALIDATE:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print("\t[{time}]: Timer is expired".format(time=current_time))
            glo_va.lock_response_server.acquire()
            if glo_va.lock_timer_expir == True:
                self.Clear_Timer(OPT_TIMER_VALIDATE)
                glo_va.lock_response_server.release()
            else:
                self.Clear_Timer(OPT_TIMER_VALIDATE)
                glo_va.lock_response_server.release()
                glo_va.is_sending_message = False
            
    def Clear_Timer(self, opt):
        if opt == 0:
            self.__timeout_validate = 0
            self.__flg_timeout_validate = False
            glo_va.current_timer_id_validation = str(uuid.uuid4())
    
    def Start_Timer(self, opt):
        if opt == 0:
            self.__flg_timeout_validate = True
    
    def Stop(self):
        self.__counter.cancel()
        self.__counter.join()
        