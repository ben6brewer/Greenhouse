from rpi_lcd import LCD

class LCDDisplay:
    def __init__(self, controller):
        self.lcd = LCD()

    def screen1(self, temperature):
        self.lcd.clear()
        self.lcd.text(f"Temperature:", 1)
        self.lcd.text(f"{temperature} F", 2)

    def screen2(self, humidity):
        self.lcd.clear()
        self.lcd.text(f"Humidity:", 1)
        self.lcd.text(f"{humidity} %", 2)

    def screen3(self, days_elapsed):
        self.lcd.clear()
        self.lcd.text(f"Days:", 1)
        self.lcd.text(f"{days_elapsed}", 2)


