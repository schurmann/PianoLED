#include <LiquidCrystal.h>
#include <FastLED.h>
const int NUM_LEDS = 60;
const int DATA_PIN = 6;
const int BRIGHTNESS = 6;

CRGB leds[NUM_LEDS];
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

typedef struct META {
    bool piano_is_on;
} META;

typedef struct NOTE {
    bool is_on;
    unsigned char note;
    unsigned char velocity;
} NOTE;

NOTE note;
META meta = {.piano_is_on=true};
unsigned char packet_type;
bool display_on = true;

void setup() {
  Serial.begin(9600);
  pinMode(7, OUTPUT);
  set_display(true);
  lcd.begin(16, 2);
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
}

void print_note(){
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Note: ");
    lcd.print(note.note);
    lcd.setCursor(0, 1);
    lcd.print("Velocity: ");
    lcd.print(note.velocity);
}


void color_leds(){
    if(note.is_on){
        leds[note.note % 10] = CRGB::Red;
    }else{
        leds[note.note % 10] = CRGB::Black;
    }
    FastLED.show();
}

void blink_led(unsigned char num){
    leds[num] = CRGB::Yellow;
    FastLED.show();
    delay(50);
    leds[num] = CRGB::Black;
    FastLED.show();
}

void set_display(bool val){
    digitalWrite(7, val);
    display_on = val;
}

void print_lcd_from_start(char *text){
    lcd.setCursor(0, 0);
    lcd.clear();
    lcd.print(text);
}

void read_midi(){
    if(!Serial.available()){
        return;
    }

    Serial.readBytes(&packet_type, 1);
    if(packet_type == 1){
        Serial.readBytes((unsigned char*)&meta, 1);
        blink_led((unsigned char) meta.piano_is_on);
        if(meta.piano_is_on){
            print_lcd_from_start("HELLO!");
            set_display(true);
        }else if(!meta.piano_is_on){
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("BYE!");
            delay(2000);
            set_display(false);
            lcd.clear();
        }
    }else if(packet_type == 2){
        Serial.readBytes((unsigned char*)&note, 3);
        print_note();
        color_leds();
    }
}

void loop() {
    read_midi();
}

