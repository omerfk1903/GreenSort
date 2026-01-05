import cv2 # Opencv 
import pickle
import struct
import socket as sc # socket
from ultralytics import YOLO # Yapay zeka kontrol
from serial import Serial # Serial haberleşme için kullanılır 
from serial.tools.list_ports import comports # Port okuma 
from numpy import int32,array,uint8 # Dizi kontrol için kullanılır 
from torch.backends.mps import is_available # Ekran kartı olarak hangisinin aktif olduğunu verir
from json import loads,dumps # Dizileri parçalamak için kullanılmıştır
from math import ceil # Yukarı yuvarlama
from time import sleep,time # Bekleme
from os.path import exists # Dosya varlığı kontrol ediliyor
from os import name,getcwd # İşletim sistemi bilgisi alınıyor
from threading import Thread,Event,current_thread # Çekirdek kontrol 
from gc import collect # Bellek temizleme işlemi
from logger import setup_logger # Sistemde olan bitenleri log dosyasına yazıran kütüphane
from pyModbusTCP.client import ModbusClient # PLC ile arasındaki iletişim için kullanılan kütüphane
from random import randint # random degerler üretme .

class Yolov8 :

    def __init__(self,FunchControl,Embedded_Systeam_Search,Socket_Camera_Send,baudrate,PLC_Start_Command,write_timeout,timeout,LoopSerialSend,Memory_chech_sleep,CMD_Control,Tolerans,distance,CONTROL_KEYBOARD,ScreanSize,ToleransWeightControl,ScreenControl,PLC_ip_v4,PLC_register_Adress,PLC_Port,ToleransMiddle,buttonSleep,sleepLoop) :

        self.classNames = ['Aliminyum', 'Aliminyum', 'Aliminyum', 'Aliminyum','Aliminyum',
        'Glass','Glass',
        'paper','paper','paper',
        'Plastic','Plastic','Plastic','Plastic']
    
        self.prev_frame_time = 0
        self.new_frame_time = 0
        self.Hipotlatest = 0
        self.errorLogsave= 0
        self.Time = 0
        self.LasTime = 0
        self.lasTime = 0
        self.plc_send_value = 0
        
        self.PLC_Start_Command = PLC_Start_Command
        self.Memory_chech_sleep = Memory_chech_sleep
        self.CMD_Control = CMD_Control
        self.FunchControl = FunchControl
        self.CONTROL_KEYBOARD = CONTROL_KEYBOARD        
        self.ScreenControl = ScreenControl
        self.DraweControl = True
        self.ToleransWeightControl = ToleransWeightControl
        self.Tolerans = Tolerans
        self.ToleransMiddle = ToleransMiddle
        self.pixel = 0.026458 # 0,026 458 333 333 333 santime çevirmek için
        self.sleepLoop = sleepLoop # 0.05
        self.buttonSleep = buttonSleep # 0.09
        self.LoopSerialSend = LoopSerialSend
        self.Socket_Camera_Send = Socket_Camera_Send
        self.Embedded_Systeam_Search = Embedded_Systeam_Search #
        
        # PLC ile haberleşme için gerekli olan girdiler.
        self.PLC_Port = PLC_Port
        self.PLC_ip_v4 = PLC_ip_v4
        self.PLC_register_Adress = PLC_register_Adress
        self.plc_step = 0
        self.plc_send = [0,0,0]
        self.plc_last_rand = 0

        # MENÜ ÜİLE ARSINDAKİ VERİ İLETİŞİMİ İÖİN GEREKLİ OLAN GİRDİLER.
        MENU_HOST = "localhost"  # Sunucu adresi
        MENU_PORT = 8000  # Sunucu portu
        
        self.send = None
        self.lasSend = None
        self.KEYBOARD = 0xFF
        self.vertices = array([[(75, 525), (440, 320), (520, 330), (920, 525)]], int32)  # köşeler
        
        # Logger başlatılıyor
        self.logger = setup_logger(txt="Yolov8")

        # Dosya yolları
        self.MainFilePath = getcwd()
        self.pathLog = f"{self.MainFilePath}\\log.txt"
        self.Path2 = f"{self.MainFilePath}\\best.pt"
        self.pathSplite = self.Path2.split('\\')
        self.pathSpliteLen = len(self.pathSplite)

        # Ekran boyut bilgileri
        self.ScreenHeight = ScreanSize[0] # yükseklik
        self.ScreenWeight = ScreanSize[1] # genişlik
        
        # Aktif olan ekran kartı çıktısı verilir
        self.Use_Grapich_card = "mps" if is_available() else "cpu"

        # Tetikleme işlemi 
        global event # global tanımlama yapılmıştır 
        event = Event()
        
        """
        if self.CMD_Control and name == "nt" : # CMD komut satırını gizlemek için kullanılır 
            from win32console import GetConsoleWindow
            from win32gui import ShowWindow
            win = GetConsoleWindow() 
            ShowWindow(win, 0)
            self.logger.info("OS : WİNDOWS")
        """

        if not self.CMD_Control and name != "nt" :
            from subprocess import Popen # linux 
            #Popen('shutdown','now') # linux komut satırını kapatmak
            self.logger.info("OS : LİNUX")
        
        # For camera
        try : 
            self.cap = cv2.VideoCapture(0)
            self.logger.info(" Camera connect")
        except : self.logger.warning("Camera disconnect") 

        # Yapay zeka kontrol 
        try : 
            self.model = YOLO(self.Path2)
            self.logger.info("Yolov8 model activate")
        except : self.logger.warning("Yolov8 model disactivate")
    
        if self.Use_Grapich_card == "cpu" : # CPU ekran kartı kullanılır ise çalışır 
            try :
                Thread_Funch_Counter = 5 # Bölünecek işlem sayısı
                if (Thread_Funch_Counter - 1) < 6 : cache = (Thread_Funch_Counter - 1) # önbellek değeri belirlenir
                else : cache = 6
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE,cache) # Önbellek boyutu artırılıyor
                cv2.useOptimized() # sistemi optimize ediliyor 
                cv2.setNumThreads(Thread_Funch_Counter) # Aynı anda yapılan işlem sayısı(Thread)
                cv2.setUseOptimized(True) # OPENCV AKTİF EDİYOR 
                cv2.ocl.setUseOpenCL(True) # OPENCL AKTİF EDİYOR
                self.logger.info("CPU graphics cart at activate")
            except : self.logger.error("CPU graphics cart at disactivate")
        else : self.logger.warning("GPU graphics disactivate")

        if self.Embedded_Systeam_Search == "Arduino" :
            try: # Serial iletişim başlatılması ve ayarlanması için kullanılır
                self.sr = Serial()
                self.sr.baudrate = baudrate
                self.sr.timeout = timeout
                #self.sr.write_timeout = write_timeout
                #self.sr.port = Port #Port ismi 
                self.sr.port = self.list_serial_ports()
                self.sr.open()
                self.sr.flush()
                if self.sr.is_open : self.logger.info("Serial connect : (NAME : {0} | PORT : {1})".format(self.sr.name,self.sr.port))
                else : self.logger.warning("Serial disconnect : (NAME : {0} | PORT : {1})".format(self.sr.name,self.sr.port))
            except : self.logger.warning("Serial disconnect : (NAME : {0} | PORT : {1})".format(self.sr.name,self.sr.port))
        
        if self.Embedded_Systeam_Search == "Plc" :
            try : # PLC TCP SERVER OLUŞTURULUYOR
                self.client = ModbusClient(
                    host=self.PLC_ip_v4,  # SERVER / PLC IP
                    port=self.PLC_Port,
                    auto_open=True,
                    auto_close=True)
                self.logger.info("PLC is ethernet to connect")
            except : self.logger.warning("PLC is not ethernet to connect")

        try : # Menü arasındaki port haberleşmesi. SERVER
            # Socket iletişimi başlatılıyor
            self.server_socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
            self.server_socket.bind((MENU_HOST, MENU_PORT))
            self.server_socket.listen(5)
            self.logger.info("Socket is connect for menu")
        except : self.logger.warning("Socket is not connect for menu")

        if Tolerans : self.logger(" Tolerans yok") 
        
        # Ana görüntünün boyutu ayarlanıyor 
        self.success, self.img = self.cap.read() # görüntü okunuyor
        self.img = cv2.resize(self.img,(self.ScreenHeight,self.ScreenWeight)) # EKRAN BOYUTU AYARLANIYOR
        (self.height, self.widht) = self.img.shape[:2] # Video boyutu alınıyor
        self.imgCopy = self.img.copy() # video görüntü kopyalanıyor
        
        # Cismin tespit için kullanılacak alan
        self.distance = distance
        self.Xcmdistance = self.distance/self.pixel
        self.Objectİmportent = int(ceil(self.widht - self.Xcmdistance)/2)
        self.Objectİmportent2 = self.widht - self.Objectİmportent
        self.Ycmdistance = int(ceil(self.Xcmdistance / 4))

        # Parçalanan görüntünün boyut bilgisi alınıyor 
        self.imgSplite = self.imgCopy[self.Ycmdistance:self.Ycmdistance + (self.height - self.Ycmdistance),
        self.Objectİmportent:self.Objectİmportent + abs(self.Objectİmportent2 - self.Objectİmportent)]
        (self.height, self.widht) = self.imgSplite.shape[:2] # Video boyutu alınıyor
        self.height = int(self.height)
        self.widht = int(self.widht)

        self.waitkey = cv2.waitKeyEx(0) 
        self.Key = self.waitkey & self.KEYBOARD == ord('q') # Key
        self.TimeButtonKey = self.waitkey & self.KEYBOARD == ord('x') # Time write and systeam control
        self.TimeButtonReadKey = self.waitkey & self.KEYBOARD == ord('r')

        if exists(self.Path2) : self.logger.info("This {0}  file found ".format(self.pathSplite[self.pathSpliteLen - 1]))
        else : self.logger.warning("This {0}  file not found ".format(self.pathSplite[self.pathSpliteLen - 1])) 
        
        # Başlangıç öncesi işlem 
        self.logger.info("5 second wait")
        for x in range(0,5) : 
            sleep(1)
            print(str(x + 1) + "..." )
        self.logger.info("Device ready the start")

    def SysteamFeedback(self) : # Makinenin durumunu aktaran fonksiyon
        """
        1 : Serial haberleşmenin durumunu .
        2 : Servoların durumlarını ve konumlarını . 
        3 : Band hareket etme durumunu .
        4 : Kamera görüntüsünü aktarması gereli . 
        """
        event.set()
        servok = 10 
        bandB = True 
        passCode = ["#Ab1","#Ab2","#Ab3"] # kodlar gönderilen verileri ayırt etmek için kullanılır.
        event.set()
        try : 
            if self.Embedded_Systeam_Search == "arduino" : 
                while self.sr.is_open :
                    send = (str(self.sr.is_open) + "/" + passCode[0]) # Serial haberleşme 
                    self.server_socket.sendall(send.encode('utf-8'))
                    sleep(0.5)
                    send = (str(servok) + "/" + passCode[1]) # Servonun konumu
                    self.server_socket.sendall(send.encode('utf-8'))
                    sleep(0.5)
                    send = (str(bandB) + "/" + passCode[2]) # bandın hareket durumu
                    self.server_socket.sendall(send.encode('utf-8'))
                    sleep(0.5)
        except sc.error as e : self.logger.warning(f"Socket is connect error : {e}")

    def CameraRecv(self) : 

        event.set()# tetiklem işlemi

        self.success, self.img = self.cap.read()

        while self.cap.isOpened() and self.success : 

            self.img = self.img.astype(uint8)#görüntü pixel uint8

            self.img = cv2.resize(self.img,(self.ScreenHeight,self.ScreenWeight))

            self.imgCopy = self.img.copy() 

            self.Xw = abs(self.Objectİmportent2 - self.Objectİmportent)

            self.Yw = abs(self.height - self.Ycmdistance)

            self.imgSplite = self.imgCopy[self.Ycmdistance:self.Ycmdistance + self.Yw,self.Objectİmportent:self.Objectİmportent + self.Xw]

            self.success, self.img = self.cap.read()
            
            if self.Key : break

            self.Key = self.waitkey & self.KEYBOARD == ord('q')   # Key

            self.waitkey = cv2.waitKeyEx(1)
            
            sleep(self.sleepLoop)

    def Socket_Send_Recv_Send(self) : # socket ile iletişim fonksiyonudur 
        cnt = 0 # 1 : zaman bilgisi toplama , 0 zaman bilgilerini işleme 
        countreSerial = 0
        def Menu_Socket_Control(client_socket,address):
            event.wait()
            global dataDecode
            while True :
                try : 
                    data = client_socket.recv(10) # 10 byte veri okuma
                    dataDecode = data.decode('utf-8') # byte türünden kullanılabilir türe dönüştürüyor
                    dD = str(dataDecode).split('/') # istediğimiz kısımları almak için parçalama yapılıyor
                    dataDecode = dD[1]
                    passSend = dD[0]
                    if (dataDecode == "A" and passSend == "#34") : # istenilen veri gelir ise çalışır 
                        for objectNameOut in self.classNames : 
                            if objectNameOut == self.objectName : 
                                self.send = self.objectName[0]
                        if cnt == 1 :
                            if (self.send == "g" or self.send == "G") and cnt == 1 : self.Time = time()
                            if (self.send == "d" or self.send == "D") and cnt == 1 : 
                                self.lasTime = time()
                                self.Time_Date_Write()
                            if (self.send == "r" or self.send == "R") and cnt == 1 : self.Time_Date_Read()
                        else : 
                            if self.Embedded_Systeam_Search == "Arduino" : self.SerialDate() # serial veri ile gönderiliyor.
                            else : self.PLC_Socket()
                    else : continue
                except sc.error or sc.timeout or ConnectionRefusedError or sc.gaierror : 
                    if countreSocket == 3 : 
                        self.logger.warning(f" Socket bağlantısın {countreSocket} denenedi ama bağlantı kurulamadığından port kapatıldı.")
                        break # 3 kere socket hatası deneniyor
                    countreSocket = countreSocket + 1 
                    continue # Sorun ile karşılaştırıldığında döngü başa geçer.
                sleep(self.sleepLoop)
                self.plc_send_value = self.send
                print(f" this Send is data : str : {self.send} | int : {ord(self.send)}")
        client_socket, address = self.server_socket.accept() 
        client_thread = Thread(target=Menu_Socket_Control, args=(client_socket,address,))
        client_thread.start()

    def YolovCameraObjectDetection(self) :

        event.wait()

        while self.cap.isOpened() :

            self.new_frame_time = time()
            
            results = self.model(self.imgSplite, stream=False,verbose=False)

            for r in results:
                boxes = r.boxes
                for box in boxes:

                    self.x1, self.y1, self.x2, self.y2 = map(int, boxes.xyxy[0])
                    
                    self.cls = int(box.cls[0])
                    self.objectName = self.classNames[self.cls]
                    
                    if self.Tolerans > 0 :
                        if self.ToleransWeightControl == 1 : # tolerans azaltıcı
                            self.x1 = ceil(self.x1 + (self.x1 * (self.Tolerans / 2)))
                            self.x2 = ceil(self.x2 - (self.x2 * (self.Tolerans / 2)))
                            self.y1 = ceil(self.y1 + (self.y1 * (self.Tolerans / 2)))
                            self.y2 = ceil(self.y2 - (self.y2 * (self.Tolerans / 2)))
                        else : # tolerans artırıcı
                            self.x1 = ceil(self.x1 - (self.x1 * (self.Tolerans / 2)))
                            self.x2 = ceil(self.x2 + (self.x2 * (self.Tolerans / 2)))
                            self.y1 = ceil(self.y1 - (self.y1 * (self.Tolerans / 2)))
                            self.y2 = ceil(self.y2 + (self.y2 * (self.Tolerans / 2)))

                    w = abs(int(self.x2 - self.x1))
                    h = abs(int(self.y2 - self.y1))

                    # cismin ortası
                    self.middleX = self.x1 + int(w / 2)
                    self.middleY = self.y1 + int(h / 2)
                           
                    # ekranın ortası
                    self.heightort = self.height / 2
                    self.widhtort = self.widht / 2

                    self.heightBack = int(self.heightort * abs(self.ToleransMiddle - 100) / 100)
                    self.heightForward = int(self.heightort * (self.ToleransMiddle + 100) / 100)

                    self.widhtBack = int(self.widhtort * abs(self.ToleransMiddle - 100) / 100)
                    self.widhtForward = int(self.widhtort * (self.ToleransMiddle + 100) / 100)
                             
                    self.heightControl  = self.heightBack < self.middleY and self.heightForward > self.middleY 
                    self.widhtControl   = self.widhtBack < self.middleX and self.widhtForward > self.middleX
                    self.HeightandWidht = self.heightControl and self.widhtControl 

                    if self.DraweControl :
                    
                        cv2.rectangle(self.img, pt1=(self.Objectİmportent  + self.widhtBack, self.heightBack + self.Ycmdistance), pt2=(self.Objectİmportent + self.widhtForward, self.heightForward + self.Ycmdistance), color=(255, 0, 0), thickness=2)
                        cv2.rectangle(self.img, pt1=(self.Objectİmportent + self.x1, self.y1 + self.Ycmdistance), pt2=(self.Objectİmportent+ self.x2, self.y2 + self.Ycmdistance), color=(255, 0, 255), thickness=2)
                        cv2.line(self.img, pt1=(self.Objectİmportent + self.middleX, self.Ycmdistance + self.middleY), pt2=(self.Objectİmportent + self.middleX, self.Ycmdistance + self.middleY), color=(255, 0, 0), thickness=3)
                        cv2.putText(self.img, self.objectName, (self.Objectİmportent + self.x1 - 2,self.y1 - 2), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(0, 100, 255), 1, cv2.LINE_AA)

                        if self.heightControl and self.widhtControl : 
                            
                            cv2.putText(self.img,"Object_Middle",(self.Objectİmportent + self.widhtBack + int((self.widhtForward-self.widhtBack)/2),
                            self.Ycmdistance + (self.heightBack-self.Ycmdistance) - 6),cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(150, 150, 255), 1, cv2.LINE_AA)
            
            fps = 1 / (self.new_frame_time - self.prev_frame_time)
            self.prev_frame_time = self.new_frame_time
            fps = int(round(fps,2))

            if self.DraweControl == 1 :

                cv2.rectangle(self.img,pt1=(self.Objectİmportent,self.Ycmdistance),pt2=(self.Objectİmportent2,self.Ycmdistance+self.Yw),color=(255,0,0),thickness=2)
                cv2.putText(self.img, str(fps), (20, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 100, 255), 1, cv2.LINE_AA)
            
            if self.ScreenControl : cv2.imshow("Image", self.img) # Görünütüyü dışarı aktarma 

            if self.Socket_Camera_Send == True : # socket ile kamera görüntüsünü aktarma 
                try : 
                    # Görüntüyü sıkıştır
                    encoded, buffer = cv2.imencode('.jpg', self.img, [cv2.IMWRITE_JPEG_QUALITY, 90])
                    data = pickle.dumps(buffer)
                    message = struct.pack("Q", len(data)) + data
                    # Görüntüyü gönder
                    self.server_socket.sendall(message)
                except : pass      

            if self.Key : break

            self.Key = self.waitkey & self.KEYBOARD == ord('q')   # Key

            self.waitkey = cv2.waitKeyEx(1) 
            
            sleep(self.sleepLoop)

    def OpencvKeyControlSer(self) :

        event.wait()
        
        countre = 0

        while self.cap.isOpened() : 

            self.TimeButtonKey = self.waitkey & self.KEYBOARD == ord('x')
            self.TimeButtonReadKey = self.waitkey & self.KEYBOARD == ord('r') 

            if self.TimeButtonReadKey or self.LoopSerialSend : self.Time_Date_Read()

            if self.TimeButtonKey or self.LoopSerialSend : 
                for objectNameOut in self.classNames : 
                    if objectNameOut == self.objectName : 
                        self.send = self.objectName[0] 
                if self.CONTROL_KEYBOARD : # süreler bulunmak istendiğinde kullanılır
                    if countre == 1  : # Servo motor kapanır ve step motor durur
                        self.send = "g"
                        self.lasTime = time()
                        self.Time_Date_Write()
                        if self.Embedded_Systeam_Search == "Arduino" : self.SerialDate() # serial veri ile gönderiliyor.
                        else : self.PLC_Socket()
                        countre = 0
                        self.logger.info("Keyboard Send : {0}".format(self.send))
                        sleep(self.buttonSleep)
                        continue
                    if countre == 0 and self.HeightandWidht : # Servo açılır ve step motor harekete geçer
                        self.send = self.objectName[0]
                        self.Time = time()#buttona birinci kez basıldığında
                        if self.Embedded_Systeam_Search == "Arduino" : self.SerialDate() # serial veri ile gönderiliyor.
                        else : self.PLC_Socket()
                        countre = countre + 1
                        self.logger.info("Keyboard Send : {0}".format(self.send))
                        sleep(self.buttonSleep)
                        continue
                else : # Proje tam olarak bittiğinde çalışması gereken
                    if self.HeightandWidht :
                        self.send = self.objectName[0]
                        if self.Embedded_Systeam_Search == "Arduino" : self.SerialDate() # serial veri ile gönderiliyor.
                        else : self.PLC_Socket()
                        self.logger.info("Keyboard Send : {0}".format(self.send))
                        sleep(self.buttonSleep)
                        continue
            if self.LoopSerialSend == 1 :
                self.send = self.objectName[0]
                if self.Embedded_Systeam_Search == "Arduino" : self.SerialDate() # serial veri ile gönderiliyor.
                else : self.PLC_Socket()
                sleep(self.buttonSleep)
            
            sleep(self.sleepLoop)

    def SerialDate(self) : # Serial haberleşme için kullanılır.
        byteSend = self.send.encode('UTF-8')# Gönderilecek komutu byte türüne dönüştürüyor
        self.sr.write(byteSend) # Komut gönderiliyor.
        while self.sr.is_open : 
            recv = self.sr.readline().decode().strip() # Gönderilen komuta karşılık gelecek komut bekleniyor .
            if recv == "OK{0}".format(self.send):
                self.sr.flush()# port boşaltılıyor
                break
            sleep(self.sleepLoop)

    def PLC_Socket(self,Try = None) :
        def plc_recv_thread():
            while self.plc_step == 2 :
                try:
                    recv = self.client.read_holding_registers(0, 3)
                    if not recv : continue
                    else :
                        if recv[2] == 1 :
                            #send = ("plc_recv" + "/" + "#Abs5") 
                            #self.server_socket.sendall(send.encode('utf-8'))
                            self.logger.info(f"Feedback recv : {recv}")
                            self.plc_send[2] = 0
                            self.plc_step = 0
                            break
                except Exception as e : self.logger.warning(f"PLC read error : {e}")

        threading_recv = Thread(target=plc_recv_thread)

        try : # send

            rand = randint(0,100) # it is a create number random

            if self.plc_last_rand != rand : # rand diff

                if self.plc_step == 0 and self.plc_send[2] == 0 : # step control

                    if Try : self.plc_send_value = int(input(" send : ")) # typ control
                    else :
                        # it will a send the value
                        if self.plc_send_value != None : 

                            self.plc_send[0] = ord(str(self.plc_send_value).strip())
                            self.plc_send[1] = rand
                            
                            # it is send data a lot  
                            result = self.client.write_multiple_registers(self.PLC_register_Adress,self.plc_send) 
                            
                            # it is step processing 
                            self.plc_step = 2 
                 
                    if result :
                        #socket_send = ("plc_send" + "/" + "#Abs5") 
                        #self.server_socket.sendall(socket_send.encode('utf-8'))
                        self.plc_last_rand = rand 
                        self.logger.info(f"Data is send : {str(self.plc_send)}", )
                        threading_recv.start()

                self.plc_last_rand = rand # it is together new data with last data

        except Warning as e : self.logger.warning(f" Send is create error block : {e}")

    def Time_Date_Write(self) : # LOG dosyasına zaman bilgileri yazılır 
        file = open(self.pathLog, 'a') # YAZILAN VERİLERİN SİLİNMEMESİ İÇİN KULLANILIR
        diffTime = round(abs(self.Time - self.lasTime),3)
        text = str(diffTime)
        file.write(text + "\n")
        file.close()

    def Time_Date_Read(self) : # LOG dosyasındaki zaman bilgileri işlemek için kullanılır 
        countre2 = 0
        ort2 = 0
        file = open(self.pathLog,'r')
        for outNumber in file.readlines() :
            byteOutNumber = outNumber.encode('UTF-8')
            if byteOutNumber != b'\n' :
                countre2=countre2+1
                floatToConvertNumber = float(byteOutNumber)
                ort2 = ort2 + floatToConvertNumber
        if(countre2!=0) : ort2 = round(ort2/countre2,3)
        file.close()

    def list_serial_ports(self): # Serial portlar bulunuyor 
        ports = comports() # portlar okunuyor
        port_list = [] # port bilgileri listeleniyor
        for port in ports:
            port_info = {
                'device': port.device,
                'name': port.name,
                'description': port.description,
                'hwid': port.hwid,
                'vid': hex(port.vid),
                'pid': hex(port.pid),
                'serial_number': port.serial_number,
                'location': port.location,
                'manufacturer': port.manufacturer,
                'product': port.product,
            }
            portDescription = str(port_info['description'])
            DeviceDesctiption = portDescription.split(' ')[1]
            if DeviceDesctiption == "CH340" : port_list.append(port_info)
        port_list_splite = loads(dumps(port_list[0]))
        return port_list_splite

    def Memory_chech(self) : 
        event.wait()
        while True : 
            collect() # Bellek boşaltılabilir
            sleep(self.Memory_chech_sleep) # Bekleme işlemi

    def Threading(self) :

        self.ThredingYolov = Thread(target=self.YolovCameraObjectDetection,daemon=True)# yolov8 yapay zeka
        self.ThreadingButton = Thread(target=self.OpencvKeyControlSer,daemon=True)# button kontrol 
        self.ThreadingCameraRecv = Thread(target=self.CameraRecv)# camera kontrol
        self.ThreadingMemory = Thread(target=self.Memory_chech,daemon=True) # Bellek temizleme yapılıyor
        self.ThreadingSocket = Thread(target=self.Socket_Send_Recv_Send,daemon=True)
        self.ThreadingSerialControl = Thread(target=self.SysteamFeedback,daemon=True)

        self.ThreadingCameraRecv.start()
        
        if event.is_set() : # tetikleme sonucunda çalışan diğer çekirdek işlemleri 

            self.ThredingYolov.start()
            self.ThreadingButton.start()
            self.ThreadingMemory.start()
            self.ThreadingSocket.start()
            self.ThreadingSerialControl.start()
            
            self.ThreadingCameraRecv.join()
            self.ThredingYolov.join()
            self.ThreadingButton.join()
            self.ThreadingMemory.join()
            self.ThreadingSocket.join()
            self.ThreadingSerialControl.join()
    
        self.logger.info("ÇEKİRDEKLERE GÖREV AKTARILDI")

cv2.destroyAllWindows()


