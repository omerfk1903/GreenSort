#define SEARCH 1
#define SRP 1

//Timer kütüphanesi
#include<Timer.h>

//Servo kütüphanesi
#include<Servo.h>

//TİMER TANIMLAMASI
Timer time1;

//Servo tanımlama
Servo myServo1;
Servo myServo2;
Servo myServo3;
Servo myServo4;

#define rolePin 8
#define LED 13

//Step motor pin tanımlamaları
#define DirectionPin 6
#define MotorMovePin 9

//Servoların güç kontrol pinleri
#define ServoRightPowerControl 10
#define ServoLeftPowerControl 11

//Tanımlamalar
int harfint[7] = {65, 80, 112, 71, 103, 121, 89};//gelen char tiplerinin int formatları

//SERVO MOTOR KONTROL FONKSİYONLARI
void ServoControl(int control, int duraction);
void ServoDirection(int ServoLeft1, int ServoLeft2, int ServoRight1, int ServoRight2, int duraction);
void ServoSpeedControl(Servo servo, int targetAngle, int duration);

//MOTOR KONTROL FONKSİYONLARI
void MotorControl(float tls, int control);
void MotorWork(bool control, String search);

//LED DENEME FONKSİYONU
void LED_CONTROL(short sleep, int countre);

//MAİN FONKSİYON
void Start();

void setup() {
  //------ SERİAL HABERLEŞME ----- //
  Serial.begin(19200);//Serial haberleşme başlatılıyor
  Serial.setTimeout(1000);//Serial haberleşme arasında 1 sn boşluk kaldığında boş değer verir
  Serial.flush();//Serial haberleşme portunu boşaltma
  while (!Serial) {
    ;
  }
  //------- ÇIKIŞLAR -------- //
  pinMode(LED, OUTPUT); // Led giriş çıkış ayarlanıyor
  pinMode(rolePin, OUTPUT); // Role tetikleme pini çıkış olarak ayarlandı.
  pinMode(ServoLeftPowerControl, OUTPUT); //Servo güç giriş pini.LeftServo.
  pinMode(ServoRightPowerControl, OUTPUT); //Servo güç giriş pini.RightServo.

  MotorWork(false, "MOTOR"); //Motor Durduruluyor
  LED_CONTROL(250, 1);
  //------------ 1.SERVO AKTİF ---------------
  digitalWrite(ServoLeftPowerControl, LOW);
  delay(100);
  myServo2.attach(3);
  myServo2.write(180);//Başlangıç konumları servolara iletiliyor
  delay(250);
  //------------ 2.SERVO AKTİF ---------------
  digitalWrite(ServoRightPowerControl, LOW);
  delay(100);
  myServo3.attach(4);
  myServo3.write(0);//Başlangıç konumları servolara iletiliyor
  delay(250);
  // ------------ LED DURDURULUYOR -----------
  MotorWork(false, "LED"); //led Kapatılıyor
}

void loop() {
  switch (SEARCH) { // Projenin çalışması için start fonksiyonu çalıştırılması gereklidir.Diğer case'ler projenin özelliklerin kontrolü için kullanılır
    case 1 :
      Start();
      break;
    case 2 :
      ServoDirection(0, 180, 50, 0, 500);
      break;
    case 5 :
      MotorWork(true, "MOTOR");
      delay(3000);
      MotorWork(false, "MOTOR");
      delay(3000);
      break;
    case 6 :
      for (int a = 0; a < 6; a++) {
        int c = harfint[a];
        Serial.println(" a: " + String(c) + " : ");
        MotorControl(3, c);
      }
      break;
  }
}
