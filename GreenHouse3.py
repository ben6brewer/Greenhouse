import time
import threading
from datetime import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT
from LCD import LCDDisplay
from CreateGraph import GraphGenerator
from SendEmail import EmailSender
from time import sleep
from LCD import LCDScreens
import sys
import select
import json

class GreenhouseController:
  def __init__(self):
    self.relay_pins = [24, 25]
    self.fan_pin = self.relay_pins[0]
    self.mist_pin = self.relay_pins[1]
    self.lowest_temp = 65 # degrees F
    self.highest_temp = 80 # degrees F
    self.lowest_humidity = 80 # %
    self.highest_humidity = 90 # %
    self.graph_generator = GraphGenerator() # Instantiate the GraphGenerator class
    self.email_sender = EmailSender()
    self.lcd_display = LCDDisplay(controller=self)
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
    
    self.minutes_elapsed = self.get_minutes_elapsed()
    self.relative_count = 0
    self.system_activated = False
    
    self.humidity = 0
    self.temperature = 0
    
    self.my_json_file = "GreenHouseData.json"
    
    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(self.fan_pin, GPIO.OUT)
    GPIO.setup(self.mist_pin, GPIO.OUT)
  
  def main(self):
    try:
      self.run_lcd()
      while True:
        self.check_user_input()
        if self.first_iteration_check():
          self.send_boot_message()
          
          self.update_time()
          self.update_variables()
          # TRUE every 1 minute
          if self.minute_check():
            self.minute_operations()
            
            # True every 10 minutes:
            if self.ten_minute_check():
              self.ten_minute_operations()
              
              # TRUE every 1 HOUR
              if self.hour_check():
                self.hour_operations()
                
                # TRUE every 1 day
                if self.day_check():
                  self.day_operations()
                  
          self.system_activated = False
          if self.humidity_check():
          self.activate_humidity()
          
          if self.temperature_check():
          self.activate_fans()
          
          if self.system_activated == False:
          sleep(2)
    
    except KeyboardInterrupt:
      pass
    
    GPIO.cleanup()
  
  @staticmethod
  def get_current_temperature():
    return round((Adafruit_DHT.read_retry(22, 4)[1]) * 9/5 + 32, 2)
  
  @staticmethod
  def get_current_humidity():
    return round(Adafruit_DHT.read_retry(22, 4)[0], 2)
  
  # Turns pump on for parameterized seconds
  def pump_on(self, seconds):
    GPIO.output(self.mist_pin, 0)
    sleep(seconds)
    GPIO.output(self.mist_pin, 1)
  
  
  # Turns pump on for parameterized seconds
  def fans_on(self, seconds):
    GPIO.output(self.fan_pin, 0)
    sleep(seconds)
    GPIO.output(self.fan_pin, 1)
  
  def get_minutes_elapsed(self):
    with open(self.my_json_file, "r") as file:
      data = json.load(file)
      self.minutes_elapsed = data.get("minutes", 0) # Use 0 as default if "minutes" key not found
    return self.minutes_elapsed
  
  def get_days_elapsed(self):
    return round(self.get_minutes_elapsed() / 1440, 2)
  
  def update_time(self):
    self.current_second = int(time.time() % 60)
    self.current_minute = int(time.time() // 60) % 60
    self.current_hour = int(time.time() // 3600) % 24
  
  def update_variables(self):
    self.humidity = self.get_current_humidity()
    self.temperature = self.get_current_temperature()
  
  def minute_check(self):
    return (self.last_minute is None or self.last_minute != self.current_minute)
  
  def minute_operations(self):
    self.last_minute = self.current_minute
    temperature = self.get_current_temperature()
    humidity = self.get_current_humidity()
  
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    
    data["TemperatureMinuteData"].append(temperature)
    data["HumidityMinuteData"].append(humidity)
    
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4)
  
  def ten_minute_check(self):
    return ((self.program_start_minute % 10) == (self.current_minute % 10))
  
  def ten_minute_operations(self):
    self.fans_on(45)
    sleep(45)
    self.add_minutes(10)
  
  def first_iteration_check(self):
    return (self.relative_count == 0)
  
  def send_boot_message(self):
    self.email_sender.send_boot_email(self.get_days_elapsed())
  
  def hour_check(self):
    return ((self.program_start_minute) == (self.current_minute))
  
  def hour_operations(self):
    avg_temperature = self.get_current_temperature()
    avg_humidity = self.get_current_humidity()
    
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    
    data["TemperatureMinuteData"].append(temperature)
    data["HumidityMinuteData"].append(humidity)
    
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4)
  
  def reset_minute_temperature_data(self):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    
    data["TemperatureMinuteData"] = [] # Reset the array to be empty
    
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4) # Write the updated data back to the JSON file
  
  def reset_minute_humidity_data(self):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    
    data["HumidityMinuteData"] = [] # Reset the array to be empty
    
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4) # Write the updated data back to the JSON file
  
  def reset_hour_temperature_data(self):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
  
    data["TemperatureHourData"] = [] # Reset the array to be empty
    
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4) # Write the updated data back to the JSON file
  
  def reset_hour_humidity_data(self):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    
    data["HumidityHourData"] = [] # Reset the array to be empty
    
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4) # Write the updated data back to the JSON file
  
  def hour_operations(self):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    
    temperature_data = data["TemperatureMinuteData"]
    average_temperature = round(sum(temperature_data) / len(temperature_data), 2)
    self.reset_minute_temperature_data()
    
    humidity_data = data["HumidityMinuteData"]
    average_humidity = round(sum(humidity_data) / len(humidity_data), 2)
    self.reset_minute_humidity_data()
    
    data["TemperatureHourData"].append(average_temperature)
    data["HumidityHourData"].append(average_humidity)
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4) # Write the updated data back to the JSON file
    self.relative_count += 1
  
  def day_check(self):
    return (self.program_start_hour == self.current_hour and self.relative_count > 1)
  
  def day_operations(self):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    temperature_hour_data = data.get("TemperatureHourData", [])
    humidity_hour_data = data.get("HumidityHourData", [])
    self.graph_generator.create_graph(self.get_days_elapsed(), [temperature_hour_data, humidity_hour_data])
    self.email_sender.send_email(self.get_days_elapsed())
    self.reset_hour_temperature_data()
    self.reset_hour_humidity_data()
  
  def humidity_check(self):
    return (self.humidity <= self.lowest_humidity)
  
  def activate_humidity(self):
    if self.get_current_humidity() < (self.lowest_humidity - 20):
      self.pump_on(30)
    elif self.get_current_humidity() < (self.lowest_humidity - 10):
      self.pump_on(20)
    else:
      self.pump_on(5)
    sleep(10)
    self.system_activated = True
  
  def temperature_check(self):
    return (self.temperature >= self.highest_temp or self.humidity >= self.highest_humidity)
  
  def activate_fans(self):
    if self.get_current_humidity() > self.highest_humidity:
      self.fans_on(20)
    elif self.get_current_temperature() > (self.highest_temp):
      self.fans_on(20)
    else:
      self.fans_on(10)
    self.system_activated = True
  
  def lcd_updater(self):
    current_screen = LCDScreens.SCREEN1
    
    while True:
      if current_screen == LCDScreens.SCREEN1:
        self.lcd_display.screen1(self.get_current_temperature(), self.get_current_humidity())
      
      elif current_screen == LCDScreens.SCREEN2:
        self.lcd_display.screen2(self.get_minutes_elapsed())
    
    # Switch to the next screen
    current_screen = LCDScreens.SCREEN1 if current_screen == LCDScreens.SCREEN2 else current_screen + 1
    sleep(5) # Adjust the delay time as needed (in seconds)
  
  def run_lcd(self):
    self.lcd_thread = threading.Thread(target=self.lcd_updater)
    self.lcd_thread.daemon = True
    self.lcd_thread.start()
  
  def reset_greenhouse_data(self):
    data = {
    "minutes": 0,
    "TemperatureMinuteData": [],
    "HumidityMinuteData": [],
    "TemperatureHourData": [],
    "HumidityHourData": [],
    }
  
    with open(self.my_json_file, 'w') as file:
      json.dump(data, file, indent=4)
  
  
  def add_minutes(self, minutes_to_add):
    with open(self.my_json_file, 'r') as file:
      data = json.load(file)
    data["minutes"] += minutes_to_add
    
    with open(self.my_json_file, 'w') as file:
    json.dump(data, file, indent=4)
  
  def check_user_input(self):
  
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    
    if rlist:
      user_input = sys.stdin.readline().strip()
      if user_input:
        words = user_input.split()
        val = None
        if words[-1].isdigit():
          val = int(words.pop())
        command = ' '.join(words)
        if command == 'read vars':
          print('temperature: ' + str(self.get_current_temperature()) + ' F')
          print('humidity: ' + str(self.get_current_humidity()) + ' %')
        elif command == 'get time':
          weeks = self.minutes_elapsed // 10080 # 10080 minutes = 7 days (1 week)
          remaining_minutes = self.minutes_elapsed % 10080
          days = remaining_minutes // 1440 # 1440 minutes = 1 day
          remaining_minutes %= 1440
          hours = remaining_minutes // 60 # 60 minutes = 1 hour
          minutes = remaining_minutes % 60
          print(f'Week: {weeks}, Day: {days}, Hour: {hours}, Minute: {minutes}')
        elif command == 'stall':
          print('sleeping for ' + str(val) + ' seconds')
          sleep(val)
          print('done sleeping')
        elif command == 'set minutes':
          print('overwritting ' + str(val) + ' minutes to Minutes.txt')
          with open("Minutes.txt", "w") as file:
            for day in range(0, val + 1, 10):
              file.write(str(day) + '\n')
          print('minutes.txt updated')
        elif command == 'pump on':
          GPIO.output(self.mist_pin, 0)
          print('pump on for ' + str(val) + ' seconds')
          sleep(val)
          GPIO.output(self.mist_pin, 1)
          print('pump off')
        elif command == 'fans on':
          GPIO.output(self.fan_pin, 0)
          print('fans on for ' + str(val) + ' seconds')
          sleep(val)
          GPIO.output(self.fan_pin, 1)
          print('fans off')
        elif command == 'pump off':
        GPIO.output(self.mist_pin, 1)
          print('pump off')
          elif command == 'fans off':
          GPIO.output(self.fan_pin, 1)
        print('fans off')
        elif command == 'set lowest humidity':
          print('setting lowest humidity to ' + str(val) + '%')
          self.lowest_humidity = val
          print('updated self.lowest_humidity')
        elif command == 'set highest humidity':
          print('setting highest humidity to ' + str(val) + '%')
          self.highest_humidity = val
          print('updated self.highest_humidity')
        elif command == 'set lowest temperature':
          print('setting lowest temp to ' + str(val) + 'F')
          self.lowest_temp = val
          print('updated self.lowest_temp')
        elif command == 'set highest temperature':
          print('setting highest temp to ' + str(val) + 'F')
          self.highest_temp = val
          print('updated self.highest_temp')
        elif command == 'AGT preset':
          self.lowest_temp = 63
          self.highest_temp = 80
          self.lowest_humidity = 80
          self.highest_humidity = 90
          with open("Minutes.txt", "w") as file:
            for day in range(0, 1, 10):
              file.write(str(day) + '\n')
          print(f'temp range: {self.lowest_temp}-{self.highest_temp}, humidity range {self.lowest_humidity}-{self.highest_humidity}')
          print('Reset Minutes.txt to 0')
        elif command == 'SG preset':
          self.lowest_temp = 60
          self.highest_temp = 80
          self.lowest_humidity = 40
          self.highest_humidity = 55
          with open("Minutes.txt", "w") as file:
            for day in range(0, 1, 10):
              file.write(str(day) + '\n')
          print(f'temp range: {self.lowest_temp}-{self.highest_temp}, humidity range {self.lowest_humidity}-{self.highest_humidity}')
          print('Reset Minutes.txt to 0')
        elif command == 'reset':
          print('clearing data')
          self.reset_greenhouse_data()
          print('data cleared')
        else:
          print()
          print('list valid requests:')
          print()
          print('GETTERS / SETTERS:')
          print('get vars - gets temperature and humidity')
          print('get time - gets current time statistics')
          print('stall (seconds) - stalls for x amount of seconds')
          print('set minutes (minutes) - set the minutes elapsed')
          print('set lowest humidity (%) - updates self.lowest_humidity')
          print('set highest humidity (%) - updates self.highest_humidity')
          print('set lowest temperature (F) - updates self.lowest_temp')
          print('set highest temperature (F) - updates self.highest_temp')
          print()
          print('HARDWARE CONTROLS:')
          print('pump on (seconds) - turns humidifier on for x seconds')
          print('fans on (seconds) - turns fans on for x seconds')
          print('pump off - turns humidifier off')
          print('fans off - turns fans off')
          print()
          print('PRESET GROWING CONDITIONS:')
          print('AGT preset - ideal growing conditions for AGT')
          print('SG preset - ideal growing conditions for Super Greens')
          print()
          print('SYSTEM RESET')
          print('reset - clears the json storage file')
  
controller = GreenhouseController()
controller.main()
