import gpiozero

class indicator:
    def __init__(self, red_pin:int, green_pin:int):
        self.red = gpiozero.LED(red_pin)
        self.green = gpiozero.LED(green_pin)
        self.red.off()
        self.green.off()

    def setReady(self):
        self.red.off()
        self.green.on()
        return 'Ready'

    def setBusy(self):
        self.green.off()
        self.red.on()
        return 'Busy'

    def setOff(self):
        self.green.off()
        self.red.off()
        return 'Off'

if __name__ == '__main__':
    import time
    myind = indicator(red_pin=21, green_pin=26)
    print(f"Status: {myind.setReady()}")
    time.sleep(3)
    print(f"Status: {myind.setBusy()}")
    time.sleep(3)
    print(f"Status: {myind.setOff()}")

