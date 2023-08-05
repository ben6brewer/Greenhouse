import time
import threading
from datetime import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT
from LCD import LCDDisplay
from CreateGraph import GraphGenerator
from SendEmail import EmailSender
from time import sleep

class GreenhouseController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.relay_pins = [24, 25]
        self.fan_pin = self.relay_pins[0]
        self.mist_pin = self.relay_pins[1]
        self.lowest_temp = 65 # degrees F
        self.highest_temp = 80 # degrees F
        self.lowest_humidity = 80 # %
        self.highest_humidity = 90 # %
        self.graph_generator = GraphGenerator() # Instantiate the GraphGenerator class
        self.email_sender = EmailSender()
        self.lcd = LCDDisplay(controller=self)
        self.minute_temperature_data = []
        self.minute_humidity_data = []
        self.hour_temperature_data = []
        self.hour_humidity_data = []

        self.current_second = int(time.time() % 60)
        self.last_second = None

        self.current_minute = int(time.time() // 60) % 60
        self.last_minute = None
        self.program_start_minute = int(time.time() // 60) % 60

        self.current_hour = int(time.time() // 3600) % 24
        self.last_hour = None
        self.program_start_hour = int(time.time() // 3600) % 24

        self.days_elapsed = self.get_days_elapsed()
        self.system_delay = False

        self.lcd_counter = 1
        self.lcd_current_screen = None
        self.lcd_previous_screen = None
        # Set up GPIO pins as outputs
        GPIO.setwarnings(False)
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.setup(self.mist_pin, GPIO.OUT)

    def main(self):
        try:
            while True:
                self.current_second = int(time.time() % 60)
                self.current_minute = int(time.time() // 60) % 60
                self.current_hour = int(time.time() // 3600) % 24
                # TRUE every second
                if self.last_second is None or self.current_second % 0 == self.last_second % 0:
                    self.lcd_rotate()
                # TRUE every 1 minute
                if self.last_minute is None or self.last_minute != self.current_minute:
                    self.last_minute = self.current_minute
                    humidity = self.get_current_humidity()
                    temperature = self.get_current_temperature()

                    self.minute_temperature_data.append(temperature)
                    self.minute_humidity_data.append(humidity)
                    print("GH min data:" + str(self.minute_temperature_data))

                # TRUE every 1 HOUR % 2 for testing
                if self.program_start_minute == self.current_minute:
                    average_temperature = round((sum(self.minute_temperature_data)) / len(self.minute_temperature_data), 2)
                    self.hour_temperature_data.append(average_temperature)
                    print("GH hour data: " + str(self.hour_temperature_data))
                    self.minute_temperature_data = []

                    average_humidity = round((sum(self.minute_humidity_data)) / len(self.minute_humidity_data), 2)
                    self.hour_humidity_data.append(average_humidity)
                    self.minute_humidity_data = []

                    self.fans_on(30)

                # TRUE every 1 day % 4 for testing
                if self.program_start_hour == self.current_hour:
                    self.graph_generator.create_graph(self.days_elapsed, [self.hour_temperature_data, self.hour_humidity_data])
                    self.email_sender.send_email(self.days_elapsed)
                    self.hour_temperature_data = []
                    self.hour_humidity_data = []

                    self.days_elapsed += 1
                    with open("Days.txt", "w") as file:
                        for day in range(self.days_elapsed + 1):
                            file.write(str(day) + '\n')

                interval = 15
                self.system_activated = False
                if 'humidity' in locals() and humidity <= self.lowest_humidity:
                    self.pump_on(interval)
                    self.system_activated = True

                if 'humidity' in locals() and humidity >= self.highest_humidity:
                    self.pump_off(interval)
                    self.system_ = True

                if 'temperature' in locals() and temperature <= self.lowest_temp:
                    self.fans_off(interval)
                    self.system_delay = True

                if 'temperature' in locals() and temperature >= self.highest_temp:
                    self.fans_on(interval)
                    self.system_delay = True

                if self.system_delay == False:
                    sleep(5)
        except KeyboardInterrupt:
            pass

        GPIO.cleanup()

    @staticmethod
    def get_current_temperature():
        temperature = Adafruit_DHT.read_retry(22, 4)[1]
        return round(temperature * 9 / 5.0 + 32, 2)

    @staticmethod
    def get_current_humidity():
        humidity = Adafruit_DHT.read_retry(22, 4)[0]
        return round(humidity, 2)

    # Turns pump on for parameterized seconds
    def pump_on(self, seconds):
        GPIO.output(self.mist_pin, 0)
        sleep(seconds)
        GPIO.output(self.mist_pin, 1)

    # Turns pump off and increments parameterized seconds
    def pump_off(self, seconds):
        GPIO.output(self.mist_pin, 1)
        sleep(seconds)

    # Turns pump on for parameterized seconds
    def fans_on(self, seconds):
        GPIO.output(self.fan_pin, 0)
        sleep(seconds)
        GPIO.output(self.fan_pin, 1)

    # Turns fans off and increments parameterized seconds
    def fans_off(self, seconds):
        GPIO.output(self.fan_pin, 1)
        sleep(seconds)

    def lcd_rotate(self):
        if self.lcd_counter == 1:
            self.lcd.screen1(self.get_current_temperature())
            self.lcd_counter += 1
        elif self.lcd_counter == 2:
            self.lcd.screen2(self.get_current_humidity())
            self.lcd_counter += 1
        elif self.lcd_counter == 3:
            self.lcd.screen3(self.days_elapsed)
            self.lcd_counter = 1

    def get_days_elapsed(self):
        with open("Days.txt", "r") as file:
            lines = file.readlines()
            if lines:
                self.days_elapsed = int(lines[-1].strip())
        return self.days_elapsed

controller = GreenhouseController()
controller.main()
