# Teste manual: liga 2s, desliga 2s e imprime estado final
import time
from light_controller import LightController

lc = LightController(pin=12)  # ajuste pin se necessário
print("Initial logical state:", lc.get_light_state())
print("Turning ON for 3s...")
lc.turn_on()
time.sleep(3)
print("Turning OFF for 3s...")
lc.turn_off()
time.sleep(3)
print("Final logical state:", lc.get_light_state())
lc.cleanup()