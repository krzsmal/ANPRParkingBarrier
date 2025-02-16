#include <Servo.h>

Servo myServo;
int servoPin = 7;
bool isRaised = false;

void setup() {
  myServo.attach(servoPin);
  myServo.write(85);
  delay(1000);
  Serial.begin(9600); 
}

void loop() {
  if (Serial.available() > 0) {

    String received = Serial.readString();

    if (received == "OPEN" && isRaised == false) {
      myServo.attach(servoPin);
      for (int pos = 85; pos >= 0; pos--) {
        myServo.write(pos);
        delay(3000 / 85);
      }
      isRaised = true;
    } else if ((received == "CLOSE")) {
      for (int pos = 0; pos <= 85; pos++) {
        myServo.write(pos);
        delay(3000 / 85);
      }
      isRaised = false;
    }
    delay(200);
  }
}
