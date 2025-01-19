import smbus2

I2C_BUS = 1
bus = smbus2.SMBus(I2C_BUS)
AS5600_ADDR = 0x36

class AS5600Sensor:
    def __init__(self, address=AS5600_ADDR):
        self.address = address
        try:
            bus.read_byte_data(self.address, 0x0E)
        except Exception as e:
            print(f"AS5600 initialization error: {e}")

    def read_angle(self):
        try:
            angle_hi = bus.read_byte_data(self.address, 0x0E)
            angle_lo = bus.read_byte_data(self.address, 0x0F)
            raw_angle = (angle_hi << 8) | angle_lo
            angle_deg = (raw_angle / 4095.0) * 360.0
            return angle_deg
        except Exception as e:
            print(f"AS5600 read error: {e}")
            return 0.0