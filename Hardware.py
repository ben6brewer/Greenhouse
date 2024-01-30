import time
import RPi.GPIO as GPIO

class Hardware:
    def __init__(self, mode=GPIO.BCM):
        self.LED_PIN = 24
        self.fan_pin = 23
        self.humidity_power_pin = 27
        self.humidity_mode_pin = 25
        
        # Set up GPIO pins
        GPIO.setmode(mode)
        GPIO.setwarnings(False)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.setup(self.humidity_power_pin, GPIO.OUT)
        GPIO.setup(self.humidity_mode_pin, GPIO.OUT)

    def led_on(self):
        GPIO.output(self.LED_PIN, 0)
        print('lights on')

    def led_off(self):
        GPIO.output(self.LED_PIN, 1)
        print('lights off')

    def fan_on(self):
        GPIO.output(self.fan_pin, 0)
        print('fans on')
        
    def fan_off(self):
        GPIO.output(self.fan_pin, 1)
        print('fans off')
    
    def mist_on(self):
        GPIO.output(self.humidity_power_pin, 0)
        time.sleep(1)
        GPIO.output(self.humidity_mode_pin, 0)
        time.sleep(1)
        GPIO.output(self.humidity_mode_pin, 1)
        print('mist on')
        
    def mist_off(self):
        GPIO.output(self.humidity_power_pin, 1)
        print('mist off')
