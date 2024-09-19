#include <ArduinoJson.h>
#include <Arduino.h>
#include <LiquidCrystal.h>

// Define as conexões e cria o objeto para acesso
const int rs = 8, en = 9, d4 = 4, d5 = 5, d6 = 6, d7 = 7;
const int backLight = 10;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

struct {
  int limite;
  char *nome;
} teclas[] = {
  {   50, "Direita " },
  {  150, "Cima    " },
  {  300, "Baixo   " },
  {  500, "Esquerda" },
  {  750, "Select  " },
  { 1024, "        " }  // nenhuma tecla apertada
};

float ra = 0.0;  // Right Ascension
float ha = 0.0;  // Hour Angle
float dec = 0.0; // Declination

void setup() {
  //Progama o pino de backlight como saída
  pinMode(backLight, OUTPUT);
  // Inicia o display e coloca uma mensagem
  lcd.begin(16, 2);
  lcd.print("Hello World");
  // Acende o backlight
  digitalWrite(backLight, HIGH);

  Serial.begin(9600);  // Start the serial communication at 9600 baud rate
  while (!Serial) {
    ;  // Wait for the serial port to connect (needed for native USB ports)
  }

  Serial.println("Ready to receive data...");
}

String degrees_to_dms(float degrees) {
    /*
      Converts Degrees to string, in format dd:mm:ss:cc
      :param degrees: Degrees (float)
    */
  
    // Check if the degrees value is a number (Arduino-specific check)
    if (!isnan(degrees)) {
        // Determine the sign of the degrees
        String sign = (degrees < 0) ? "-" : "+";
        degrees = abs(degrees);

        // Calculate degrees, minutes, seconds, and fractional seconds
        int degrees_int = (int)degrees;                      // Integer part of degrees
        int minutes = (int)((degrees - degrees_int) * 60);   // Minutes
        int seconds = (int)(((degrees - degrees_int) * 60 - minutes) * 60);  // Seconds
        int seconds_decimal = (int)((((degrees - degrees_int) * 60 - minutes) * 60 - seconds) * 100);  // Fractional seconds

        // Format the result as a string dd:mm:ss:cc
        char degrees_string[16];  // String buffer to hold the formatted string
        sprintf(degrees_string, "%s%02d:%02d:%02d", sign.c_str(), degrees_int, minutes, seconds);

        // Return the formatted string
        return String(degrees_string);
    } else {
        // Return an empty string if the input is not a number
        return "";
    }
}

String hours_to_hms(float hours, int decimal_digits = 0) {
    /*
      Converts Float Hour to string Hour, in format hh:mm:ss:cc
      :param hours: Hours (float)
      :param decimal_digits: Number of decimal digits for fractional seconds
    */
    
    // Check if the hours value is a number (Arduino-specific check)
    if (!isnan(hours)) {
        // Determine the sign of the hours
        String sign = (hours < 0) ? "-" : "";
        hours = abs(hours);

        // Calculate whole hours, minutes, seconds, and fractional seconds
        int whole_hours = (int)hours;                             // Integer part of hours
        float fractional_hours = hours - whole_hours;             // Fractional part of hours

        int minutes = (int)(fractional_hours * 60);               // Minutes
        float fractional_minutes = fractional_hours * 60 - minutes;

        int seconds = (int)(fractional_minutes * 60);             // Seconds
        float fractional_seconds = fractional_minutes * 60 - seconds;

        // Calculate the fractional part for seconds, based on decimal_digits
        int fractional_seconds_value = (int)(fractional_seconds * pow(10, decimal_digits));

        // Create a string for the seconds part with fractional digits
        char seconds_str[10];  // Buffer for seconds with fractional part
        sprintf(seconds_str, "%02d%0*d", seconds, decimal_digits, fractional_seconds_value);

        // Format the result as a string hh:mm:ss:cc
        char time_string[20];  // Buffer to hold the formatted string
        sprintf(time_string, "%s%02d:%02d:%s", sign.c_str(), whole_hours, minutes, seconds_str);

        // Return the formatted string
        return String(time_string);
    } else {
        // Return an empty string if the input is not a number
        return "";
    }
}



void loop() {
  if (Serial.available() > 0) {
    // Read incoming serial data
    String incomingData = Serial.readStringUntil('\n'); // Read until newline character

    // Parse the JSON string
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, incomingData);

    if (error) {
      Serial.println(F("deserializeJson() failed: "));
      // lcd.setCursor(3, 1);
      lcd.print("Err");
      return;
    }
    //{"ra":11.546, "ha":4.23, "dec":-77.343}
    // Extract ra, ha, and dec values from the JSON object
    ra = doc["ra"];
    ha = doc["ha"];
    dec = doc["dec"];

    // Print the received values for debugging
    Serial.print("RA: ");
    Serial.println(hours_to_hms(ra));

    Serial.print("DEC: ");
    Serial.println(degrees_to_dms(dec));

    lcd.setCursor(3, 1);
    lcd.print(hours_to_hms(ra));
    // Serial.print("HA: ");
    // Serial.println(ha);
    // Serial.print("Dec: ");
    // Serial.println(dec);
  }
}
