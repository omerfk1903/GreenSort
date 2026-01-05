from Yolov8WithObjectsDetections import Yolov8

Sys = Yolov8(
    FunchControl=1,# hangi funch çalıştıracaksın
    Embedded_Systeam_Search="Plc",# Mikrodenetleyici seçimi ("Arduino","Plc") 
    PLC_ip_v4="192.168.0.1",PLC_Port=502,PLC_Start_Command=False,PLC_register_Adress=0,# plc tanımları
    Socket_Camera_Send=False,write_timeout=0.1,timeout=1,baudrate=19200,LoopSerialSend=0,CONTROL_KEYBOARD=True,# serial and socket
    ScreenControl=True,ScreanSize=(640,480), # screen
    ToleransWeightControl=0,ToleransMiddle=10,Tolerans=0, # tolerans
    sleepLoop=0.005,buttonSleep=0.03,# bekleme
    CMD_Control=False,#cmd komut satırını kapat
    distance=8, 
    Memory_chech_sleep=1)

if __name__ == "__main__" :
    
    if  Sys.FunchControl == 1 : 

        Sys.Threading()

    elif Sys.FunchControl == 2 :

        while True :
            
            Sys.PLC_Socket(Try=True)

    else : print(" Böyle bir seçenek yok")
    
Sys.cap.release()
