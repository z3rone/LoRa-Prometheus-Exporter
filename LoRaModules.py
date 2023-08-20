from cryptography.hazmat.primitives.asymmetric import ed25519
from ByteRead import readBytes

class Module_ENS160_AHT21:
    _DEVICE_TYPE_LEN = 1
    _UNIQUE_ID_LEN   = 8
    _TIME_LEN        = 8
    _TEMPERATURE_LEN = 2
    _HUMIDITY_LEN    = 2
    _CO2_LEN         = 2
    _ETHOH_LEN       = 2
    _TVOC_LEN        = 2
    _AQI_LEN         = 1
    _SIGNATURE_LEN   = 64

    _TEMPERATURE_FACTOR = 100
    _TEMPERATURE_OFFSET = 300

    _HUMIDITY_FACTOR = 100

    typeID = bytes([0x01])
    uniqueID = None
    time = None
    battery = None # TODO
    temperature = None
    humidity = None
    co2 = None
    tvoc = None
    ethoh = None
    aqi = None

    pubKey = bytes([185, 185, 210, 10, 252, 37, 248, 37, 157, 194, 141, 137, 58, 217, 3, 31, 6, 147, 230, 156, 152, 252, 192, 225, 180, 231, 227, 180, 105, 225, 249, 127])
    def parseMessage(self, message):
        pubKey = ed25519.Ed25519PublicKey.from_public_bytes(self.pubKey)
        pubKey.verify(message[-64:], message[:-64])
        
        if message[:self._DEVICE_TYPE_LEN] != self.typeID:
            raise ValueError("Device type does not match")
        message = message[self._DEVICE_TYPE_LEN:]
        
        self.uniqueID = readBytes(message[:self._UNIQUE_ID_LEN])
        message  = message[self._UNIQUE_ID_LEN:]
        
        self.time    = readBytes(message[:self._TIME_LEN])
        message = message[self._TIME_LEN:]
        
        #battery = message[:_BATTERY_LEN]
        #message = message[_BATTERY_LEN:]
        
        self.temperature = readBytes(message[:self._TEMPERATURE_LEN])
        self.temperature /= self._TEMPERATURE_FACTOR
        self.temperature -= self._TEMPERATURE_OFFSET
        message     = message[self._TEMPERATURE_LEN:]

        self.humidity = readBytes(message[:self._HUMIDITY_LEN])
        self.humidity /= self._HUMIDITY_FACTOR
        message  = message[self._HUMIDITY_LEN:]

        self.co2     = readBytes(message[:self._CO2_LEN])
        message = message[self._CO2_LEN:]

        self.tvoc    = readBytes(message[:self._TVOC_LEN])
        message = message[self._TVOC_LEN:]

        self.ethoh   = readBytes(message[:self._ETHOH_LEN])
        message = message[self._ETHOH_LEN:]

        self.aqi     = readBytes(message[:self._AQI_LEN])
        message = message[self._AQI_LEN:]
