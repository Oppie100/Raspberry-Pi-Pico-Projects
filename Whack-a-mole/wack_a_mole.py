from machine import Pin, PWM, I2C
from time import sleep
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# === Pins Setup ===
button = Pin(14, Pin.IN, Pin.PULL_DOWN)   # Button on GP14
buzzer = PWM(Pin(16))                      # Passive buzzer on GP16

# I2C LCD on GP0 (SDA), GP1 (SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
LCD_ADDR = 39  # Replace with your i2c.scan() result
lcd = I2cLcd(i2c, LCD_ADDR, 2, 16)

# === Mole animation frames ===
frame1 = bytearray([
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
])

frame2 = bytearray([
    0b00100,
    0b01110,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
])

frame3 = bytearray([
    0b00100,
    0b01110,
    0b10101,
    0b11111,
    0b10101,
    0b00100,
    0b01010,
    0b10001
])

# Load custom chars
lcd.custom_char(0, frame1)
lcd.custom_char(1, frame2)
lcd.custom_char(2, frame3)

def buzz(freq=1000, duration=0.3):
    buzzer.freq(freq)
    buzzer.duty_u16(40000)  # Volume
    sleep(duration)
    buzzer.duty_u16(0)

def mole_animation():
    lcd.move_to(0, 1)
    lcd.putchar(chr(0))
    sleep(0.15)
    lcd.move_to(0, 1)
    lcd.putchar(chr(1))
    sleep(0.15)
    lcd.move_to(0, 1)
    lcd.putchar(chr(2))
    sleep(0.3)
    lcd.move_to(0, 1)
    lcd.putchar(chr(1))
    sleep(0.15)
    lcd.move_to(0, 1)
    lcd.putchar(chr(0))
    sleep(0.15)

def wait_for_start():
    lcd.clear()
    lcd.putstr("Press button to\nstart game!")
    while True:
        if button.value() == 1:
            buzz(1000, 0.2)
            lcd.clear()
            lcd.putstr("Starting...")
            sleep(1)
            break
        sleep(0.1)

# === Game parameters ===
score = 0
base_time = 3.0        # Starting mole pop-up time (seconds)
min_time = 0.8         # Minimum mole pop-up time (fastest)
level_up_every = 5     # Increase level every 5 points

lcd.clear()
lcd.putstr("Whack-a-Mole!")
sleep(1)

wait_for_start()

try:
    while True:
        # Calculate current level and mole pop-up time
        level = score // level_up_every + 1
        mole_time = max(min_time, base_time - (level - 1) * 0.3)

        lcd.clear()
        lcd.putstr(f"Level: {level} Score: {score}")
        sleep(1)

        mole_up = True
        lcd.clear()
        lcd.putstr("Mole is UP!")
        mole_animation()
        lcd.putstr("\nPress button!")

        # Check button presses during mole_time seconds (in 0.1s intervals)
        for _ in range(int(mole_time * 10)):
            if button.value() == 1:
                score += 1
                buzz(1500, 0.15)
                lcd.clear()
                lcd.putstr(f"Hit! Score:\n{score}")
                mole_up = False
                sleep(1)
                break
            sleep(0.1)

        if mole_up:
            buzz(500, 0.5)
            lcd.clear()
            lcd.putstr(f"Missed!\nScore: {score}")
            sleep(1)

except KeyboardInterrupt:
    lcd.clear()
    lcd.putstr(f"Game Over\nScore: {score}")
    buzzer.duty_u16(0)
