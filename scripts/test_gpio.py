# Teste manual: liga 2s, desliga 2s e imprime estado final
import time
from src.light_controller import LightController

lc = LightController(pin=12)  # confirme pin (BCM)
lc.turn_on()
time.sleep(2)
lc.turn_off()
time.sleep(1)
print("light_state:", lc.get_light_state())