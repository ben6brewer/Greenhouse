'''
Author:      Ben Brewer
Date:        7/29/2023
Description: This file contains the GraphGenerator class. This class is used to create a graph of the temperature
             and humidity data. All of the graphs are saved in the Graphs folder.
'''
import matplotlib.pyplot as plt
from DataCommands import DataCommands

class GraphGenerator:
    def __init__(self):
        self.data = DataCommands()
    
    '''
    Function:    create_graph
    Description: This function creates a graph of the temperature and humidity data
    Parameters:  days_elapsed - The number of days that have elapsed since the start of the experiment
                 data - The temperature and humidity data
    Return: None
    '''
    def create_graph(self, days_elapsed, data):
        temperature_data = data[0]
        humidity_data = data[1]
        plt.clf()
        time_array = list(range(len(temperature_data)))
        plt.plot(time_array, temperature_data, marker='o', label='Temperature')
        plt.plot(time_array, humidity_data, marker='o', label='Humidity')

        plt.xlabel('Time (hours)')
        plt.ylabel('Fahrenheit / Relative Humidity')
        plt.title('Greenhouse Day ' + str(days_elapsed))
        plt.legend()
        directory = f'/home/ben6brewer/Desktop/Greenhouse/Graphs/Day_{days_elapsed}_Graph.pdf'
        plt.savefig(directory, format='pdf')