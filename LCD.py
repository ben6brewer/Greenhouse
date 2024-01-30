'''
Author:      Ben Brewer
Date:        8/1/2023
Description: This file contains the LCD class which is used to display information on the LCD screen.
'''
from rpi_lcd import LCD
import threading
from time import sleep

class LCDScreens:
    SCREEN1 = 1
    SCREEN2 = 2
    
class LCDDisplay:
    def __init__(self, controller):
        self.lcd = LCD()

    '''
    Function:    screen1
    Description: This function displays the temperature and humidity on the LCD screen.
    Parameters:  temperature - The temperature to display on the LCD screen.
                 humidity - The humidity to display on the LCD screen.   
    '''
    def screen1(self, temperature, humidity):
        self.lcd.clear()
        self.lcd.text(f"Temp:  {temperature} F", 1)
        self.lcd.text(f"Humid: {humidity} %", 2)

    '''
    Function:    screen2
    Description: This function displays the time elapsed since the last watering on the LCD screen.
    Parameters:  minutes_elapsed - The number of minutes elapsed since the start of the program.
    '''
    def screen2(self, minutes_elapsed):
        self.lcd.clear()

        # Calculate weeks, days, hours, and minutes
        weeks = minutes_elapsed // 10080  # 10080 minutes = 7 days (1 week)
        remaining_minutes = minutes_elapsed % 10080

        days = remaining_minutes // 1440  # 1440 minutes = 1 day
        remaining_minutes %= 1440

        hours = remaining_minutes // 60  # 60 minutes = 1 hour
        minutes = remaining_minutes % 60

        # Display the information on the LCD
        line1 = f"Week: {weeks}, Day: {days}"
        if hours >= 10:
            line2 =f"Hr:  {hours}, Min: {minutes}"
        else:
            line2 =f"Hr:   {hours}, Min: {minutes}"

        self.lcd.text(line1, 1)
        self.lcd.text(line2, 2)