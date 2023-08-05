import os
import shutil
import tempfile
import yagmail
import matplotlib.pyplot as plt
from CreateGraph import GraphGenerator


class EmailSender:
    def __init__(self):
        self.username = "ben06brewer@gmail.com"
        self.password = "ckljvohlxaocohpx"
        self.graph_generator = GraphGenerator()

    def send_email(self, days_elapsed):
        print("Email for day " + str(days_elapsed) + " sent")

        directory = f'/home/ben6brewer/Desktop/Graphs/Day_{days_elapsed}_Graph.pdf'
        message = f"Daily greenhouse monitoring report. Here is the graph for Day {days_elapsed}"
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f'Day_{days_elapsed}_Graph.pdf')

        plt.savefig(temp_file, format='pdf')
        yag = yagmail.SMTP(self.username, self.password)
        yag.send(
            to=self.username,
            subject="Daily Greenhouse Graph",
            contents=message,
            attachments=temp_file
        )
        os.remove(temp_file)
        shutil
