#include <Arduino.h>
#include <driver/dac.h>
#include <math.h>

#define DAC_PIN 25
#define SAMPLE_RATE 8000
#define MAX_VOICES 8

struct Voice {
  bool active = false;
  uint8_t note = 0;
  uint8_t velocity = 0;
  float phase = 0;
  float phaseIncrement = 0;
};

Voice voices[MAX_VOICES];
unsigned long lastSampleMicros = 0;
const unsigned long sampleInterval = 1000000UL / SAMPLE_RATE;

float noteToFreq(uint8_t note) {
  return 440.0 * pow(2.0, (note - 69) / 12.0);
}

void playSample() {
  float sample = 0;
  int activeVoices = 0;
  for (int i = 0; i < MAX_VOICES; i++) {
    if (voices[i].active) {
      sample += sin(voices[i].phase) * (voices[i].velocity / 255.0);
      voices[i].phase += voices[i].phaseIncrement;
      if (voices[i].phase > 2 * PI) voices[i].phase -= 2 * PI;
      activeVoices++;
    }
  }
  if (activeVoices > 0) {
    sample /= activeVoices;
    uint8_t dacVal = (uint8_t)((sample + 1.0) * 127.5);
    dacWrite(DAC_PIN, dacVal);
  } else {
    dacWrite(DAC_PIN, 128);
  }
}

int findVoice(uint8_t note) {
  for (int i = 0; i < MAX_VOICES; i++) {
    if (voices[i].active && voices[i].note == note) return i;
  }
  for (int i = 0; i < MAX_VOICES; i++) {
    if (!voices[i].active) return i;
  }
  return -1;
}

void parseInput(String input) {
  int start = 0;
  while (true) {
    int openBracket = input.indexOf('[', start);
    int closeBracket = input.indexOf(']', openBracket);
    if (openBracket == -1 || closeBracket == -1) break;

    String block = input.substring(openBracket + 1, closeBracket);
    int sep1 = block.indexOf(';');
    int sep2 = block.indexOf(';', sep1 + 1);
    if (sep1 == -1 || sep2 == -1) {
      Serial.println("wrong format!");
      break;
    }

    int note = block.substring(0, sep1).toInt();
    int velocity = block.substring(sep1 + 1, sep2).toInt();
    int onoff = block.substring(sep2 + 1).toInt();

    if (note < 0 || note > 127 || velocity < 0 || velocity > 255 || (onoff != 0 && onoff != 1)) {
      Serial.println("invalid values!");
      start = closeBracket + 1;
      continue;
    }

    int v = findVoice(note);
    if (v == -1) {
      Serial.println("no free voice available!");
      start = closeBracket + 1;
      continue;
    }

    if (onoff == 1) {
      voices[v].active = true;
      voices[v].note = note;
      voices[v].velocity = velocity;
      voices[v].phase = 0;
      voices[v].phaseIncrement = 2 * PI * noteToFreq(note) / SAMPLE_RATE;
      Serial.print("note on: ");
      Serial.print(note);
      Serial.print(" velocity: ");
      Serial.println(velocity);
    } else {
      if (voices[v].active) {
        voices[v].active = false;
        Serial.print("note off: ");
        Serial.println(note);
      }
    }

    start = closeBracket + 1;
  }
}

void setup() {
  Serial.begin(115200);
  dacWrite(DAC_PIN, 128);
}

void loop() {
  unsigned long now = micros();
  if (now - lastSampleMicros >= sampleInterval) {
    lastSampleMicros += sampleInterval;
    playSample();
  }

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.length() > 0) {
      parseInput(input);
    }
  }
}
