'''
Author:      Ben Brewer
Date:        7/29/2023
Description: This file contains the EmailSender class. This class is used to send emails to the user.
'''
import os
import shutil
import tempfile
import yagmail
import matplotlib.pyplot as plt
from CreateGraph import GraphGenerator
from DataCommands import DataCommands


class EmailSender:
    def __init__(self):
        self.username = "ben06brewer@gmail.com"
        self.password = "ckljvohlxaocohpx"
        self.graph_generator = GraphGenerator()
        self.data = DataCommands()

    '''
    Function:    send_graph
    Description: This function sends an email to the user with the graph for the current day.
    Parameters:  None
    '''
    def send_graph(self):
        days_elapsed = self.data.get_days_elapsed()
        print("Email for day " + str(days_elapsed) + " sent")

        directory = f'/home/ben6brewer/Desktop/Greenhouse/Graphs/Day_{days_elapsed}_Graph.pdf'
        message = f"Day: {days_elapsed} Graph"
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f'Day_{days_elapsed}_Graph.pdf')

        plt.savefig(temp_file, format='pdf')
        yag = yagmail.SMTP(self.username, self.password)
        yag.send(
            to=self.username,
            subject="Daily Graph",
            contents=message,
            attachments=temp_file
        )
        os.remove(temp_file)
        shutil

    '''
    Function:    send_boot_email
    Description: This function sends an email to the user when the system boots up with the current day.
    Parameters:  None
    '''
    def send_boot_email(self):
        days_elapsed = self.data.get_days_elapsed()
        message = f"system booted up from day: {days_elapsed}"

        yag = yagmail.SMTP(self.username, self.password)
        yag.send(
            to=self.username,
            subject="Daily Graph",
            contents=message,
        )

    '''
    Function:    send_pump_warning
    Description: This function sends an email to the user when the pump has been running for too long.
    Parameters:  total_pump_time - the total amount of time the pump has been running
    '''    
    def send_pump_warning(self, total_pump_time):
        message = f"BIN OVERFLOW WARNING. Pump has been running for {total_pump_time} seconds."

        yag = yagmail.SMTP(self.username, self.password)
        yag.send(
            to=self.username,
            subject="Daily Graph",
            contents=message,
        )

    '''
    Function:    send_image
    Description: This function sends an email to the user with the most recent image taken of the greenhouse.
    Parameters:  None
    '''    
    def send_image(self, path_to_image):
        current_day = self.data.get_days_elapsed()
        message = f"Timelapse Picture for {current_day}"
        
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        img = plt.imread(path_to_image)
        
        ax.imshow(img)
        
        filename = f"day_{current_day}.jpg"
        
        plt.savefig(filename, format="jpg", bbox_inches='tight', pad_inches=0, dpi=300)
        
        yag = yagmail.SMTP(self.username, self.password)
        yag.send(
            to=self.username,
            subject="Timelapse",
            contents=message,
            attachments=filename
        )
        plt.close(fig)




