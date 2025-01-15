import smbus2
import time

I2C_BUS = 1
bus = smbus2.SMBus(I2C_BUS)
MPU6500_ADDR = 0x68

class MPU6500Sensor:
    def __init__(self, address=MPU6500_ADDR):
        self.address = address
        try:
            bus.write_byte_data(self.address, 0x6B, 0x00)
            time.sleep(0.1)
        except Exception as e:
            print(f"MPU6500 initialization error: {e}")

    def read_acceleration(self):
        try:
            data = bus.read_i2c_block_data(self.address, 0x3B, 6)
            raw_ax = (data[0]<<8 | data[1])
            raw_ay = (data[2]<<8 | data[3])
            raw_az = (data[4]<<8 | data[5])
            def convert(val):
                if val > 32767: 
                    val -= 65536
                return val / 16384.0
            ax = convert(raw_ax)
            ay = convert(raw_ay)
            az = convert(raw_az)
            return {"accX": ax*9.81, "accY": ay*9.81, "accZ": az*9.81}
        except Exception as e:
            print(f"MPU6500 read error: {e}")
            return {"accX": 0.0, "accY": 0.0, "accZ": 0.0}