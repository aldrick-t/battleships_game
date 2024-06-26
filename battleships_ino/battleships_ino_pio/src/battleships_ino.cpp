// 
//   Battleships Game: Arduino Console Program.
//   Arduino C++ code for the opponent connected through serial to the host device.
//   The opponent places ships on the board and receives and sends attacks to and from the host.
//   The opponent's board is displayed on the 8x8 LED matrix controlled by the MD_MAX7219 controller chip.
//   User can use the basic buttons as input.
//   By: aldrick-t (github.com/aldrick-t), ArlesMolina (github.com/ArlesMolina)
//   Version: June 2024 (v0.2.1) 
//  


#include <MD_MAX72xx.h>
#include <SPI.h>

// Define hardware type and pins
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 1
#define CS_PIN 6

// Create MD_MAX72XX object
MD_MAX72XX mx = MD_MAX72XX(MD_MAX72XX::FC16_HW, CS_PIN, MAX_DEVICES);

// Define buttons
#define BTN_RIGHT 2
#define BTN_LEFT 3
#define BTN_UP 4
#define BTN_DOWN 5
#define BTN_ENTER 7
#define BTN_VIEW 8

// Game variables
int tablerob[10][2];
int tableroa[10][2];
int ataquea[2];
int ataqueb[2];
int tableroataqueaa[10][3]; // Coordinate and intensity

int shipCount = 0;
int x = 0, y = 0;

unsigned long lastDebounceTime[6] = {0}; 
unsigned long debounceDelay = 50; 
bool gameStarted = false; // Variable to control if the game has started
bool shipsPlaced = false; // Variable to control if the ships have been placed
bool viewMode = false; // false for ship view, true for attack view
bool opponentTurn = false; // Variable to control the opponent's turn
int lastAttack[2] = {-1, -1}; // Last received attack

// PWM variables
int brightness = 255; // Full brightness
unsigned long lastUpdateTime = 0;
int pwmState = 0;
bool lastAttackHit = false; // Variable para indicar si el último ataque fue un acierto o no


// Function declarations
void placeShips();
void receiveAttack();
void displayCursorSHIPS(int x, int y);
void receiveShipCoordinates();
void switchView();
void displayShipView();
void displayAttackView();
void moveCursorForAttack();
bool readButton(int buttonPin, int buttonIndex);
void updateDisplay();
void pwmControlLED(int row, int col, bool hit); // Declaración de la función pwmControlLED

bool readButton(int buttonPin, int buttonIndex) {
  static bool lastButtonState[6] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
  static bool buttonState[6] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
  bool reading = digitalRead(buttonPin);

  if (reading != lastButtonState[buttonIndex]) {
    lastDebounceTime[buttonIndex] = millis();
  }

  if ((millis() - lastDebounceTime[buttonIndex]) > debounceDelay) {
    if (reading != buttonState[buttonIndex]) {
      buttonState[buttonIndex] = reading;

      if (buttonState[buttonIndex] == LOW) {
        lastButtonState[buttonIndex] = reading;
        return true;
      }
    }
  }

  lastButtonState[buttonIndex] = reading;
  return false;
}

void setup() {
  // Initialize the matrix
  mx.begin();
  mx.control(MD_MAX72XX::INTENSITY, 1);
  mx.clear();

  // Initialize buttons
  pinMode(BTN_RIGHT, INPUT_PULLUP);
  pinMode(BTN_LEFT, INPUT_PULLUP);
  pinMode(BTN_UP, INPUT_PULLUP);
  pinMode(BTN_DOWN, INPUT_PULLUP);
  pinMode(BTN_ENTER, INPUT_PULLUP);
  pinMode(BTN_VIEW, INPUT_PULLUP);

  // Initialize serial communication
  Serial.begin(9600);

  // Initialize game variables
  memset(tablerob, -1, sizeof(tablerob));
  memset(tableroa, -1, sizeof(tableroa));
  memset(ataquea, -1, sizeof(ataquea));
  memset(ataqueb, -1, sizeof(ataqueb));
  memset(tableroataqueaa, -1, sizeof(tableroataqueaa));
}

void loop() {
  if (readButton(BTN_VIEW, 5)) { // Assuming the view button is the 6th button
    switchView();
  }

  if (!gameStarted) { // If the game has not started
    placeShips(); // Place the ships
    gameStarted = true; // Change the state to indicate that the game has started
  } else {
    if (!shipsPlaced) { // If the ships have not been placed
      placeShips(); // Continue placing the ships
    } else {
      if (viewMode) { // Attack mode
        moveCursorForAttack();
      } else {
        receiveAttack(); // Receive attacks
      }
    }
  }

  // Always update the display to ensure the cursor is shown
  updateDisplay();
}

