void Start() {
  static int recv_int, tls = 0;
  static char recv_char;
  tls = 2;
  while (Serial.available() == 1) { 
    recv_char = Serial.read();
    recv_int = int(recv_char);//char tipi veriyi int türüne dönüştürüyor
    if (recv_int == 121 or recv_int == 89)break;
    for (int t = 0; t < 5; t++) {
      if (recv_int == harfint[t]) { //gelen komutun kontrolü
        if (recv_int != 65)ServoControl(recv_int, 10); // Servo kolu açılıyor
        delay(250);
        if(recv_int != 71)MotorControl(tls, recv_int); // Tolerans,Giriş verisi
        delay(250);
        recv_int = 103; // Servo kolunu kapatma kodu
        if (recv_int != 65)ServoControl(recv_int, 10); // Servonun kolu kapatılıyor
        break;
      }
    }
  }
}

//increment burada istenilen nokta ile olan nokta arasında ki mesafenin bir süre içinde bitmesi için eklenmi hızlandırıcıdır.
void ServoDirection(int ServoLeft1, int ServoLeft2, int ServoRight1, int ServoRight2, int duration) {
  ServoSpeedControl(myServo1, ServoLeft1, duration);
  ServoSpeedControl(myServo2, ServoLeft2, duration);
  ServoSpeedControl(myServo3, ServoRight1, duration);
  ServoSpeedControl(myServo4, ServoRight2, duration);
}

void ServoControl(int control, int duration) { 
  static int lastControl= 0;
  if (lastControl != control) {
    if (control == 65)ServoSpeedControl(myServo1, control, duration);
    if (control == 80)ServoSpeedControl(myServo2,control, duration);
    if (control == 112)ServoSpeedControl(myServo3, control, duration);
    if (control == 71)ServoSpeedControl(myServo4, control, duration);
    if (control == 103)ServoDirection(0 , 180, 0, 0,duration);//C
  }
  lastControl = control;
}

void MotorWork(bool control, String search) {
  if (search == "MOTOR") {
    if (control == false)digitalWrite(rolePin, 1);
    else digitalWrite(rolePin, 0);
  }
  if (search == "LED") {
    if (control == false)digitalWrite(LED, 0);
    else LED_CONTROL(150, 1);
  }
}

void ServoSpeedControl(Servo servo, int targetAngle, int duration) {
  static int currentAngle, increment, newAngle,lastread = 0;
  currentAngle = servo.read(); // Mevcut açı okunuyor
  while(currentAngle != targetAngle){
  // Hedef açıya ulaşmak için adım adım hareket ediliyor
  increment = floor((targetAngle - currentAngle) / duration);// gerekli hız
  for (int i = 0; i <= duration; i++) {
    newAngle = currentAngle + (increment * i);
#if SRP == 1
    Serial.println(" Servo konumu : "  + String(newAngle));
#endif
    servo.write(newAngle);
    delay(1); //1 saniyede bir işlem yapacağı belirtiliyor     
  }
  currentAngle = servo.read(); 
  if (lastread == currentAngle){
    for(;currentAngle<=targetAngle;currentAngle++){
      servo.write(currentAngle);
#if SRP == 1
      Serial.println(" Servo konumu : "  + String(currentAngle));
#endif
      delay(1);
    }
    break;
  }
  else lastread = currentAngle;
 }
}

void MotorControl(float tls, int control) { //roleyi tetikleyerek bacaktan yüksek gerilim motor üzerinde akar ve hareket etmiş olur.
  static int lasTime, diff, Tp, StepMotorWorkTime, Time, recv_int = 0; //ZAMAN,GEÇMİŞ ZAMAN,ZAMANLAR_ARASINDAKİ FARK,TOPLAM_GEÇEN_ZAMAN
  static int TimeWork[2] = {10000, 6000}; // Bandın çalışma süreler
  static float tlsUnder, tlsTop = 0;//TOPLAM_GEÇEN_ZAMANIN_ALT_TOLERANSI VE ÜST TOLERANSI
  static bool cnt = false;//KOŞULUN OLUŞUP OLUŞMADIĞI
  if (time1.state() != RUNNING)time1.start();
  if (control == 65)StepMotorWorkTime = TimeWork[0];
  if (control == 112 or control == 80)StepMotorWorkTime = TimeWork[1];
  tlsUnder = 100 - tls ;
  tlsTop = 100 + tls ;
  tlsUnder = StepMotorWorkTime * (tlsUnder / 100) ;
  tlsTop = StepMotorWorkTime * (tlsTop / 100) ;
  while (time1.state() == RUNNING) { //timer aktif ise loop döngüsü çalışır
    MotorWork(true, "MOTOR"); // motor çalıştırılıyor
    MotorWork(true, "LED"); // led çalıştırılıyor
    Time = time1.read();
    diff = abs(Time - lasTime);
    Tp = Tp + diff;
    cnt = (Tp >= tlsUnder) and (Tp <= tlsTop);//istenilen süre içinde motorun çalıştırılıp çalışmayacağına karar verir.
#if SEARCH == 6
    Serial.println("TİMER : " + String(Time) + " CNT : " + String(cnt)  + " TP : " + String(Tp) + " Top : " + String(tlsTop) + " Under : " + String(tlsUnder));
#endif
    lasTime = Time; // Geçilmiş süre tanımlanır.
    if (cnt == true or recv_int == 121) {
#if SEARCH == 6
      Serial.println(" ------------ SÜRE DOLDU VE SİSTEM DURDURULDU ---------------");
#endif
      time1.stop(); //Timer sayıcı sıfırlanıyor
      MotorWork(false, "MOTOR"); // MOTOR
      MotorWork(false, "LED"); // LED
      Tp = 0;
      lasTime = 0;
      cnt = false;
      for(int a=0;a<2;a++)Serial.println("OK"+String(char(control)));
      Serial.flush();
      break;
    }
  }
}

void LED_CONTROL(short sleep, int countre) {
  for (int y = 0; y < countre; y++) {
    digitalWrite(LED, HIGH);
    delay(sleep);
    digitalWrite(LED, LOW);
    delay(sleep);
  }
}
