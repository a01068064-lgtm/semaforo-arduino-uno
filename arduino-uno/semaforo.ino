// SEMAFORO - Arduino UNO
// Rojo PIN 2 (20s), Amarillo PIN 3 (5s), Verde PIN 4 (25s)
// Envia por Serial: "RED:20", "GREEN:25", "YELLOW:5" ... @9600 baud

const int PIN_ROJO = 2;
const int PIN_AMARILLO = 3;
const int PIN_VERDE = 4;

const int DUR_ROJO = 20;
const int DUR_AMARILLO = 5;
const int DUR_VERDE = 25;

void setup() {
  pinMode(PIN_ROJO, OUTPUT);
  pinMode(PIN_AMARILLO, OUTPUT);
  pinMode(PIN_VERDE, OUTPUT);
  digitalWrite(PIN_ROJO, LOW);
  digitalWrite(PIN_AMARILLO, LOW);
  digitalWrite(PIN_VERDE, LOW);
  Serial.begin(9600);
  delay(500);
  Serial.println("ARDUINO_READY");
}

void encenderSolo(int pinEncendido) {
  digitalWrite(PIN_ROJO, pinEncendido == PIN_ROJO ? HIGH : LOW);
  digitalWrite(PIN_AMARILLO, pinEncendido == PIN_AMARILLO ? HIGH : LOW);
  digitalWrite(PIN_VERDE, pinEncendido == PIN_VERDE ? HIGH : LOW);
}

void correrFase(const char* nombre, int pin, int duracion) {
  encenderSolo(pin);
  for (int restante = duracion; restante > 0; restante--) {
    Serial.print(nombre);
    Serial.print(":");
    Serial.println(restante);
    delay(1000);
  }
}

void loop() {
  correrFase("RED", PIN_ROJO, DUR_ROJO);
  correrFase("GREEN", PIN_VERDE, DUR_VERDE);
  correrFase("YELLOW", PIN_AMARILLO, DUR_AMARILLO);
}