void switchView() {
  viewMode = !viewMode;
  if (viewMode) {
    // Display the attack view
    displayAttackView();
  } else {
    // Display the ship view
    displayShipView();
  }
}

void displayShipView() {
  mx.clear();
  for (int i = 0; i < 5; i++) {
    if (tablerob[i][0] != -1) {
      mx.setPoint(tablerob[i][1], tablerob[i][0], true);
      mx.setPoint(tablerob[i][1], tablerob[i][0] + 1, true);
    }
  }
  // Flash the latest attack received
  if (lastAttack[0] != -1 && lastAttack[1] != -1) {
    for (int i = 0; i < 5; i++) {
      mx.setPoint(lastAttack[1], lastAttack[0], i % 2 == 0);
      delay(100);
    }
    mx.setPoint(lastAttack[1], lastAttack[0], false);  // Turn off LED after flashing
  }
}

//void displayAttackView() {
  //mx.clear();
  //for (int i = 0; i < 10; i++) {
  //  if (tableroataqueaa[i][0] != -1) {
  //    mx.setPoint(tableroataqueaa[i][1], tableroataqueaa[i][0], true);
  //  }
  //}
  // Show the cursor for attack
  //if (!opponentTurn) {
  //  mx.setPoint(y, x, true);
  //}
//}

void displayAttackView() {
  mx.clear();
  for (int i = 0; i < 10; i++) {
    if (tableroataqueaa[i][0] != -1) {
      mx.setPoint(tableroataqueaa[i][1], tableroataqueaa[i][0], true);
    }
  }

  // Mostrar el cursor para el ataque
  if (!opponentTurn) {
    mx.setPoint(y, x, true);
  }

  // Parpadeo del último ataque recibido si hubo un acierto
  if (lastAttack[0] != -1 && lastAttack[1] != -1) {
    pwmControlLED(lastAttack[1], lastAttack[0], lastAttackHit);
  } else {
    // Si no hubo ataque reciente, asegúrate de apagar el LED si está encendido
    mx.setPoint(lastAttack[1], lastAttack[0], false);
  }
}


void placeShips() {
  displayCursorSHIPS(x, y);

  if (readButton(BTN_RIGHT, 0)) {
    if (x < 6) {  // Check to prevent moving out of the right boundary
      x = (x + 1) % 8;
    }
  }
  if (readButton(BTN_LEFT, 1)) {
    if (x > 0) {  // Check to prevent moving out of the left boundary
      x = (x - 1 + 8) % 8;
    }
  }
  if (readButton(BTN_UP, 2)) {
    y = (y - 1 + 8) % 8;
  }
  if (readButton(BTN_DOWN, 3)) {
    y = (y + 1) % 8;
  }

  if (readButton(BTN_ENTER, 4)) {
    if (shipCount < 5) {
      tablerob[shipCount][0] = x;
      tablerob[shipCount][1] = y;
      shipCount++;
      mx.setPoint(y, x, true);
      mx.setPoint(y, x + 1, true);  // Set the second part of the ship
      // Check if all ships have been placed
      if (shipCount == 5) {
        shipsPlaced = true; // Change the state to indicate that the ships have been placed
        
        Serial.print("positions:");  // Add " positions" to indicate all ships are placed
        // Send ship coordinates to Raspberry Pi
        for (int i = 0; i < 5; i++) {
          Serial.print(tablerob[i][0]);
          Serial.print(",");
          Serial.print(tablerob[i][1]);
          Serial.print(" ");
          Serial.print(tablerob[i][0] + 1);
          Serial.print(",");
          Serial.print(tablerob[i][1]);
          if (i < 4) Serial.print(" ");
        }

        // Send confirmation to Raspberry Pi
        Serial.println(" ready");
      }
    }
  }
}

void displayCursorSHIPS(int x, int y) {
  mx.clear();
  for (int i = 0; i < 5; i++) {
    if (tablerob[i][0] != -1) {
      mx.setPoint(tablerob[i][1], tablerob[i][0], true);
      mx.setPoint(tablerob[i][1], tablerob[i][0] + 1, true);  // Set the second part of the ship
    }
  }
  mx.setPoint(y, x, true);
  mx.setPoint(y, x + 1, true);  // Set the second part of the ship
}

