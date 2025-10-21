try:
    from smbus import SMBus
except ImportError:
    from smbus2 import SMBus
from time import sleep

class LCD:
    """
    Classe para controlar um display LCD 16x2 via I2C no Raspberry Pi.
    Uso:
        display = LCD(address=0x27)
        display.write("Ola Mundo!", line=1)
    """

    # Constantes LCD
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_FUNCTIONSET = 0x20
    LCD_ENTRYLEFT = 0x02
    LCD_DISPLAYON = 0x04
    LCD_2LINE = 0x08
    LCD_5x8DOTS = 0x00
    LCD_4BITMODE = 0x00
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    En = 0b00000100  # Enable bit
    Rw = 0b00000000  # Read/Write bit (mantido em 0)
    Rs = 0b00000001  # Register select bit

    def __init__(self, address=0x27, port=1):
        """Inicializa o LCD no endereço I2C especificado."""
        self.address = address
        self.bus = SMBus(port)
        self._init_lcd()

    def _write_cmd(self, cmd):
        self.bus.write_byte(self.address, cmd)
        sleep(0.0001)

    def _strobe(self, data):
        self._write_cmd(data | self.En | self.LCD_BACKLIGHT)
        sleep(0.0005)
        self._write_cmd((data & ~self.En) | self.LCD_BACKLIGHT)
        sleep(0.0001)

    def _write_four_bits(self, data):
        self._write_cmd(data | self.LCD_BACKLIGHT)
        self._strobe(data)

    def _write(self, cmd, mode=0):
        self._write_four_bits(mode | (cmd & 0xF0))
        self._write_four_bits(mode | ((cmd << 4) & 0xF0))

    def _init_lcd(self):
        """Inicializa a sequência padrão do LCD."""
        sleep(0.1)
        self._write(0x03)
        sleep(0.1)
        self._write(0x03)
        sleep(0.1)
        self._write(0x03)
        sleep(0.1)
        self._write(0x02)
        self._write(self.LCD_FUNCTIONSET | self.LCD_2LINE | self.LCD_5x8DOTS | self.LCD_4BITMODE)
        self._write(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        self._write(self.LCD_CLEARDISPLAY)
        self._write(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT)
        sleep(0.2)

    def clear(self):
        """Limpa o display."""
        self._write(self.LCD_CLEARDISPLAY)
        self._write(self.LCD_RETURNHOME)
        sleep(0.2)

    def backlight(self, state=True):
        """Liga (True) ou desliga (False) o backlight."""
        self._write_cmd(self.LCD_BACKLIGHT if state else self.LCD_NOBACKLIGHT)

    def _set_line(self, line):
        """Define posição da linha."""
        if line == 1:
            self._write(0x80)
        elif line == 2:
            self._write(0xC0)
        elif line == 3:
            self._write(0x94)
        elif line == 4:
            self._write(0xD4)

    def write(self, text, line=1):
        """
        Escreve um texto no display.
        Exemplo: display.write("Ola Mundo!", line=1)
        """
        self._set_line(line)
        for char in text.ljust(16)[:16]:  # Garante 16 caracteres por linha
            self._write(ord(char), self.Rs)