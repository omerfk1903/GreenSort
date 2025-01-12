from Yolov8WithObjectsDetections import Yolov8

Sys = Yolov8(
    timeout=1,
    Socket_Camera_Send=True,
    write_timeout=0.1,
    FunchControl=1,
    CMD_Control=True,
    baudrate=19200,
    ScreenControl=True,
    ToleransWeightControl=0,
    ToleransMiddle=10,
    sleepLoop=0.005,
    buttonSleep=0.03,
    LoopSerialSend=0,
    distance=8,
    CONTROL_KEYBOARD=True,
    ScreanSize=(640,480),
    Tolerans=0,
    Memory_chech_sleep=1)

if __name__ == "__main__" :
    
    if  Sys.FunchControl == 1 : 

        Sys.Threading()
    
Sys.cap.release()