from datetime import datetime
import smbus2

# constants

INA3221_ADDRESS = (0x40)
INA3221_READ = (0x01)

INA3221_REG_CONFIG = (0x00)
INA3221_CONFIG_RESET = (0x8000)  # Reset Bit
	
INA3221_CONFIG_ENABLE_CHAN1 = (0x4000)  # Enable Channel 1
INA3221_CONFIG_ENABLE_CHAN2 = (0x2000)  # Enable Channel 2
INA3221_CONFIG_ENABLE_CHAN3 = (0x1000)  # Enable Channel 3

INA3221_CONFIG_AVG2 = (0x0800)  # AVG Samples Bit 2 - See table 3 spec
INA3221_CONFIG_AVG1 = (0x0400)  # AVG Samples Bit 1 - See table 3 spec
INA3221_CONFIG_AVG0 = (0x0200)  # AVG Samples Bit 0 - See table 3 spec

INA3221_CONFIG_VBUS_CT2 = (0x0100)  # VBUS bit 2 Conversion time - See table 4 spec
INA3221_CONFIG_VBUS_CT1 = (0x0080)  # VBUS bit 1 Conversion time - See table 4 spec
INA3221_CONFIG_VBUS_CT0 = (0x0040)  # VBUS bit 0 Conversion time - See table 4 spec

INA3221_CONFIG_VSH_CT2 = (0x0020)  # Vshunt bit 2 Conversion time - See table 5 spec
INA3221_CONFIG_VSH_CT1 = (0x0010)  # Vshunt bit 1 Conversion time - See table 5 spec
INA3221_CONFIG_VSH_CT0 = (0x0008)  # Vshunt bit 0 Conversion time - See table 5 spec

INA3221_CONFIG_MODE_2 = (0x0004)  # Operating Mode bit 2 - See table 6 spec
INA3221_CONFIG_MODE_1 = (0x0002)  # Operating Mode bit 1 - See table 6 spec
INA3221_CONFIG_MODE_0 = (0x0001)  # Operating Mode bit 0 - See table 6 spec

INA3221_REG_SHUNTVOLTAGE_1 = (0x01)
INA3221_REG_BUSVOLTAGE_1 = (0x02)

SHUNT_RESISTOR_VALUE = (0.1)   # default shunt resistor value of 0.1 Ohm



class INA3221Sensor():

    def __init__(self):
        self._bus = smbus2.SMBus(1)
        self._addr = INA3221_ADDRESS
        config = INA3221_CONFIG_ENABLE_CHAN1 |		\
                    INA3221_CONFIG_ENABLE_CHAN2 |	\
                    INA3221_CONFIG_ENABLE_CHAN3 |	\
                    INA3221_CONFIG_AVG1 |		\
                    INA3221_CONFIG_VBUS_CT2 |		\
                    INA3221_CONFIG_VSH_CT2 |		\
                    INA3221_CONFIG_MODE_2 |		\
                    INA3221_CONFIG_MODE_1 |		\
                    INA3221_CONFIG_MODE_0




        self._write_register_little_endian(INA3221_REG_CONFIG, config)


    def _write(self, register, data):
        self._bus.write_byte_data(self._addr, register, data)


    def _read(self, data):

        returndata = self._bus.read_byte_data(self._addr, data)
        return returndata


    def _read_register_little_endian(self, register): 
	
        result = self._bus.read_word_data(self._addr,register) & 0xFFFF
        lowbyte = (result & 0xFF00)>>8 
        highbyte = (result & 0x00FF) << 8
        switchresult = lowbyte + highbyte 
        return switchresult
   
   
    def _write_register_little_endian(self, register, data): 

        data = data & 0xFFFF
        lowbyte = data>>8
        highbyte = (data & 0x00FF)<<8
        switchdata = lowbyte + highbyte
        self._bus.write_word_data(self._addr, register, switchdata)
       


    def _getBusVoltage_raw(self, channel):

        value = self._read_register_little_endian(INA3221_REG_BUSVOLTAGE_1+(channel -1) *2) 
        if value > 32767:
            value -= 65536
        return value

    def _getShuntVoltage_raw(self, channel):
	
        value = self._read_register_little_endian(INA3221_REG_SHUNTVOLTAGE_1+(channel -1) *2)
        if value > 32767:
            value -= 65536
        return value

    # public functions

    def getBusVoltage_V(self, channel):

        value = self._getBusVoltage_raw(channel)
        return value * 0.001


    def getShuntVoltage_mV(self, channel):

        value = self._getShuntVoltage_raw(channel)
        return value * 0.005

    def getCurrent_mA(self, channel):
    	
        valueDec = self.getShuntVoltage_mV(channel)/ SHUNT_RESISTOR_VALUE               
        return valueDec

    def read(self):
        try:
            voltage = self.getBusVoltage_V(2)
            current = self.getCurrent_mA(1)
            return {"voltage": voltage, "current": current}
        except Exception as e:
            print(f"INA3221 read error: {e}")
            return {"voltage": 0.0, "current": 0.0}
