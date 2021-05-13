from utils.parameters import *
from utils.common_functions import LogMesssage
from threading import Timer
import time, uuid
CYCLE_TIMER_PERIOD = 1

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class TimerModule:
    def __init__(self):
        # opt: 0 timer for request validate user
        self.__timeout_validate = 0
        self.__flg_timeout_validate = False

        self.__timeout_get_examination_room = 0
        self.__flg_timeout_get_examination_room = False

        self.__timeout_submit_examination = 0
        self.__flg_timeout_submit_examination = False

        self.__timeout_send_voice_message = 0
        self.__flg_timeout_send_voice_message = False

        self.__timeout_get_init_parameters = 0
        self.__flg_timeout_get_init_parameters = False

        self.__timeout_missing_face = 0

        self.timer_id = -1

        self.__counter=RepeatTimer(CYCLE_TIMER_PERIOD, self.Update_Timer)
        self.__counter.daemon = True
        self.__counter.start()
    
    def Update_Timer(self):
        try:
            self.__timeout_missing_face = self.__timeout_missing_face + 1

            if self.__timeout_missing_face >= glo_va.TIMEOUT_MISSING_FACE:
                self.__timeout_missing_face = 0
                glo_va.times_missing_face = 0

            if self.__flg_timeout_validate:
                self.__timeout_validate = self.__timeout_validate + 1

                # Check if time out for valifation or not
                if self.__timeout_validate >= glo_va.TIMEOUT_VALIDATE:
                    LogMesssage("[__Check_Timer]: Timer for validation is expired")

                    self.__Check_Timer()

            if self.__flg_timeout_get_examination_room:
                self.__timeout_get_examination_room = self.__timeout_get_examination_room + 1

                # Get the examaniation room
                if self.__timeout_get_examination_room >= glo_va.TIMEOUT_GET_EXAMINATION_ROOM:
                    LogMesssage("[__Check_Timer]: Timer for getting examination room is expired")

                    self.__Check_Timer()

            if self.__flg_timeout_submit_examination:
                self.__timeout_submit_examination = self.__timeout_submit_examination + 1
            
                # Get the examaniation room
                if self.__timeout_submit_examination >= glo_va.TIMEOUT_SUBMIT_EXAMINATION:
                    LogMesssage("[__Check_Timer]: Timer for submit examination is expired")
                    
                    self.__Check_Timer()

            if self.__flg_timeout_send_voice_message:
                self.__timeout_send_voice_message = self.__timeout_send_voice_message + 1
            
                # Get the examaniation room
                if self.__timeout_send_voice_message >= glo_va.TIMEOUT_SEND_MESSAGE_VOICE:
                    LogMesssage("[__Check_Timer]: Timer for send voice message is expired")
                    
                    self.__Check_Timer()

            if self.__flg_timeout_get_init_parameters:
                self.__timeout_get_init_parameters = self.__timeout_get_init_parameters + 1
            
                # Get the examaniation room
                if self.__timeout_get_init_parameters >= glo_va.TIMEOUT_GET_INIT_PARAMETERS:
                    LogMesssage("[__Check_Timer]: Timer for getting init parameters is expired")
                    
                    self.__Check_Timer()
        
        except Exception as e:
            LogMesssage('Has error at Update_Timer in timer: {e}'.format(e=e))

            if glo_va.lock_response_server.locked() == True:
                glo_va.lock_response_server.release()
                LogMesssage('[__Check_Timer]: Release lock response server')

    def __Check_Timer(self):
        # Acquire lock to stop server receive response
        if glo_va.lock_response_server.acquire(False):
            LogMesssage('[__Check_Timer]: Acquire lock response server')

            # if server is not acquire first, get lock and resend again message
            if glo_va.turn == glo_va.TIMER_GOT_BY_NO_ONE:
                self.Clear_Timer()
                glo_va.is_sending_message = False
                LogMesssage('[__Check_Timer]: is_sending_message is reset')
                LogMesssage('[__Check_Timer]: Release lock response server')
                glo_va.lock_response_server.release()

            # if server has received response, set lock = -1 for the next time out
            elif glo_va.turn == glo_va.TIMER_GOT_BY_SERVER:
                glo_va.turn = glo_va.TIMER_GOT_BY_NO_ONE
                LogMesssage('[__Check_Timer]: Has response from server first')
                LogMesssage('[__Check_Timer]: Release lock response server')
                glo_va.lock_response_server.release()
                return
                
        else:
            LogMesssage('[__Check_Timer]: Acquire lock response server fail')

    def Clear_Timer(self):
        self.timer_id = -1

        self.__timeout_validate = 0
        self.__flg_timeout_validate = False
        
        self.__timeout_get_examination_room = 0
        self.__flg_timeout_get_examination_room = False

        self.__timeout_submit_examination = 0
        self.__flg_timeout_submit_examination = False

        self.__timeout_send_voice_message = 0
        self.__flg_timeout_send_voice_message = False

        self.__timeout_get_init_parameters = 0
        self.__flg_timeout_get_init_parameters = False
    
    def Start_Timer(self, opt):
        if opt == glo_va.OPT_TIMER_VALIDATE:
            self.__timeout_validate = 0
            self.__flg_timeout_validate = True
            self.timer_id = str(uuid.uuid4())

        if opt == glo_va.OPT_TIMER_GET_EXAMINATION_ROOM:
            self.__timeout_get_examination_room = 0
            self.__flg_timeout_get_examination_room = True
            self.timer_id = str(uuid.uuid4())

        if opt == glo_va.OPT_TIMER_SUBMIT_EXAMINATION:
            self.__timeout_submit_examination = 0
            self.__flg_timeout_submit_examination = True
            self.timer_id = str(uuid.uuid4())

        if opt == glo_va.OPT_TIMER_SEND_MESSAGE_VOICE:
            self.__timeout_send_voice_message = 0
            self.__flg_timeout_send_voice_message = True
            self.timer_id = str(uuid.uuid4())

        if opt == glo_va.OPT_TIMER_GET_INIT_PARAMETERS:
            self.__timeout_get_init_parameters = 0
            self.__flg_timeout_get_init_parameters = True
            self.timer_id = str(uuid.uuid4())
    
    def Stop(self):
        self.__counter.cancel()
        self.__counter.join()
        