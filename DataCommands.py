'''
Author:      Ben Brewer
Date:        7/29/2023
Description: This file contains the DataCommands class. This class is used to edit the data.json file.
'''
import sys
import select
import json
import os
import Adafruit_DHT

class DataCommands:
    def __init__(self):
        pass
    
    '''
    Function:    get_current_temperature
    Description: This function returns the current temperature in Fahrenheit.
    Parameters:  None
    '''
    def get_current_temperature(self):
        return round((Adafruit_DHT.read_retry(22, 4)[1]) * 9/5 + 32, 2)

    '''
    Function:    get_current_humidity
    Description: This function returns the current humidity as a percentage.
    Parameters:  None
    '''
    def get_current_humidity(self):
        return round(Adafruit_DHT.read_retry(22, 4)[0], 2)
    
    '''
    Function:    get_minutes_elapsed
    Description: This function returns the number of minutes that have elapsed since the program started.
    Parameters:  None
    '''
    def get_minutes_elapsed(self):
            with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
                data = json.load(json_file)
                minutes_elapsed = data.get('minutes', 0)
                return minutes_elapsed

    '''
    Function:    get_hours_elapsed
    Description: This function returns the number of hours that have elapsed since the program started.
    Parameters:  None
    '''        
    def get_hours_elapsed(self):
            with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
                data = json.load(json_file)
                hours_elapsed = data.get('hours', 0)
                return hours_elapsed

    '''
    Function:    get_days_elapsed
    Description: This function returns the number of days that have elapsed since the program started.
    Parameters:  None
    '''        
    def get_days_elapsed(self):
        minutes = self.get_minutes_elapsed()
        day = minutes / 1440.0
        day = "{:.2f}".format(day)
        return day

    '''
    Function:    update_minutes_in_json
    Description: This function adds to the minutes in the data.json file.
    Parameters:  minutes_to_add - The number of minutes to add to the minutes in the data.json file.
    '''        
    def update_minutes_in_json(self, minutes_to_add):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            current_minutes = data.get('minutes', 0)
            new_minutes = current_minutes + minutes_to_add
            data['minutes'] = new_minutes
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    update_hours_in_json
    Description: This function adds to the hours in the data.json file.
    Parameters:  hours_to_add - The number of hours to add to the hours in the data.json file.
    '''      
    def update_hours_in_json(self, hours_to_add):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            current_hours = data.get('hours', 0)
            new_hours = current_hours + hours_to_add
            data['hours'] = new_hours
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:   reset_json_data
    Description: This function resets serves as the base for the data.json file.
    Parameters:  None
    '''
    def reset_json_data(self):
        data = {
        "minutes": 0,
        "TotalPumpTime": 0,
        "hours": 0,

        "TemperatureMinuteArray": [],
        "HumidityMinuteArray": [],
        "TemperatureHourArray": [],
        "HumidityHourArray": []
        }

        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

    '''
    Function:    append_temperature_to_minute_array
    Description: This function appends the current temperature to the TemperatureMinuteArray in the data.json file.
    Parameters:  temperature - The current temperature.
    '''
    def append_temperature_to_minute_array(self, temperature):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            temperature_array = data.get('TemperatureMinuteArray', [])
            temperature_array.append(temperature)
            data['TemperatureMinuteArray'] = temperature_array
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    append_humidity_to_minute_array
    Description: This function appends the current humidity to the HumidityMinuteArray in the data.json file.
    Parameters:  humidity - The current humidity.
    '''
    def append_humidity_to_minute_array(self, humidity):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json','r+') as json_file:
            data = json.load(json_file)
            humidity_array = data.get('HumidityMinuteArray', [])
            humidity_array.append(humidity)
            data['HumidityMinuteArray'] = humidity_array
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    append_temperature_to_hour_array
    Description: This function appends the current temperature to the TemperatureHourArray in the data.json file.
    Parameters:  temperature - The current temperature.
    '''
    def append_temperature_to_hour_array(self, temperature):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            temperature_array = data.get('TemperatureHourArray', [])
            temperature_array.append(temperature)
            data['TemperatureHourArray'] = temperature_array
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    append_humidity_to_hour_array
    Description: This function appends the current humidity to the HumidityHourArray in the data.json file.
    Parameters:  humidity - The current humidity.
    '''
    def append_humidity_to_hour_array(self, humidity):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            humidity_array = data.get('HumidityHourArray', [])
            humidity_array.append(humidity)
            data['HumidityHourArray'] = humidity_array
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    reset_minute_arrays
    Description: This function resets the minute arrays in the data.json file.
    Parameters:  None
    '''
    def reset_minute_arrays(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            data['TemperatureMinuteArray'] = []
            data['HumidityMinuteArray'] = []
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    reset_hour_arrays
    Description: This function resets the hour arrays in the data.json file.
    Parameters:  None
    '''
    def reset_hour_arrays(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            data['TemperatureHourArray'] = []
            data['HumidityHourArray'] = []
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    get_temperature_minute_array
    Description: This function returns the TemperatureMinuteArray from the data.json file.
    Parameters:  None
    '''
    def get_temperature_minute_array(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
            data = json.load(json_file)
            temperature_array = data.get('TemperatureMinuteArray', [])
            return temperature_array

    '''
    Function:    get_humidity_minute_array
    Description: This function returns the HumidityMinuteArray from the data.json file.
    Parameters:  None
    '''
    def get_humidity_minute_array(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
            data = json.load(json_file)
            humidity_array = data.get('HumidityMinuteArray', [])
            return humidity_array

    '''
    Function:    get_temperature_hour_array
    Description: This function returns the TemperatureHourArray from the data.json file.
    Parameters:  None
    '''
    def get_temperature_hour_array(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
            data = json.load(json_file)
            temperature_array = data.get('TemperatureHourArray', [])
            return temperature_array

    '''
    Function:    get_humidity_hour_array
    Description: This function returns the HumidityHourArray from the data.json file.
    Parameters:  None
    '''
    def get_humidity_hour_array(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
            data = json.load(json_file)
            humidity_array = data.get('HumidityHourArray', [])
            return humidity_array

    '''
    Function:    add_to_total_pump_time
    Description: This function adds the pump time to the TotalPumpTime in the data.json file.
    Parameters:  pump_time - The time the pump was on.
    '''
    def add_to_total_pump_time(self, pump_time):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            total_pump_time = data.get('TotalPumpTime', 0)
            total_pump_time += pump_time
            data['TotalPumpTime'] = total_pump_time
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()

    '''
    Function:    get_total_pump_time
    Description: This function returns the TotalPumpTime from the data.json file.
    Parameters:  None
    '''        
    def get_total_pump_time(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r') as json_file:
            data = json.load(json_file)
            total_pump_time = data.get('TotalPumpTime', 0)
            return total_pump_time

    '''
    Function:    reset_total_pump_time
    Description: This function resets the TotalPumpTime in the data.json file.
    Parameters:  None
    '''
    def reset_total_pump_time(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            data['TotalPumpTime'] = 0
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()
            
    '''
    Function:    reset_hours
    Description: This function resets the hours in the data.json file.
    Parameters:  None
    '''
    def reset_hours(self):
        with open('/home/ben6brewer/Desktop/Greenhouse/data.json', 'r+') as json_file:
            data = json.load(json_file)
            data['hours'] = 0
            json_file.seek(0)
            json.dump(data, json_file, indent=4)
            json_file.truncate()