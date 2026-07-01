#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int potPin = A0;
const int senzorPin = 2;
const int releuPin = 9;
const int buzzerPin = 8;

// setpoint
int setpoint = 0;

// picaturi si debit
volatile int picaturiFereastra = 0;   // live in fereastra curenta
int picaturiUltime = 0;               // ultimele 10 secunde
int debitPicMin = 0;

// senzor - varianta sensibila cu interrupt
volatile unsigned long ultimaDetectie = 0;
const unsigned long debounceTime = 8;   // 8; daca rateaza, pun 5; daca dubleaza, pun 12

// timp
unsigned long ultimulCalcul = 0;
const unsigned long intervalCalcul = 10000; // 10 secunde

// stare sistem
const char* stareText = "INIT";
bool pompaPornita = false;

// ================= FUNCTII =================
void pornestePompa()
{
  digitalWrite(releuPin, HIGH);   // high este on
  pompaPornita = true;
}

void oprestePompa()
{
  digitalWrite(releuPin, LOW);    // low este off
  pompaPornita = false;
}

void pornesteBuzzer()
{
  digitalWrite(buzzerPin, HIGH);
}

void opresteBuzzer()
{
  digitalWrite(buzzerPin, LOW);
}

// interrupt pentru picaturi
void detectDrop()
{
  unsigned long acum = millis();

  if (acum - ultimaDetectie > debounceTime)
  {
    picaturiFereastra++;
    ultimaDetectie = acum;
  }
}

void setup()
{
  pinMode(senzorPin, INPUT);
  pinMode(releuPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  oprestePompa();
  opresteBuzzer();

  // interrupt pe senzor
  attachInterrupt(digitalPinToInterrupt(senzorPin), detectDrop, FALLING);
  // daca vezi ca pierde evenimente, incearca RISING in loc de FALLING

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("IV DRIP CONTROL");
  lcd.setCursor(0, 1);
  lcd.print("Start...");
  delay(1200);
  lcd.clear();

  Serial.begin(115200);
  ultimulCalcul = millis();
}

void loop()
{
  int suma = 0;
  for (int i = 0; i < 20; i++)
  {
    suma += analogRead(potPin);
    delay(1);
  }

  int potMedie = suma / 20;
  int setpointBrut = map(potMedie, 0, 1023, 0, 120);

  static float setpointFiltrat = 0;
  setpointFiltrat = 0.85 * setpointFiltrat + 0.15 * setpointBrut;

  int setpointNou = (int)setpointFiltrat;

  if (abs(setpointNou - setpoint) >= 2)
  {
    setpoint = setpointNou;
  }

  // ================= TIMP =================
  unsigned long acum = millis();

  // ================= CALCUL + CONTROL LA 10 SEC =================
  if (acum - ultimulCalcul >= intervalCalcul)
  {
    noInterrupts();
    picaturiUltime = picaturiFereastra;
    picaturiFereastra = 0;
    interrupts();

    // 10 sec -> x6 pentru pic/min
    debitPicMin = picaturiUltime * 6;

    if (debitPicMin == 0)
    {
      stareText = "NOFLOW";
      pornestePompa();
      pornesteBuzzer();
    }
    else if (debitPicMin < 20)
    {
      stareText = "LOW";
      pornestePompa();
      pornesteBuzzer();
    }
    else if (debitPicMin < setpoint)
    {
      stareText = "SUB";
      pornestePompa();
      opresteBuzzer();
    }
    else if (debitPicMin <= setpoint + 5)
    {
      stareText = "OK";
      oprestePompa();
      opresteBuzzer();
    }
    else if (debitPicMin <= setpoint + 15)
    {
      stareText = "PESTE";
      oprestePompa();
      opresteBuzzer();
    }
    else
    {
      stareText = "DANGER";
      oprestePompa();
      pornesteBuzzer();
    }

    Serial.print("Setpoint: ");
    Serial.print(setpoint);
    Serial.print(" pm | Flux: ");
    Serial.print(picaturiUltime);
    Serial.print("/10s | Debit: ");
    Serial.print(debitPicMin);
    Serial.print(" pm | Stare: ");
    Serial.print(stareText);
    Serial.print(" | Pompa: ");
    Serial.print(pompaPornita ? "ON" : "OFF");
    Serial.print(" | Buzzer: ");
    if (debitPicMin == 0 || debitPicMin < 20 || debitPicMin > setpoint + 15)
      Serial.println("ON");
    else
      Serial.println("OFF");

    ultimulCalcul = acum;
  }

  // ================= LCD ARANJAT =================
  int picaturiLive;
  noInterrupts();
  picaturiLive = picaturiFereastra;
  interrupts();

  // linia 2 - setpoint si debit 
  lcd.setCursor(0, 0);
  lcd.print("S:");
  lcd.print(setpoint);
  lcd.print("pm ");

  lcd.print("D:");
  lcd.print(debitPicMin);
  lcd.print("pm ");

  lcd.print("   ");

  // linia 2 -picaturi live si stare
  lcd.setCursor(0, 1);
  lcd.print("F:");
  lcd.print(picaturiLive);
  lcd.print("/10s ");

  lcd.print(stareText);

  lcd.print("      ");

  delay(50);
}