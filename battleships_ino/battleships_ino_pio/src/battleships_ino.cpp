#include <MD_MAX72xx.h>
#include <SPI.h>

// Definir los pines y el tipo de hardware
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 1
#define CS_PIN 6

// Crear el objeto MD_MAX72XX
MD_MAX72XX mx = MD_MAX72XX(MD_MAX72XX::FC16_HW, CS_PIN, MAX_DEVICES);

// Definir los botones
#define BTN_RIGHT 2
#define BTN_LEFT 3
#define BTN_UP 4
#define BTN_DOWN 5
#define BTN_ENTER 7
#define BTN_VIEW 8

// Variables de juego
int tablerob[10][2];
int tableroa[10][2];
int ataquea[2];
int ataqueb[2];
int tableroataqueaa[10][3]; // Coordenada y intensidad

int shipCount = 0;
int x = 0, y = 0;

unsigned long lastDebounceTime[5] = {0}; 
unsigned long debounceDelay = 50; 
bool gameStarted = false; // Variable para controlar si el juego ha comenzado o no
bool shipsPlaced = false; // Variable para controlar si los barcos han sido colocados
bool viewMode = false; // Variable para controlar si se está en modo de visualización

// Function declarations
void placeShips();
void receiveAttack();
void displayCursorSHIPS(int x, int y);
void receiveShipCoordinates();

bool readButton(int buttonPin, int buttonIndex) {
  static bool lastButtonState[5] = {HIGH, HIGH, HIGH, HIGH, HIGH};
  static bool buttonState[5] = {HIGH, HIGH, HIGH, HIGH, HIGH};
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

void displayShipView() {
  mx.clear();
  for (int i = 0; i < 5; i++) {
    if (tablerob[i][0] != -1) {
      mx.setPoint(tablerob[i][1], tablerob[i][0], true);
      mx.setPoint(tablerob[i][1], tablerob[i][0] + 1, true);
    }
  }
}

void displayAttackView() {
  mx.clear();
  for (int i = 0; i < 10; i++) {
    if (tableroataqueaa[i][0] != -1) {
      mx.setPoint(tableroataqueaa[i][1], tableroataqueaa[i][0], true);
    }
  }
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

void moveCursorForAttack() {
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
      delay(200);
    }
    mx.setPoint(y, x, false);  // Turn off LED after flashing
  }
}

void setup() {
  // Inicializar la matriz
  mx.begin();
  mx.control(MD_MAX72XX::INTENSITY, 1);
  mx.clear();

  // Inicializar los botones
  pinMode(BTN_RIGHT, INPUT_PULLUP);
  pinMode(BTN_LEFT, INPUT_PULLUP);
  pinMode(BTN_UP, INPUT_PULLUP);
  pinMode(BTN_DOWN, INPUT_PULLUP);
  pinMode(BTN_ENTER, INPUT_PULLUP);
  pinMode(BTN_VIEW, INPUT_PULLUP);

  // Inicializar la comunicación serie
  Serial.begin(9600);

  // Inicializar las variables de juego
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

  if (!gameStarted) { // Si el juego no ha comenzado
    placeShips(); // Ubica los barcos
    gameStarted = true; // Cambia el estado para indicar que el juego ha comenzado
  } else {
    if (!shipsPlaced) { // Si los barcos no han sido colocados
      placeShips(); // Continuar ubicando los barcos
    } else {
      if (viewMode) { // Attack mode
        moveCursorForAttack();
      } else {
        receiveAttack(); // Recibir ataques
      }
    }
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
    tablerob[shipCount][0] = x;
    tablerob[shipCount][1] = y;
    shipCount++;
    mx.setPoint(y, x, true);
    mx.setPoint(y, x + 1, true);  // Set the second part of the ship

    // Check if all ships have been placed
    if (shipCount == 5) {
      shipsPlaced = true; // Change the state to indicate ships have been placed
      
      // Send ship coordinates to Raspberry Pi
      for (int i = 0; i < 5; i++) {
        Serial.print(tablerob[i][0]);
        Serial.print(",");
        Serial.print(tablerob[i][1]);
        if (i < 4) Serial.print(" ");
      }
      Serial.println(" positions");  // Add " positions" to indicate all ships are placed

      // Send confirmation to Raspberry Pi
      Serial.println("ready");
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
    while (commaIndex != -1 && index < 5) {
      tableroa[index][0] = data.substring(0, commaIndex).toInt();
      int spaceIndex = data.indexOf(' ', commaIndex);
      if (spaceIndex == -1) spaceIndex = data.length();
      tableroa[index][1] = data.substring(commaIndex + 1, spaceIndex).toInt();
      data = data.substring(spaceIndex + 1);
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
      for (int i = 0; i < 5; i++) {
        if (tablerob[i][0] == ataquea[0] && tablerob[i][1] == ataquea[1]) {
          hit = true;
          hitIndex = i;
          break;
        }
      }

      // Flash LED at attacked coordinate
      for (int i = 0; i < 5; i++) {
        mx.setPoint(ataquea[1], ataquea[0], i % 2 == 0);
        delay(100);
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

      // Switch to attack mode after a delay
      delay(2000);
      switchView();
    }
  }
}