import tkinter as tk
from subprocess import Popen,CalledProcessError
from os import getcwd 
from threading import Thread

class GreenSortStartClass :     
    def __init__(self) :
        self.TryControl = 1 # Bilgisayarda kullanılıp kullanılmayacağını belirler 
        self.AppCnt = 1 # Butonların çalışıp çalışmadığı kontrol edilir.

        # Menü
        self.window = tk.Tk() 
        self.window.geometry("450x150") 
        self.window.title("GreenSort") 

        # Dosya konumu
        self.file = getcwd()

        # Çalıştırılacak kodların cmd komutları
        self.cmd1Command = ["cmd.exe","/k",f"python {self.file}\\src\\python\\Yolov8Control.py"]
        self.cmd2Command = ["cmd.exe","/k",f"python {self.file}\\src\\python\\TkControl.py "]

        # label 
        self.Text_1 = tk.Label(self.window,text="APP START",font=("Arial",16),fg="Black")

        # Menü'nün Buton oluşturma 
        self.GreenSort_Start = tk.Button(self.window,text="GrenSortStart",background="Red",height=5,width=15,command=self.start1)
        self.Tkinter_cnt = tk.Button(self.window,text="TkinterMenu",background="green",height=5,width=15,command=self.start2)
        self.Yolov8_cnt = tk.Button(self.window,text="Yolov8",background="yellow",height=5,width=15,command=self.start3)

        # Widgetlerin konumları belirleniyor
        self.GreenSort_Start.place(x=10,y=50)
        self.Tkinter_cnt.place(x=150,y=50)
        self.Yolov8_cnt.place(x=290,y=50)
        self.Text_1.place(x=150,y=10)

    def start1(self) : # mod 1
        def threading() : 
            try : 
                self.cmd1 = Popen(self.cmd1Command,shell=True)
                self.cmd2 = Popen(self.cmd2Command,shell=True)
                self.cmd1.wait()
                self.cmd2.wait()
                if self.GreenSort_Start.cget("state") == "normal" : self.GreenSort_Start.config(state="disabled")
                if self.Tkinter_cnt.cget("state") == "normal" : self.Tkinter_cnt.config(state="disabled")
                if self.Yolov8_cnt.cget("state") == "normal" : self.Yolov8_cnt.config(state="disabled")
            except CalledProcessError as e:
                # Komut sırasında hata oluşursa
                print("Hata: Program çalıştırılırken bir sorun oluştu.")
                print("Hata mesajı:", e.stderr)

            except FileNotFoundError:
                # Program bulunamadıysa
                print("Hata: Çalıştırılmak istenen program bulunamadı.")

            except Exception as e:
                # Diğer bilinmeyen hatalar
                print(f"Bilinmeyen bir hata oluştu: {e}")
        thread = Thread(target=threading)
        thread.start()
        thread.join()
        self.window.update()

    def start2(self) : # mod 2
        def threading():
            try : 
                self.cmd = Popen(self.cmd2Command,shell=True)
                self.cmd.wait()
                if self.Tkinter_cnt.cget("state") == "normal" : self.Tkinter_cnt.config(state="disabled")
                if self.GreenSort_Start.cget("state") == "normal" : self.GreenSort_Start.config(state="disabled")
            except CalledProcessError as e:
                # Komut sırasında hata oluşursa
                print("Hata: Program çalıştırılırken bir sorun oluştu.")
                print("Hata mesajı:", e.stderr)
    
            except FileNotFoundError:
                # Program bulunamadıysa
                print("Hata: Çalıştırılmak istenen program bulunamadı.")

            except Exception as e:
                # Diğer bilinmeyen hatalar
                print(f"Bilinmeyen bir hata oluştu: {e}")
        thread = Thread(target=threading)
        thread.start()
        thread.join()
        self.window.update()

    def start3(self) :  # mod 3
        def threading() : 
            try :
                self.cmd = Popen(self.cmd1Command,shell=True)
                self.cmd.wait()
                if self.Yolov8_cnt.cget("state") == "normal" : self.Yolov8_cnt.config(state="disabled")
                if self.GreenSort_Start.cget("state") == "normal" : self.GreenSort_Start.config(state="disabled")
            except CalledProcessError as e:
                # Komut sırasında hata oluşursa
                print("Hata: Program çalıştırılırken bir sorun oluştu.")
                print("Hata mesajı:", e.stderr)

            except FileNotFoundError:
                # Program bulunamadıysa
                print("Hata: Çalıştırılmak istenen program bulunamadı.")

            except Exception as e:
                # Diğer bilinmeyen hatalar
                print(f"Bilinmeyen bir hata oluştu: {e}")
        thread = Thread(target=threading)
        thread.start()
        thread.join()
        self.window.update()

    def update(self) : # Menü sürekli yenilemek için kullanılır .
        self.window.mainloop()

GSSC = GreenSortStartClass()

if __name__ == "__main__" : 

    GSSC.update()
