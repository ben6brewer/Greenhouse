'''
Author:      Ben Brewer
Date:        8/13/2023
Description: This class is responsible for campturing images of the plants inside the greenhouse.
'''
import os
import picamera
from PIL import Image, ImageDraw, ImageFont

class Camera:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1080)
        self.font_path = "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf"

    def capture_image(self, data):
        filename = f'/home/ben6brewer/Desktop/Greenhouse/Pictures/day_{data[0]}.jpg'
        # Capture the image
        self.camera.capture(filename)
        
        # Open the captured image using Pillow
        img = Image.open(filename)
        #img = img.rotate(180)

        # Create a drawing context
        draw = ImageDraw.Draw(img)

        # Define the font and size for the text
        font = ImageFont.truetype(self.font_path, size=50)

        # Define the position to place the text
        text_position = (20, 20)

        # Format the data
        day, temperature, humidity = data

        # Create the text to be added to the image
        text = f"Day: {day}\nTemperature: {temperature} F\nHumidity: {humidity} %"

        draw.multiline_text(text_position, text, fill=(0, 0, 0), font=font)

        # Save the modified image (overwrite the original)
        img.save(filename)

        print(f"Image saved to {filename}")
        return filename

