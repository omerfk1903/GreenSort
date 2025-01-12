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
from threading import Thread,Event,current_thread# Çekirdek kontrol 
from gc import collect # Bellek temizleme işlemi

class Yolov8 :

    def __init__(self,FunchControl,Socket_Camera_Send,baudrate,write_timeout,timeout,LoopSerialSend,Memory_chech_sleep,CMD_Control,Tolerans,distance,CONTROL_KEYBOARD,ScreanSize,ToleransWeightControl,ScreenControl,ToleransMiddle,buttonSleep,sleepLoop) :

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

        HOST = "localhost"  # Sunucu adresi
        PORT = 8000  # Sunucu portu
        
        self.send = None
        self.lasSend = None
        self.KEYBOARD = 0xFF
        self.vertices = array([[(75, 525), (440, 320), (520, 330), (920, 525)]], int32)  # köşeler
     
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
    
        if self.CMD_Control and name == "nt" : # CMD komut satırını gizlemek için kullanılır 
            from win32console import GetConsoleWindow
            from win32gui import ShowWindow
            win = GetConsoleWindow() 
            ShowWindow(win, 0)
            print("OS : WİNDOWS ")

        if not self.CMD_Control and name != "nt" :
            from subprocess import Popen # linux 
            Popen('shutdown','now') # linux komut satırını kapatmak
            print("OS : LİNUX")
        
        # For camera
        try : 
            self.cap = cv2.VideoCapture(0)
            print("KAMERAYA ERİŞİLDİ")
        except : print("KAMERAYA ERİŞİLEMEDİ")

        # Yapay zeka kontrol 
        try : 
            self.model = YOLO(self.Path2)
            print("MODEL HAZIR")
        except : print("YOLOV 8 MODELİ BULUNAMADI YADA FARKLI BİR HATAYLA KARŞILAŞILDI ")
    
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
                print("CPU EKRAN KARTI ÖZELLİKLERİ AKTİF ")
            except : print("CPU OPTİMİZESİ ÇALIŞTIRILAMADI ")
        else : print("GPU EKRAN KARTI AKTİF")

        #Port = self.list_serial_ports()['name'] #Port ismi 
        #if len(Port) == 0 : print(" PORT YOK ") 
        try: # Serial iletişim başlatılması ve ayarlanması için kullanılır
            self.sr = Serial()
            self.sr.baudrate = baudrate
            self.sr.timeout = timeout
            #self.sr.write_timeout = write_timeout
            #self.sr.port = Port #Port ismi 
            self.sr.port = self.list_serial_ports()
            self.sr.open()
            self.sr.flush()
            if self.sr.is_open : 
                print("SERİAL CONNECT ")
                print("ARDUİNO COM : {0}".format(self.sr.port))
            else : 
                print("SERİAL DİSCONNECT ")
                print("ARDUİNO COM : {0}".format(self.sr.port))
        except : 
            print("SERİAL DİSCONNET")
            print("ARDUİNO COM : {0}".format(self.sr.port))
        
        try : 
            # Socket iletişimi başlatılıyor
            self.server_socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
            self.server_socket.bind((HOST, PORT))
            self.server_socket.listen(5)
            print("SOCKET OLUŞTURULDU ")
        except : 
            print("SOCKET OLUŞTURULAMADI ")
        
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

        print("Cut processing : Y : {0} | X : {1} ".format(self.Ycmdistance,self.Xcmdistance))

        # Parçalanan görüntünün boyut bilgisi alınıyor 
        self.imgSplite = self.imgCopy[self.Ycmdistance:self.Ycmdistance + (self.height - self.Ycmdistance),
        self.Objectİmportent:self.Objectİmportent + abs(self.Objectİmportent2 - self.Objectİmportent)]
        (self.height, self.widht) = self.imgSplite.shape[:2] # Video boyutu alınıyor
        self.height = int(self.height)
        self.widht = int(self.widht)
        
        print("Height : {0} | Widht : {1} ".format(self.height,self.widht))

        self.waitkey = cv2.waitKeyEx(0) 
        self.Key = self.waitkey & self.KEYBOARD == ord('q') # Key
        self.TimeButtonKey = self.waitkey & self.KEYBOARD == ord('x') # Time write and systeam control
        self.TimeButtonReadKey = self.waitkey & self.KEYBOARD == ord('r')

        print(" Use Grapich Card : {0} ".format(self.Use_Grapich_card))

        if exists(self.Path2) : print("This {0}  file found ".format(self.pathSplite[self.pathSpliteLen - 1]))
        else : print("This {0}  file not found ".format(self.pathSplite[self.pathSpliteLen - 1]))
        
        # Başlangıç öncesi işlem 
        print("5 second wait ")
        for x in range(0,5) : 
            sleep(1)
            print(str(x + 1) + "..." )
        print("Device ready the start")

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
            while True :
                send = (str(self.sr.is_open) + "/" + passCode[0]) # Serial haberleşme 
                self.server_socket.sendall(send.encode('utf-8'))
                sleep(0.5)
                send = (str(servok) + "/" + passCode[1]) # Servonun konumu
                self.server_socket.sendall(send.encode('utf-8'))
                sleep(0.5)
                send = (str(bandB) + "/" + passCode[2]) # bandın hareket durumu
                self.server_socket.sendall(send.encode('utf-8'))
                sleep(0.5)
        except sc.error as e : print(f"Socket bağlantı hatası : {e}")

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
        def handle_client(client_socket,address):
            event.wait()
            global dataDecode
            while self.sr.is_open :
                try : 
                    data = client_socket.recv(10)  # 10 byte veri okuma
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
                        else : self.SerialDate() 
                    else : continue
                except sc.error or sc.timeout or ConnectionRefusedError or sc.gaierror : 
                    if countreSocket == 3 : break # 3 kere socket hatası deneniyor
                    countreSocket = countreSocket + 1 
                    continue # Bir sorun ile karşılaşılır ise programı kapatır.
                sleep(self.sleepLoop)
        #while self.sr.is_open :
        client_socket, address = self.server_socket.accept() 
        client_thread = Thread(target=handle_client, args=(client_socket,address,))
        client_thread.start()

    def YolovCameraObjectDetection(self) :

        event.wait()

        while self.cap.isOpened() :

            self.new_frame_time = time()
            
            results = self.model(self.imgSplite, stream=False)

            for r in results:
                boxes = r.boxes
                for box in boxes:

                    x1, y1, x2, y2 = box.xyxy[0]
                    self.x1, self.y1, self.x2, self.y2 = int(x1), int(y1), int(x2), int(y2)
                    
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
                    else : print("TOLERANS YOKTUR")

                    w = abs(int(self.x2 - self.x1))
                    h = abs(int(self.y2 - self.y1))

                    #cismin ortası
                    self.middleX = self.x1 + int(w / 2)
                    self.middleY = self.y1 + int(h / 2)
                           
                    #ekranın ortası
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
                        self.SerialDate()
                        countre = 0
                        print(" send : {0} ".format(self.send))
                        sleep(self.buttonSleep)
                        continue
                    if countre == 0 and self.HeightandWidht : # Servo açılır ve step motor harekete geçer
                        self.send = self.objectName[0]
                        self.Time = time()#buttona birinci kez basıldığında
                        self.SerialDate()
                        countre = countre + 1
                        print(" send : {0} ".format(self.send))
                        sleep(self.buttonSleep)
                        continue
                else : # Proje tam olarak bittiğinde çalışması gereken
                    if self.HeightandWidht :
                        self.send = self.objectName[0]
                        self.SerialDate()
                        print(" send : {0} ".format(self.send))
                        sleep(self.buttonSleep)
                        continue
            if self.LoopSerialSend == 1 :
                self.send = self.objectName[0]
                self.SerialDate()
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
        if(countre2!=0) : 
            ort2 = round(ort2/countre2,3)
            print(" veri ortalaması : {0}".format(ort2))
        else : print(" veri yok ")
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
    
        print("ÇEKİRDEKLERE GÖREV AKTARILDI")

cv2.destroyAllWindows()