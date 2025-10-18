import RPi.GPIO as GPIO

class LightController:
    def __init__(self, pin=12):
        self.pin = pin
        self.light_state = False  # False means off, True means on
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # evita "channel already in use" warnings
        # opcional: chamar GPIO.cleanup() aqui se quiser garantir estado limpo
        # GPIO.cleanup()
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def turn_on(self):
        if not self.light_state:
            self.light_state = True
            GPIO.output(self.pin, GPIO.HIGH)
            print("Light turned ON")

    def turn_off(self):
        if self.light_state:
            self.light_state = False
            GPIO.output(self.pin, GPIO.LOW)
            print("Light turned OFF")

    def get_light_state(self):
        return self.light_state

    def cleanup(self):
        GPIO.cleanup()