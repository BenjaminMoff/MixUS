using namespace std;

String message = "";
char trigger = '8';
bool stringComplete = false;

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (stringComplete) {
    Serial.print("G-code received\n");

    // If the message received contains the trigger character, notify the application
    if (message[3] == trigger) {
      
      // Simulate g-code execution with a delay
      delay(1000);
      Serial.print("Instruction completed\n");
    }
    message = "";
    stringComplete = false;
  }  
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    message += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
