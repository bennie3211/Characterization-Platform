#include <HX711.h>
#include <Arduino.h>
#include <EEPROM.h>

// HX711 pins
#define HX711_DOUT 6
#define HX711_SCK  5
#define HX711_GAIN 128

// EEPROM Address
const int EEPROM_ADDR_SCALE = 0;

HX711 loadcell;

// Define functions
void tare(byte samples);
void calibrate(double units);

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; }

  loadcell.begin(HX711_DOUT, HX711_SCK, HX711_GAIN);
  delay(500);

  // Load Calibration
  float saved_scale = 0.0f;
  EEPROM.get(EEPROM_ADDR_SCALE, saved_scale);

  // Use default scale when no value or 0.0 is returned
  if (isnan(saved_scale) || saved_scale == 0.0) {
    loadcell.set_scale(1.0);
  } else {
    loadcell.set_scale(saved_scale);
  }

  // Initialize tare at startup
  tare(100);
}

void loop() {
  // Handle serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    int sepIndex = cmd.indexOf(':');

    if (sepIndex > 0) {
      String action = cmd.substring(0, sepIndex);
      String value  = cmd.substring(sepIndex + 1);

      double argument = value.toDouble();

      if (action.equalsIgnoreCase("tare")) {
        tare((byte)argument);
      }
      else if (action.equalsIgnoreCase("cal")) {
        calibrate(argument);
      }
    }
  }

  // Read load cell ONLY when new data is ready
  if (loadcell.is_ready()) {

    // Retrieve one sample from HX711
    double reaction = loadcell.get_units(1);

    // JSON output
    Serial.print("{");
      Serial.print("\"force\":");
      Serial.print(reaction, 3);
    Serial.println("}");
  }
}

/*
 * Tare load cell with given samples
*/
void tare(byte samples) {
  loadcell.tare(samples);
}

void calibrate(double units) {
  // Reset scale for new calibration
  loadcell.set_scale(1.0);

  // Read offset-corrected raw value
  double value = loadcell.get_value(100);
  double new_scale = value / units;

  // Set the new scale factor
  loadcell.set_scale(new_scale);

  // Save scale factor to EEPROM
  EEPROM.put(EEPROM_ADDR_SCALE, (float)new_scale);
}