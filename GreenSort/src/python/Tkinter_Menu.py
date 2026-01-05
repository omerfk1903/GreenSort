from Yolov8WithObjectsDetections import Thread,sleep,current_thread,sc,name,exists,collect,getcwd
from cv2 import INTER_AREA,resize,cvtColor,COLOR_BGR2RGB,VideoCapture,CAP_PROP_POS_FRAMES
from PIL import Image, ImageTk
from datetime import datetime as dt
from tkinter import messagebox
from struct import calcsize
from logger import setup_logger
import tkinter as tk

class tkinter_Menu : 

    def __init__(self) : 

        CMD_CONTROL = 1 # Komut satırın kapanması yada açık kalmasını kontrol eder.

        self.passSend = ["#34/","#53/"] # Serial haberleşmede gelen komutların görevlerini sifreli kodlara göre ayrılıyor
        self.cnts = 0

        self.HOST = "localhost"  # Sunucu adresi
        self.PORT = 8000  # Sunucu portu
        
        self.Button_Recv_state = False # Veri alma butonu 
        self.Button_Send_state = False # ver gönderme butonu
        self.Button_Systeam_Break_state = False 
        self.buttonThreading_sleep = 0.05

        # Mikrodenetleyici seçimi yapılıyor
        self.ButtonSerialControl = False
        self.ButtonPlcControl = True

        self.data = b""
        self.payload_size = calcsize("Q") 

        self.MinFilePath = getcwd()# Dosya konumu alınıyor.

        # Logger başlatılıyor
        self.logger = setup_logger(txt="Tkinter")

        #------------ WİNDOWS CMD CLOSE -----------#
        if CMD_CONTROL and name == "nt" : # CMD komut satırını gizlemek için kullanılır 
            from win32console import GetConsoleWindow
            from win32gui import ShowWindow
            win = GetConsoleWindow() 
            ShowWindow(win, 0)
            self.logger.info("OS : Windows")
        
        #------------ LİNUX CMD CLOSE -------------#
        if not CMD_CONTROL and name != "nt" :
            from subprocess import Popen # linux 
            #Popen('shutdown','now') # linux komut satırını kapatmak
            self.logger.info("OS : Linux")
        
        #-------------- PATH ---------------------#
        self.windowsBack =  self.MinFilePath + "\\img\\Arka_Plan.png"
        self.iconPath = self.MinFilePath + "\\img\\826963.ico"

        #---------- Windows -----------------------#
        kat = 2/3
        widht = 800
        height = int(widht * kat)
        self.window = tk.Tk() # Menü oluşturuluyor
        self.window.geometry(f"{widht}x{height}") # Menü boyutu ayarlanıyor
        self.window.title("Control System") # Uygulamamının ismi ekleniyor
        if exists(self.iconPath) : self.window.iconbitmap(default=self.iconPath)# uygulamaya icon ekleniyor
        else : self.logger.warning("İcon is not found galery")
        
        # ----------------- Background galery add ---------------#
        self.canvas = tk.Canvas(self.window,width=widht,height=height)
        self.image = ImageTk.PhotoImage(Image.open(self.windowsBack).resize((widht,height)))
        self.canvas.create_image(0,0,anchor=tk.NW,image=self.image)
        self.canvas.pack()
        
        #----------- Widget -------------------------#
        self.Systeam_Break_Button = tk.Button(self.window,text="Break",background="black",fg="blue",height=5,width=10,command=self.Button_Systeam_Break_State)
        self.Recv_button          = tk.Button(self.window,text="Read",background="black",fg="red",height=5,width=10,command=self.Button_Recv_State)
        self.Send_button          = tk.Button(self.window,text="Send",background="black",fg="green",height=5,width=10,command=self.Button_Send_State)
        self.Socket_Open_Close    = tk.Button(self.window,text="socket",command=self.socketBind)
        self.Button               = tk.Button(self.window,text="Camera",background="black",fg="yellow",width=10,height=5,command=self.Recv_Camera)
        self.Systeam_Micro_Data   = tk.Button(self.window,text="Micro_Data",command=self.SerialControl)
        self.Screen               = tk.Label(self.window) # Görüntüyü aktaracak
        self.listbox              = tk.Listbox(self.window) # Anlık işlemler aktarılıyor 
        self.entr                 = tk.Entry(self.window,width=20) # Girdi
        self.scrollbar            = tk.Scrollbar(self.window,orient=tk.VERTICAL,command=self.listbox.yview)#listbox hareketlendirme

        #-------------- Config -----------------------#
        self.Button.config(state="disabled") # Buttonu disable olarak çalıştırılıyor
        self.Screen.config(text="GÖRÜNTÜ GELMİYOR")
        self.listbox.config(state="disabled",width=26,height=28,background="black",fg="green",yscrollcommand=self.scrollbar.set)
        self.Systeam_Micro_Data.config(state="disabled")
        
        # ------------------- BUTTON ---------------#
        self.Recv_button.place(x=10,y=10)
        self.Send_button.place(x=110,y=10)
        self.Systeam_Break_Button.place(x=10,y=110)
        self.Socket_Open_Close.place(x=120,y=210)
        self.Button.place(x=110,y=110)
        self.Systeam_Micro_Data.place(x=40,y=210)

        # ------------------- DİĞERLERİ -------------#
        self.Screen.place(x=205,y=10)
        self.listbox.place(x=620,y=10)
        self.entr.place(x=50,y=260)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        #-------------- ÇEKİRDEK ---------------------#
        self.MemoryControl = Thread(target=self.Memory_chech) # Bellek boşaltma fonksiyonu
        #self.cmr = Thread(target=self.Socket_Recv_Camera) # Görüntü menüye aktarılıyor

    def socketBind(self) : 
        while not self.cnts : # Socket bağlantısının durumuna göre 
            try :
                self.client_socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
                self.client_socket.setsockopt(sc.SOL_SOCKET,sc.SO_REUSEADDR, 1)
                self.listbox.insert(tk.END,f"PORT : {self.PORT} Connect 1")
                self.listbox.yview_moveto(1)# listbox hareketlendirme 
                self.cnts = not self.cnts
                self.Socket_Recv_Camera() # kamera gönrüntüsü aktarılıyor
                if self.Systeam_Micro_Data.cget("state") == "disabled" : self.Systeam_Micro_Data.config(state="normal")
            except (sc.timeout,sc.error) :
                self.listbox.insert(tk.END,f" PORT : {self.PORT} Disconnect 1 ")
                self.listbox.yview_moveto(1)
                if self.Systeam_Micro_Data.cget("state") == "normal" : self.Systeam_Micro_Data.config(state="disabled")
        try : 
            self.entrRecvstr = self.entr.get()
            self.entRecvint = int(self.entrRecvstr)# entry girilen veri int formatına dönüştürülür
            self.InputLen = len([int(x)for x in str(self.entrRecvstr)]) # Girilen veriyi parçalara ayırı
            if self.InputLen == 4 : self.client_socket.connect((self.HOST, self.entRecvint))
            while True : 
                if self.client_socket.getpeername() != " " :
                    print(f"Address : {self.client_socket.getpeername()} Name : {self.client_socket.getsockname} HOST CONNECT") 
                    break
            self.Button.config(state="normal")
            self.listbox.config(state="normal")
            self.Button_Visiable(True)
            self.Socket_Recv_Camera()
            self.listbox.insert(tk.END,f" | PORT : {self.PORT} CONNECT ")
            self.listbox.yview_moveto(1)
        except : 
            countre = 0
            while True : 
                try : 
                    if self.client_socket.getpeername() != " " :
                        self.logger.info(f"Address : {self.client_socket.getpeername()} Name : {self.client_socket.getsockname} HOST CONNECT")
                        break
                except : 
                    countre = countre + 1
                    self.logger.warning("HOST DİSCONNECT ...")
                    if countre == 3 : 
                        self.logger.warning("Connect is not was setup with at server ")
                        self.listbox.insert(tk.END,f" PORT : {self.PORT} Disconnect 1 ")
                        self.listbox.yview_moveto(1)
                        break
            self.Button_Visiable(False)
            self.Socket_Open_Close.config(state="normal")
            self.cnts = not self.cnts

    def SerialControl(self) : # Serial durumuna göre buttonların kontrolü
        def Threading() : 
            try : 
                while True : 
                    recv = self.client_socket.recv(10)
                    recvdecode = recv.decode('utf-8')
                    recvSplite = recvdecode.split('/')
                    recvCode = recvSplite[1] 
                    data = recvSplite[0]
                    if recvCode == "#Ab1" : 
                        if data == "True" : self.ButtonSerialControl = True
                        else : self.ButtonSerialControl = False
                        self.listbox.insert(tk.END,f"SR DURUM : {data}")
                        self.listbox.yview_moveto(1)
                    elif recvCode == "#Ab2" :
                        self.listbox.insert(tk.END,f"Servo : {data}")
                        self.listbox.yview_moveto(1)
                    elif recvCode == "#Ab3" : 
                        self.listbox.insert(tk.END,f"Band durumu : {data}")
                        self.listbox.yview_moveto(1)
                    elif recvCode == "#Abs5" : # plc için komut gidip gitmedigi kontrol ediliyor.
                        data_splite = data.split('_')[1]
                        if data_splite == "send" :
                            self.listbox.insert(tk.END,f"Band is send value : {data}")
                            self.Send_button.config(state="disabled")
                        if data_splite == "recv" :
                            self.listbox.insert(tk.END,f"Band is recv value : {data}")
                            self.Send_button.config(state="active")
                        self.listbox.yview_moveto(1)
                    else : pass
            except : 
                self.listbox.insert(tk.END,"Socket Disconnect")
                self.listbox.yview_moveto(1)
        ThreadStart = Thread(target=Threading)
        ThreadStart.start()
        ThreadStart.join()
        self.window.update()

    def Memory_chech(self) :
        while True : 
            collect() # Bellek boşaltılabilir
            self.listbox.insert(tk.END,"MemoryClear")
            self.listbox.yview_moveto(1)
            sleep(5)

    def Socket_Recv_Camera(self) : # Alınan kamera görüntüsü menüye ekleniyor
        try : 
            framePath = f"{self.MinFilePath}\\img\\Image 2023-12-17 17-13-55.mp4"
            if exists(framePath) : # OPENCV -> PIL_IMAGE -> TKİNTER Dönüştürme işlemidir 
                self.cap = VideoCapture(framePath)
                def update_frame() :
                    ret,frame = self.cap.read()
                    if ret :
                        screenHeight = int(frame.shape[0]/2)# Yükseklik
                        screenWidht= int(frame.shape[1]/2)# Genişlik
                        frame = resize(frame,(screenWidht,screenHeight),interpolation=INTER_AREA)# Görüntünün boyutu ayarlanıyor
                        cv2image = cvtColor(frame, COLOR_BGR2RGB) # Video RGB formatına dönüştürülüyor.
                        img = Image.fromarray(cv2image) # video sayısal verileri dizi haline dönüştürülüyor.
                        imgtk = ImageTk.PhotoImage(image=img) # dizi halindeki veriler resim formatına dönüştürülüyor
                        self.Screen.imgtk = imgtk # Screen etiketine video ekleme 
                        self.Screen.configure(image=imgtk,width=screenWidht,height=screenHeight)# Video ekleme ve boyut ayarlama 
                        self.Screen.after(10, update_frame)# ideo yenileme süresi 
                    else : 
                        self.cap.set(CAP_PROP_POS_FRAMES,0)# Video başlangıcında başlamasına yarıyor
                        update_frame()
                update_frame()
            else : self.Screen.config(text="RESME ULAŞILAMADI")
        except : self.Screen.config(text="HATA VERDİ GÖRÜNTÜ GELMİYOR") 
  
    def Recv_Camera(self) : 
        self.Button.config(state="disabled")
        #self.cmr.start()

    def Button_Recv_State(self):# VERİ OKUMA 
        def threading() :
            try : 
                self.Button_Recv_state = not self.Button_Recv_state
                if (self.Button_Recv_state != (not self.Button_Recv_state)) and self.client_socket.getpeername() != " " :
                    print(f"Button_Recv : {current_thread().name}")
                    send = self.passSend[0] + "G"
                    self.client_socket.sendall(send.encode('utf-8'))
                    self.listbox.insert(tk.END,send + " " + str(dt.now().date()))
                    self.listbox.yview_moveto(1)              
                sleep(self.buttonThreading_sleep)
            except : 
                self.Socket_Open_Close.config(state="normal")
                self.Button_Visiable(False)
        thr = Thread(target=threading)
        thr.start()
        self.window.update()

    def Button_Send_State(self):# VERİ GÖNDERME 
        def threading() :
            try : 
                self.Button_Send_state = not self.Button_Send_state
                if (self.Button_Send_state != (not self.Button_Send_state)) and self.client_socket.getpeername() != " " : 
                    self.logger.info(f"Button_Send : {current_thread().name}")
                    send = self.passSend[0] + "A"
                    self.client_socket.sendall(send.encode('utf-8'))
                    self.listbox.insert(tk.END,send + " " + str(dt.now().date()))
                    self.listbox.yview_moveto(1)
                sleep(self.buttonThreading_sleep)
            except : 
                self.Socket_Open_Close.config(state="normal")
                self.Button_Visiable(False)
        thr = Thread(target=threading)
        thr.start()
        self.window.update()

    def Button_Systeam_Break_State(self): # SİSTEMİ DURDURMA VE BAŞLATMA 
        def threading() :
            try : 
                self.Button_Systeam_Break_state = (not self.Button_Systeam_Break_state)
                if (self.Button_Systeam_Break_state != (not self.Button_Systeam_Break_state)) and self.client_socket.getpeername() != " " :
                    self.logger.info(f"Button_Break state : {current_thread().name} ")
                    send = self.passSend[0] + "B"
                    self.client_socket.sendall(send.encode('utf-8'))
                    self.listbox.insert(tk.END,send + " " + str(dt.now().date()))
                    self.listbox.yview_moveto(1)
                sleep(self.buttonThreading_sleep)
            except : 
                self.Socket_Open_Close.config(state="normal")
                self.Button_Visiable(False)
        thr = Thread(target=threading)
        thr.start()
        self.window.update()

    def Button_Visiable(self,control) : # Buttonun durumuna göre durumunu değiştirme
        if control == False and (self.ButtonSerialControl and self.ButtonPlcControl) == False : 
            control = "disabled"
            if self.Recv_button.cget("state") == "normal" : 
                self.Recv_button.config(state=control)
            if self.Systeam_Break_Button.cget("state") == "normal": 
                self.Systeam_Break_Button.config(state=control)
            if self.Send_button.cget("state") == "normal" : 
                self.Send_button.config(state=control)
        if control == True and (self.ButtonSerialControl or self.ButtonPlcControl) == True :  
            control = "normal"
            if self.Recv_button.cget("state") == "disabled" : 
                self.Recv_button.config(state="disabled")
            if self.Systeam_Break_Button.cget("state") == "disabled": 
                self.Systeam_Break_Button.config(state=control)
            if self.Send_button.cget("state") == "disabled" : 
                self.Send_button.config(state=control)

    def socketClose(self) : 
        self.client_socket.close()
        messagebox.showinfo(message=" port disconnect ")
        self.listbox.insert(tk.END,f"PORT : {self.PORT} DİSCONNECT")
        self.listbox.yview_moveto(1)
        self.Button_Visiable(False)
        self.listbox.config(state="disabled")

    def Tkinter(self) :
        self.Button_Visiable(False) # Button durumu 
        self.MemoryControl.start() # Bellek temizleme 
        self.window.mainloop() # Menü yenileme 
