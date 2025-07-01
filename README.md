# Sine32 — A Really Simple MIDI Sine Synthesizer on ESP32

Sine32 is a MIDI-enabled sine wave synthesizer, powered by an ESP32. It is controllable over serial and can be used with any device capable of:
- Establishing a serial connection
- Running python code
- Running loopMIDI or similar virtual MIDI routing software

## Getting Started

### Requirements

- ESP32 development board
- A speaker
- Arduino IDE (recommended) or ESP-IDF environment for flashing
- loopMIDI (or equivalent virtual MIDI routing software)
- Python 3.12 runtime (other versions may work but are untested)

### Installation

1. Clone this repo:  
   ```bash
   git clone https://github.com/pattycoder01/sine32.git
   ```
2. Flash the ```sine32.ino``` sketch onto the esp32
3. Connect a speaker to GPIO25 and GND on the ESP32

## User Manual

### Usage

1. Connect your ESP32 with installed firmware and connected speaker
2. Start loopMIDI and create a new virtual port if necessary
3. Start the ```Sine32_controller.py``` script using python
4. Set the ```MIDI Input Port``` field to your loopMIDI port
5. Set the ```Serial Port``` field to the Serial Port of your ESP32 (usually there's only one; if not, try available ports until the ESP32 responds)
6. Press the ```Start``` button
7. Send MIDI data to the loopMIDI port from your DAW or any software that supports MIDI output

### Explanation of the UI Elements

- **MIDI Input Port:** Select the MIDI input device you'd like to use — typically your loopMIDI port, but this can also be a hardware MIDI keyboard
- **Serial Port:** The COM port your ESP32 is connected to. If multiple ports are shown, try each until the ESP32 responds
- **Baudrate:** The speed at which tone data is sent via serial. Default is 115200 — only change this if you've modified the firmware to use a different baud rate
- **Transposition:** The number of semitones to shift incoming MIDI notes up or down
- **Controls:**
  - **Start** - Begins streaming MIDI data over serial to the ESP32
  - **Stop** - Stops MIDI data transmission. Note: This does not stop any currently playing tones - press the ESP32’s reset button if needed
  - **Refresh** - Re-scans available MIDI and serial ports. Use this if you plug in a new device after launching the software

### Recommended Third-Party Software
A virtual MIDI port is required to connect your DAW to the controller. We recommend using [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) on Windows.

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
