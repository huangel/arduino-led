int pins[] = {2, 3, 4, 5, 6, 7, 8};
int cpins = 7;
int val;

void setup() { 
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() >= cpins) {
    for (int i = 0; i < cpins; i++) {
      val = Serial.read();
      analogWrite(pins[i], val);
      Serial.write(val);
    }
  }
} 
