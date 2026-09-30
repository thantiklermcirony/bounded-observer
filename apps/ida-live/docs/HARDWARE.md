# External 850 nm LED driver (optional)

Needed only for fast pulses (anything faster than one switch per second) and for the
covered-LED control. The headband's own light needs no extra hardware.

## Parts

- Arduino Uno or Nano (ATmega328P), with USB cable
- one 850 nm infrared LED (5 mm through-hole or a small SMD emitter); note its rated current
- a logic-level N-channel MOSFET (e.g. AO3400 or IRLZ44N) or an NPN transistor (2N2222) with 1 kΩ base resistor
- a series resistor sized for the LED's rated current from 5 V (for 50 mA at a 1.5 V forward voltage: (5 - 1.5) / 0.05 = 70 Ω, use 82 Ω)
- thin twisted-pair wire and a soft mount so the LED rests against the forehead

## Wiring

```
Arduino pin 9 ──[1 kΩ if NPN]── gate/base
Arduino 5V ── series resistor ── LED anode ── LED cathode ── drain/collector
source/emitter ── Arduino GND
```

Twist the two LED wires together along their whole length and route them away from the
headband's electrodes. That reduces electrical pickup, which would otherwise show up in
the EEG at exactly the pulse rate.

## Firmware

Open `hardware/ir_led_driver/ir_led_driver.ino` in the Arduino IDE and upload it. In the
serial monitor at 115200 baud it prints `READY ida-led 1`; typing `L` shows its
limits. The firmware refuses any pattern with more than 30 s of light-on time, enforces
a 0.5 s rest between patterns, caps brightness at MAX_PWM, and turns the LED off on
`X`. Its dimming runs at about 31 kHz, far above the EEG range.

Then in IDA Live: **Control › Test fire › List serial ports**, put the port (e.g.
`COM5`) into the knob `actuators.external_led.port`, and fire a test pattern.

## Safety

- 850 nm is invisible, so the eye has no blink or look-away reflex to it. Keep the LED
  against the forehead skin, never aimed at or near the eyes, and never look into it.
- Stay within the LED's rated current and check it stays cool to the touch after a long
  steady pattern.
- A single low-power LED at the skin is a very different thing from a laser or a
  photobiomodulation array. Don't substitute either without reading their safety data.
