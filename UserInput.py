'''
Author:      Ben Brewer
Date:        7/29/2023
Description: This file is responsible for parsing user input from the command line.
'''
import sys
import select
import json
import os
import time
from SendEmail import EmailSender
from DataCommands import DataCommands
import Adafruit_DHT
from time import sleep
from CreateGraph import GraphGenerator
from Hardware import Hardware

class ParseUserInput:
    def __init__(self):
        self.graph_generator = GraphGenerator()
        self.email_sender = EmailSender()
        self.data = DataCommands()
        self.hardware = Hardware()
    
    '''
    Function:    check_user_input
    Description: This function checks for user input from the command line, parses it, and performs the appropriate action.
    Parameters:  None
    '''
    def check_user_input(self):
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)

            if rlist:
                user_input = sys.stdin.readline().strip()
                if user_input:
                    words = user_input.split()
                    val = None
                if words[-1].isdigit() and user_input:
                    val = int(words.pop())
                command = ' '.join(words)
                if command == 'get vars':
                    print('temperature: ' + str(self.data.get_current_temperature()) + ' F')
                    print('humidity: ' + str(self.data.get_current_humidity()) + ' %')
                elif command == 'get time':
                    weeks = self.data.get_minutes_elapsed() // 10080 # 10080 minutes = 7 days (1 week)
                    remaining_minutes = self.data.get_minutes_elapsed() % 10080
                    days = remaining_minutes // 1440 # 1440 minutes = 1 day
                    remaining_minutes %= 1440
                    hours = remaining_minutes // 60 # 60 minutes = 1 hour
                    minutes = remaining_minutes % 60
                    print(f'Week: {weeks}, Day: {days}, Hour: {hours}, Minute: {minutes}')
                elif command == 'stall':
                    print('sleeping for ' + str(val) + ' seconds')
                    sleep(val)
                    self.data.update_minutes_in_json(val//60)
                    print('done sleeping')
                elif command == 'pump on':
                    self.hardware.mist_on()
                    print('pump on for ' + str(val) + ' seconds')
                    sleep(val)
                    self.hardware.mist_off()
                    print('pump off')
                elif command == 'fans on':
                    self.hardware.fan_on()
                    print('fans on for ' + str(val) + ' seconds')
                    sleep(val)
                    self.hardware.fan_off()
                    print('fans off')
                elif command == 'light on':
                    self.hardware.led_on()
                    print('lights on for ' + str(val) + ' seconds')
                    sleep(val)
                    self.hardware.led_off()
                    print('lights off')
                elif command == 'pump off':
                    self.hardware.mist_off()
                    print('pump off')
                elif command == 'fans off':
                    self.hardware.fan_off()
                    print('fans off')
                elif command == 'light off':
                    self.hardware.led_off()
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
                elif command == 'SG preset':
                    self.lowest_temp = 60
                    self.highest_temp = 80
                    self.lowest_humidity = 40
                    self.highest_humidity = 55
                    print(f'temp range: {self.lowest_temp}-{self.highest_temp}, humidity range {self.lowest_humidity}-{self.highest_humidity}')
                    print('Reset Minutes.txt to 0')
                    self.data.reset_json_data()
                elif command == 'reset':
                    print('clearing data')
                    self.data.reset_json_data()
                    print('data cleared')
                else:
                    self.valid_requests()
    
    '''
    Function:    valid_requests
    Description: This function prints out all of the valid requests that the user can make.
    Parameters:  None
    '''
    def valid_requests(self):
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
        print('light on (seconds) - turns lights on for x seconds')
        print('pump off - turns humidifier off')
        print('fans off - turns fans off')
        print('light off - turns lights off')
        print()
        print('PRESET GROWING CONDITIONS:')
        print('SG preset - ideal growing conditions for Super Greens')
        print()
        print('SYSTEM RESET')
        print('reset - clears the json storage file')