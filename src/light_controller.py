import os
import time
import logging
from lcd_display import LCD

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

try:
    import RPi.GPIO as GPIO
except Exception:
    # mock para desenvolvimento
    class _MockGPIO:
        BCM = 'BCM'; OUT = 'OUT'; IN = 'IN'; LOW = 0; HIGH = 1
        def setmode(self, m): logger.info("[MockGPIO] setmode %s", m)
        def setwarnings(self, v): pass
        def setup(self, pin, mode): logger.info("[MockGPIO] setup pin=%s mode=%s", pin, mode)
        def output(self, pin, value): logger.info("[MockGPIO] output pin=%s value=%s", pin, value)
        def input(self, pin): return None
        def cleanup(self): logger.info("[MockGPIO] cleanup")
    GPIO = _MockGPIO()
    logger.warning("RPi.GPIO not available, using MockGPIO (no real GPIO control).")

class LightController:
    def __init__(self, pin=12, active_low=None):
        """
        pin: BCM pin number
        active_low: True if device is active when pin is LOW. If None, reads LIGHT_ACTIVE_LOW env var.
        """
        self.pin = pin
        self.light_state = False  # logical state
        env_val = os.getenv("LIGHT_ACTIVE_LOW", "").lower()
        if active_low is None:
            self.active_low = env_val in ("1", "true", "yes")
        else:
            self.active_low = bool(active_low)

        # define níveis físicos para ON/OFF
        if self.active_low:
            self.on_level = GPIO.LOW
            self.off_level = GPIO.HIGH
        else:
            self.on_level = GPIO.HIGH
            self.off_level = GPIO.LOW

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)
        # iniciar em OFF
        GPIO.output(self.pin, self.off_level)

        # nova flag: se True, ao desligar colocamos o pino como INPUT (emula cleanup)
        self.tristate_off = os.getenv("LIGHT_TRISTATE_OFF", "1").lower() in ("1", "true", "yes")

        logger.info("LightController initialized on pin %s (initial OFF), active_low=%s, on_level=%s off_level=%s tristate_off=%s",
                    self.pin, self.active_low, self.on_level, self.off_level, self.tristate_off)

    def turn_on(self):
        logger.info("turn_on called: ensuring pin %s is OUTPUT and writing on_level=%s", self.pin, self.on_level)
        display = LCD(address=0x27)  # troque o endereço se necessário (veja com i2cdetect)
        display.backlight(True)
        display.clear()
        
        display.write("Pisca Pisca", line=1)
        display.write("LIGADO!", line=2)

        try:
            # se estava em INPUT devido ao tristate-off, reconfigure como OUTPUT
            try:
                GPIO.setup(self.pin, GPIO.OUT)
            except Exception as e:
                logger.debug("Could not setup pin %s as OUTPUT before turn_on: %s", self.pin, e)
            GPIO.output(self.pin, self.on_level)
            time.sleep(0.02)
            GPIO.output(self.pin, self.on_level)
            logger.info("GPIO.output executed for pin %s -> %s", self.pin, self.on_level)
            try:
                level = GPIO.input(self.pin)
                logger.info("GPIO.input for pin %s returned: %s", self.pin, level)
            except Exception as e:
                logger.debug("GPIO.input not available/readable for pin %s: %s", self.pin, e)
        except Exception:
            logger.exception("Error writing to GPIO pin %s during turn_on", self.pin)

        if not self.light_state:
            logger.info("Light state changed: OFF -> ON")
        else:
            logger.info("Light already ON (pin re-set)")
        self.light_state = True

    def turn_off(self):
        logger.info("turn_off called: writing off_level=%s to pin %s", self.off_level, self.pin)
        display = LCD(address=0x27)  # troque o endereço se necessário (veja com i2cdetect)
        display.backlight(True)
        display.clear()
        
        display.write("Pisca Pisca", line=1)
        display.write("DESLIGADO!", line=2)
        try:
            # assegura modo OUTPUT antes do write (caso tenha sido tri-stated antes)
            try:
                GPIO.setup(self.pin, GPIO.OUT)
            except Exception:
                pass

            GPIO.output(self.pin, self.off_level)
            time.sleep(0.02)
            GPIO.output(self.pin, self.off_level)
            logger.info("GPIO.output executed for pin %s -> %s (double-write)", self.pin, self.off_level)

            try:
                level = GPIO.input(self.pin)
                logger.info("GPIO.input for pin %s returned: %s", self.pin, level)
            except Exception as e:
                logger.debug("GPIO.input not available/readable for pin %s: %s", self.pin, e)

            if self.tristate_off:
                # tente colocar o pino em INPUT (alta-impedância) — preferível a cleanup global
                try:
                    GPIO.setup(self.pin, GPIO.IN)
                    logger.info("Pin %s set to INPUT (tristate) to emulate cleanup off", self.pin)
                except Exception as e:
                    logger.warning("Could not set pin %s to INPUT, attempting GPIO.cleanup(pin): %s", self.pin, e)
                    try:
                        GPIO.cleanup(self.pin)
                        logger.info("GPIO.cleanup(pin) called for %s", self.pin)
                    except Exception as e2:
                        logger.exception("GPIO.cleanup(pin) also failed for %s: %s", self.pin, e2)

        except Exception:
            logger.exception("Error writing to GPIO pin %s during turn_off", self.pin)

        if self.light_state:
            logger.info("Light state changed: ON -> OFF")
        else:
            logger.info("Light already OFF (pin re-set)")
        self.light_state = False

    def get_light_state(self):
        return self.light_state

    def cleanup(self):
        logger.info("Cleaning up GPIO")
        try:
            GPIO.cleanup()
        except Exception:
            logger.exception("Error during GPIO.cleanup()")