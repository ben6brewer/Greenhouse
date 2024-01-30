'''
Author: Ben Brewer
Date: 7/20/2023
Description: This is the main file for the Greenhouse Controller. It will run the main loop and call the other classes
'''
import time
import threading
from datetime import datetime
from DataCommands import DataCommands
import RPi.GPIO as GPIO
import Adafruit_DHT
from LCD import LCDDisplay
from CreateGraph import GraphGenerator
from SendEmail import EmailSender
from UserInput import ParseUserInput
from Camera import Camera
from time import sleep
from LCD import LCDScreens
from Hardware import Hardware
import sys
import select
import json
import os

class GreenhouseController:
    def __init__(self):
        self.lowest_temp = 65 # degrees F
        self.highest_temp = 80 # degrees F
        self.lowest_humidity =  90# %
        self.highest_humidity = 100 # %
        self.graph_generator = GraphGenerator() # Instantiate the GraphGenerator class
        self.email_sender = EmailSender()
        self.data = DataCommands()
        self.input = ParseUserInput()
        self.camera = Camera()
        self.hardware = Hardware()
        self.lcd_display = LCDDisplay(controller=self)
        self.minute_temperature_data = []
        self.minute_humidity_data = []
        self.hour_temperature_data = []
        self.hour_humidity_data = []

        self.current_minute = int(time.time() // 60) % 60
        self.last_minute = None
        self.program_start_minute = int(time.time() // 60) % 60

        
        self.program_start_ten_minute = int(time.time() // 60) % 60

        self.startup_email_sent = False
        self.system_activated = False

        self.humidity = 0
        self.temperature = 0
        
        # path to json = '/home/ben6brewer/Desktop/Greenhouse/data.json'

    def main(self):
        #starts gpio as off
        self.hardware.mist_off()
        self.hardware.fan_off()
        self.hardware.led_off()
        
        try:
            self.run_lcd()
            while True:
                #self.hardware.led_on()
                #sleep(500)
                self.input.check_user_input()
                if not self.first_iteration_check():
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



    '''
    Function:    pump_on
    Description: This function turns the pump on for the parameterized seconds
    Parameters:  seconds - the number of seconds to turn the pump on for
    '''
    def pump_on(self, seconds):
        self.hardware.mist_on()
        sleep(seconds)
        self.hardware.mist_off()
        self.data.add_to_total_pump_time(seconds)
        if self.data.get_total_pump_time() > 2000:
            self.email_sender.send_pump_warning(self.data.get_total_pump_time())
            self.data.reset_total_pump_time()


    '''
    Function:    fans_on
    Description: This function turns the fans on for the parameterized seconds
    Parameters:  seconds - the number of seconds to turn the fans on for
    '''
    def fans_on(self, seconds):
        self.hardware.fan_on()
        sleep(seconds)
        self.hardware.fan_off()

    '''
    Function:    update_time
    Description: This function updates the current time variables
    Parameters:  None
    '''
    def update_time(self):
        self.current_minute = int(time.time() // 60) % 60
        self.current_hour = int(time.time() // 3600) % 24

    '''
    Function:   update_variables
    Description: This function updates the current temperature and humidity variables
    Parameters:  None
    '''
    def update_variables(self):
        self.humidity = self.data.get_current_humidity()
        self.temperature = self.data.get_current_temperature()

    '''
    Function:    minute_check
    Description: This function checks if the current time is a new minute
    Parameters:  None
    '''
    def minute_check(self):
        if (self.last_minute is None or self.last_minute != self.current_minute):
            self.last_minute = self.current_minute
            return True
        return False

    '''
    Function:   minute_operations
    Description: This function performs the operations that need to be done every minute
    Parameters:  None
    '''
    def minute_operations(self):
        self.data.append_temperature_to_minute_array(self.temperature)
        self.data.append_humidity_to_minute_array(self.humidity)
        self.data.update_minutes_in_json(1)

    '''
    Function:    ten_minute_check
    Description: This function checks if the current time is a new 10 minute interval
    Parameters:  None
    '''
    def ten_minute_check(self):
        return ((self.current_minute % 10) == (self.program_start_ten_minute % 10))

    '''
    Function:   ten_minute_operations
    Description: This function performs the operations that need to be done every 10 minutes
    Parameters:  None
    '''
    def ten_minute_operations(self):
        self.fans_on(30)
        self.hardware.led_on()
        sleep(1)
        path = self.camera.capture_image([self.data.get_days_elapsed(), self.data.get_current_temperature(), self.data.get_current_humidity()])
        self.email_sender.send_image(path)
        self.hardware.led_off()

    '''
    Function:   first_iteration_check
    Description: This function checks if the program has been run before
    Parameters:  None
    '''
    def first_iteration_check(self):
        return self.startup_email_sent

    '''
    Function:    send_boot_message
    Description: This function sends an email to the user when the program is first run
    Parameters:  None
    '''
    def send_boot_message(self):
        print('got into boot')
        self.email_sender.send_boot_email()
        self.startup_email_sent = True

    '''
    Function:    hour_check
    Description: This function checks if the current time is a new hour
    Parameters:  None
    '''
    def hour_check(self):
        return ((self.current_minute % 60) == (self.program_start_minute % 60))

    '''
    Function:   hour_operations
    Description: This function performs the operations that need to be done every hour
    Parameters:  None
    '''
    def hour_operations(self):
        average_temperature = round((sum(self.data.get_temperature_minute_array())) / len(self.data.get_temperature_minute_array()), 2)
        self.data.append_temperature_to_hour_array(average_temperature)

        average_humidity = round((sum(self.data.get_humidity_minute_array())) / len(self.data.get_humidity_minute_array()), 2)
        self.data.append_humidity_to_hour_array(average_humidity)

        self.data.reset_minute_arrays()
        self.last_hour_operations = self.current_hour  # Update last_hour_operations
        self.data.update_hours_in_json(1)

    '''
    Function:    day_check
    Description: This function checks if the current time is a new day
    Parameters:  None
    '''
    def day_check(self):
        hours_elapsed = self.data.get_hours_elapsed()
        return (hours_elapsed == 24)

    '''
    Function:   day_operations
    Description: This function performs the operations that need to be done every day
    Parameters:  None
    '''
    def day_operations(self):
        self.graph_generator.create_graph(self.data.get_days_elapsed(), [self.data.get_temperature_hour_array(), self.data.get_humidity_hour_array()])
        self.email_sender.send_graph()
        self.data.reset_hour_arrays()
        self.data.reset_hours()

    '''
    Function:    humidity_check
    Description: This function checks if the current humidity is below the lowest humidity
    Parameters:  None
    '''
    def humidity_check(self):
        return (self.data.get_current_humidity() <= self.lowest_humidity)

    '''
    Function:   activate_humidity
    Description: This function activates the humidity system
    Parameters:  None
    '''
    def activate_humidity(self):
        while self.humidity_check():
            self.pump_on(60)
        self.system_activated = True

    '''
    Function:    temperature_check
    Description: This function checks if the current temperature is above the highest temperature or if the current humidity is above the highest humidity
    Parameters:  None
    '''
    def temperature_check(self):
        return (self.temperature >= self.highest_temp or self.humidity >= self.highest_humidity)

    '''
    Function:   activate_fans
    Description: This function activates the fans
    Parameters:  None
    '''
    def activate_fans(self):
        if self.data.get_current_humidity() > self.highest_humidity:
            self.fans_on(20)
        elif self.data.get_current_temperature() > (self.highest_temp):
            self.fans_on(20)
        else:
            self.fans_on(10)
        self.system_activated = True

    '''
    Function:    lcd_updater
    Description: This function updates the LCD screen
    Parameters:  None
    '''
    def lcd_updater(self):
        current_screen = LCDScreens.SCREEN1

        while True:
            if current_screen == LCDScreens.SCREEN1:
                self.lcd_display.screen1(self.data.get_current_temperature(), self.data.get_current_humidity())

            elif current_screen == LCDScreens.SCREEN2:
                self.lcd_display.screen2(self.data.get_minutes_elapsed())

            # Switch to the next screen
            current_screen = LCDScreens.SCREEN1 if current_screen == LCDScreens.SCREEN2 else current_screen + 1
            sleep(5) # Adjust the delay time as needed (in seconds)

    '''
    Function:    run_lcd
    Description: This function starts the LCD thread
    Parameters:  None
    '''
    def run_lcd(self):
        self.lcd_thread = threading.Thread(target=self.lcd_updater)
        self.lcd_thread.daemon = True
        self.lcd_thread.start()

    

controller = GreenhouseController()
controller.main()  