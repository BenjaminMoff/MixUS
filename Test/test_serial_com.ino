using namespace std;

String message = "";
char trigger = '8';
bool stringComplete = false;

bool begun = false;
void setup() {
  Serial.begin(9600);
}

void loop() {
  if(!begun){
    Serial.print("echo:  M907 X135 Y135 Z135 E135 135");
    delay(1000);
  }
  if (stringComplete) {
    begun = true;
    Serial.print("G-code received\n");

    // If the message received contains the trigger character, notify the application
    if (message[3] == trigger) {

      // Simulate g-code execution with a delay
      delay(1000);
      Serial.print("Instruction completed\r\n");
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