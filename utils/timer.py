from utils.parameters import *
from identifying_users.identifying_users_functions import Submit_Again
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

        self.__timeout_get_examination_room = 0
        self.__flg_timeout_get_examination_room = False

        self.__timeout_submit_examination = 0
        self.__flg_timeout_submit_examination = False

        self.timer_id = None

        self.__counter=RepeatTimer(CYCLE_TIMER_PERIOD, self.Update_Timer)
        self.__counter.start()
    
    def Update_Timer(self):
        # print("Validating: {}, {}".format(self.__flg_timeout_validate, self.__timeout_validate))
        # print("Get exam room: {}, {}".format(self.__flg_timeout_get_examination_room, self.__timeout_get_examination_room))
        # print()
        # print(glo_va.turn)
        if self.__flg_timeout_validate:
            self.__timeout_validate = self.__timeout_validate + 1

        if self.__flg_timeout_get_examination_room:
            self.__timeout_get_examination_room = self.__timeout_get_examination_room + 1

        if self.__flg_timeout_submit_examination:
            self.__timeout_submit_examination = self.__timeout_submit_examination + 1

        # Check if time out for valifation or not
        if self.__timeout_validate >= TIMEOUT_VALIDATE:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print("\t[{time}]: Timer for validation is expired".format(time=current_time))

            # Acquire lock to stop server receive response
            glo_va.lock_response_server.acquire()
            # if server is not acquire first, get lock and resend again message
            if glo_va.turn == -1:
                glo_va.is_sending_message = False
                glo_va.lock_response_server.release()
            # if server has received response, set lock = -1 for the next time out
            elif glo_va.turn == 1:
                glo_va.turn = -1
                glo_va.lock_response_server.release()
                return
            
            self.Clear_Timer()
        
        # Get the examaniation room
        if self.__timeout_get_examination_room >= TIMEOUT_GET_EXAMINATION_ROOM:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print("\t[{time}]: Timer for getting examination room is expired".format(time=current_time))
            ret = Submit_Again()
            glo_va.lock_response_server.acquire()
            if glo_va.turn == -1:
                glo_va.is_sending_message = False
                glo_va.lock_response_server.release()
            elif glo_va.turn == 1:
                glo_va.turn = -1
                glo_va.lock_response_server.release()
                return
            
            self.Clear_Timer()
        
        # Get the examaniation room
        if self.__timeout_submit_examination >= TIMEOUT_SUBMIT_EXAMINATION:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            print("\t[{time}]: Timer for submit examination is expired".format(time=current_time))
            glo_va.lock_response_server.acquire()
            if glo_va.turn == -1:
                glo_va.is_sending_message = False
                glo_va.lock_response_server.release()
            elif glo_va.turn == 1:
                glo_va.turn = -1
                glo_va.lock_response_server.release()
                return
            self.Clear_Timer()


    def Clear_Timer(self):
        self.__timeout_validate = 0
        self.__flg_timeout_validate = False
        
        self.__timeout_get_examination_room = 0
        self.__flg_timeout_get_examination_room = False

        self.__timeout_submit_examination = 0
        self.__flg_timeout_submit_examination = False
    
    def Start_Timer(self, opt):
        if opt == OPT_TIMER_VALIDATE:
            self.__timeout_validate = 0
            self.__flg_timeout_validate = True
            self.timer_id = str(uuid.uuid4())

        if opt == OPT_TIMER_GET_EXAMINATION_ROOM:
            self.__timeout_get_examination_room = 0
            self.__flg_timeout_get_examination_room = True
            self.timer_id = str(uuid.uuid4())

        if opt == OPT_TIMER_SUBMIT_EXAMINATION:
            self.__timeout_submit_examination = 0
            self.__flg_timeout_submit_examination = True
            self.timer_id = str(uuid.uuid4())
    
    def Stop(self):
        self.__counter.cancel()
        self.__counter.join()
        