void receiveShipCoordinates() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    int index = 0;
    int commaIndex = data.indexOf(',');

    while (commaIndex != -1 && index < 10) {
      int x = data.substring(0, commaIndex).toInt();
      data = data.substring(commaIndex + 1);
commaIndex = data.indexOf(',');
int y = data.substring(0, commaIndex).toInt();
tableroa[index][0] = x;
tableroa[index][1] = y;
data = data.substring(commaIndex + 1);
commaIndex = data.indexOf(',');
index++;
}
}
}

void receiveAttack() {
if (Serial.available()) {
String data = Serial.readStringUntil('\n');
int commaIndex = data.indexOf(',');
if (commaIndex != -1) {
ataquea[0] = data.substring(0, commaIndex).toInt();
ataquea[1] = data.substring(commaIndex + 1).toInt();

  bool hit = false;
  int hitIndex = -1;
  for (int i = 0; i < 10; i++) {
    if (tablerob[i][0] == ataquea[0] && tablerob[i][1] == ataquea[1]) {
      hit = true;
      lastAttackHit = true;
      hitIndex = i;
      break;
    }
  }

  // Flash LED at attacked coordinate
  for (int i = 0; i < 5; i++) {
    mx.setPoint(ataquea[1], ataquea[0], i % 2 == 0);
    delay(300);
  }
  mx.setPoint(ataquea[1], ataquea[0], false);  // Turn off LED after flashing

  if (hit) {
    Serial.println("hit");
  } else {
    Serial.println("miss");
  }

  // Save attack on player B's board
  for (int i = 0; i < 10; i++) {
    if (tablerob[i][0] == -1) {
      tablerob[i][0] = ataquea[0];
      tablerob[i][1] = ataquea[1];
      tablerob[i][2] = hit ? 1 : 0; // 1 if hit, 0 if miss
      break;
    }
  }

  // Save the last attack received
  lastAttack[0] = ataquea[0];
  lastAttack[1] = ataquea[1];

  // Switch to attack mode after a delay
  delay(2000);
  opponentTurn = false;  // Switch to player's turn
  switchView();
}

}
}

void moveCursorForAttack() {
if (!opponentTurn) {
if (readButton(BTN_RIGHT, 0)) {
if (x < 7) { x++; }
}
if (readButton(BTN_LEFT, 1)) {
if (x > 0) { x--; }
}
if (readButton(BTN_UP, 2)) {
if (y > 0) { y--; }
}
if (readButton(BTN_DOWN, 3)) {
if (y < 7) { y++; }
}
if (readButton(BTN_ENTER, 4)) {
// Send attack coordinates to Raspberry Pi
Serial.print("attack:");
Serial.print(x);
Serial.print(",");
Serial.println(y);
  // Flash LED at attacked coordinate
  for (int i = 0; i < 5; i++) {
    mx.setPoint(y, x, i % 2 == 0);
    delay(100);
  }
  mx.setPoint(y, x, false);  // Turn off LED after flashing

  // Save attack on player A's board
  for (int i = 0; i < 10; i++) {
    if (tableroataqueaa[i][0] == -1) {
      tableroataqueaa[i][0] = x;
      tableroataqueaa[i][1] = y;
      tableroataqueaa[i][2] = 1; // Mark as attacked
      break;
    }
  }
  opponentTurn = true;  // Switch to opponent’s turn
}
}
}

void updateDisplay() {
if (viewMode) {
displayAttackView();
} else {
displayShipView();
}
}

void pwmControlLED(int row, int col, bool hit) {
  unsigned long currentTime = millis();
  static unsigned long lastFlashTime = 0;
  static bool flashState = false;

  if (currentTime - lastUpdateTime > 30) { // Ajusta el intervalo de tiempo para una transición suave
    lastUpdateTime = currentTime;

    if (hit) {
      if (currentTime - lastFlashTime > 500) { // Intervalo de parpadeo de 500ms (cambia según sea necesario)
        lastFlashTime = currentTime;
        flashState = !flashState;
      }

      brightness = flashState ? 255 : 0; // Brillo completo o apagado dependiendo del estado de parpadeo
      mx.control(MD_MAX72XX::INTENSITY, brightness);
    } else {
      mx.setPoint(row, col, true); // Mantén el LED encendido si no hubo acierto
    }
  }
}
