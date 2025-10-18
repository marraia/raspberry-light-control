import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

class LightController:
    def __init__(self, pin=12):
        self.pin = pin
        self.light_state = False  # False means off, True means on
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # evita "channel already in use" warnings
        # opcional: chamar GPIO.cleanup() aqui se quiser garantir estado limpo
        GPIO.cleanup()
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        logger.info("LightController initialized on pin %s (initial OFF)", self.pin)

    def turn_on(self):
        # sempre escrever no pino para garantir estado correto
        GPIO.output(self.pin, GPIO.LOW)
        logger.info("turn_on called: setting pin %s HIGH", self.pin)
        if not self.light_state:
            logger.info("Light state changed: OFF -> ON")
        else:
            logger.info("Light was already ON (pin re-set)")
        self.light_state = True

    def turn_off(self):
        logger.info("turn_off called: setting pin %s LOW", self.pin)
        try:
            GPIO.output(self.pin, GPIO.HIGH)
            logger.info("GPIO.output executed: pin %s -> LOW", self.pin)
            try:
                # lê o nível do pino para confirmar
                level = GPIO.input(self.pin)
                logger.info("GPIO.input for pin %s returned: %s", self.pin, level)
            except Exception as e:
                logger.warning("Could not read GPIO.input for pin %s: %s", self.pin, e)
        except Exception as e:
            logger.exception("Error writing to GPIO pin %s: %s", self.pin, e)

        if self.light_state:
            logger.info("Light state changed: ON -> OFF")
        else:
            logger.info("Light was already OFF (pin re-set)")

        self.light_state = False

    def get_light_state(self):
        return self.light_state

    def cleanup(self):
        logger.info("Cleaning up GPIO")
        GPIO.cleanup()