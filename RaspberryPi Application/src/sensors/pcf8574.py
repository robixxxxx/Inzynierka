import smbus2

I2C_BUS = 1
bus = smbus2.SMBus(I2C_BUS)
PCF8574_ADDR = 0x20

class PCF8574IOExpander:
    def __init__(self, address=PCF8574_ADDR):
        self.address = address
        try:
            self.state = 0x00
            bus.write_byte(self.address, self.state)
        except Exception as e:
            print(f"PCF8574 initialization error: {e}")

    def set_bit(self, bit, value):
        try:
            if value:
                self.state |= (1 << bit)
            else:
                self.state &= ~(1 << bit)
            bus.write_byte(self.address, self.state)
        except Exception as e:
            print(f"PCF8574 set_bit error: {e}")