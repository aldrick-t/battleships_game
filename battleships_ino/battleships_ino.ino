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

// Variables de juego
int tablerob[10][2];
int tableroa[10][2];
int ataquea[2];
int ataqueb[2];
int tableroataqueaa[10][3]; // Coordenada y intensidad

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

  // Inicializar las variables de juego
  memset(tablerob, -1, sizeof(tablerob));
  memset(tableroa, -1, sizeof(tableroa));
  memset(ataquea, -1, sizeof(ataquea));
  memset(ataqueb, -1, sizeof(ataqueb));
  memset(tableroataqueaa, -1, sizeof(tableroataqueaa));

  // Colocar los barcos
  placeShips();

  // Ciclo principal del juego
  while (true) {
    // Recibir ataque
    receiveAttack();
    // Realizar ataque
    performAttack();
    // Verificar estado del juego
    checkGameState();
  }
}

void placeShips() {
  int shipCount = 0;
  int x = 0, y = 0;

  while (shipCount < 5) {
    displayCursor(x, y);

    if (digitalRead(BTN_RIGHT) == LOW) x = (x + 1) % 8;
    if (digitalRead(BTN_LEFT) == LOW) x = (x - 1 + 8) % 8;
    if (digitalRead(BTN_UP) == LOW) y = (y - 1 + 8) % 8;
    if (digitalRead(BTN_DOWN) == LOW) y = (y + 1) % 8;

    if (digitalRead(BTN_ENTER) == LOW) {
      tablerob[shipCount][0] = x;
      tablerob[shipCount][1] = y;
      shipCount++;
      mx.setPoint(x, y, true);
      delay(200); // Para evitar múltiples lecturas
    }
  }
}

void displayCursor(int x, int y) {
  mx.clear();
  for (int i = 0; i < 5; i++) {
    if (tablerob[i][0] != -1) {
      mx.setPoint(tablerob[i][0], tablerob[i][1], true);
    }
  }
  mx.setPoint(x, y, true);
  delay(100);
}

void receiveAttack() {
  // Simulación de recepción de coordenadas de ataque
  ataquea[0] = random(0, 8);
  ataquea[1] = random(0, 8);

  bool hit = false;
  for (int i = 0; i < 5; i++) {
    if (tablerob[i][0] == ataquea[0] && tablerob[i][1] == ataquea[1]) {
      hit = true;
      break;
    }
  }

  if (hit) {
    for (int i = 0; i < 5; i++) {
      mx.setPoint(ataquea[0], ataquea[1], i % 2 == 0);
      delay(100);
    }
  } else {
    for (int i = 0; i < 5; i++) {
      mx.setPoint(ataquea[0], ataquea[1], i % 2 == 0);
      delay(300);
    }
  }

  // Guardar ataque en el registro
  for (int i = 0; i < 10; i++) {
    if (tableroa[i][0] == -1) {
      tableroa[i][0] = ataquea[0];
      tableroa[i][1] = ataquea[1];
      tableroa[i][2] = hit ? 1 : 0;
      break;
    }
  }
}

void performAttack() {
  int x = 0, y = 0;

  while (true) {
    displayCursor(x, y);

    if (digitalRead(BTN_RIGHT) == LOW) x = (x + 1) % 8;
    if (digitalRead(BTN_LEFT) == LOW) x = (x - 1 + 8) % 8;
    if (digitalRead(BTN_UP) == LOW) y = (y - 1 + 8) % 8;
    if (digitalRead(BTN_DOWN) == LOW) y = (y + 1) % 8;

    if (digitalRead(BTN_ENTER) == LOW) {
      ataqueb[0] = x;
      ataqueb[1] = y;
      break;
    }
  }

  bool hit = false;
  for (int i = 0; i < 10; i++) {
    if (tableroa[i][0] == ataqueb[0] && tableroa[i][1] == ataqueb[1]) {
      hit = tableroa[i][2];
      break;
    }
  }

  if (hit) {
    for (int i = 0; i < 5; i++) {
      mx.setPoint(ataqueb[0], ataqueb[1], i % 2 == 0);
      delay(100);
    }
  } else {
    mx.setPoint(ataqueb[0], ataqueb[1], true);
    delay(1000);
  }

  // Guardar ataque en el registro
  for (int i = 0; i < 10; i++) {
    if (tableroataqueaa[i][0] == -1) {
      tableroataqueaa[i][0] = ataqueb[0];
      tableroataqueaa[i][1] = ataqueb[1];
      tableroataqueaa[i][2] = hit ? 1 : 0;
      break;
    }
  }
}

void checkGameState() {
  int shipsLeft = 0;
  for (int i = 0; i < 5; i++) {
    if (tablerob[i][0] != -1) shipsLeft++;
  }

  if (shipsLeft == 0) {
    displaySadFace();
    waitForRestart();
  }

  shipsLeft = 0;
  for (int i = 0; i < 10; i++) {
    if (tableroa[i][0] != -1 && tableroa[i][2] == 1) shipsLeft++;
  }

  if (shipsLeft == 0) {
    displayHappyFace();
    waitForRestart();
  }
}

void displaySadFace() {
  mx.clear();
  // Dibujar una carita triste
  mx.setPoint(1, 1, true);
  mx.setPoint(1, 2, true);
  mx.setPoint(2, 2, true);
  mx.setPoint(2, 3, true);
  mx.setPoint(1, 4, true);
  mx.setPoint(1, 5, true);
  mx.setPoint(2, 5, true);
  mx.setPoint(2, 6, true);
  delay(2000);
}

void displayHappyFace() {
  mx.clear();
  // Dibujar una carita feliz
  mx.setPoint(1, 1, true);
  mx.setPoint(1, 2, true);
  mx.setPoint(1, 3, true);
  mx.setPoint(1, 4, true);
  mx.setPoint(1, 5, true);
  mx.setPoint(1, 6, true);
  mx.setPoint(2, 1, true);
  mx.setPoint(2, 6, true);
  delay(2000);
}

void waitForRestart() {
  while (digitalRead(BTN_ENTER) == HIGH);
  setup(); // Reiniciar el juego
}