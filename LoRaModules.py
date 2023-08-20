from cryptography.hazmat.primitives.asymmetric import ed25519
from prometheus_client import Gauge, REGISTRY
from ByteRead import readBytes

def getNodeClass(type_byte):
    if type_byte == bytes([0x01]):
        return Module_ENS160_AHT21
    return None

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


    def __init__(self):
        labels = ['unique_id', 'device_type']
        self.uniqueID    = Gauge('irs_lora_unique_id', 'Chip ID of the node', labels)
        self.time        = Gauge('irs_lora_time', 'Timestamp of the node clock', labels)
        self.battery     = Gauge('irs_lora_battery', 'Battery voltage of the node (mV)', labels)
        self.temperature = Gauge('irs_lora_temperature', 'Measured temperature (°C)', labels)
        self.humidity    = Gauge('irs_lora_humidity', 'Measured humidity (%RH)', labels)
        self.co2         = Gauge('irs_lora_co2', 'Measured CO2 (ppm)', labels)
        self.tvoc        = Gauge('irs_lora_tvoc', 'Measured TVOC (ppb)', labels)
        self.ethoh       = Gauge('irs_lora_ethoh (ppb)')
        self.aqi         = Gauge('irs_lora_aqi (-)')
        REGISTRY.register(self.uniqueID)
        REGISTRY.register(self.time)
        REGISTRY.register(self.battery)
        REGISTRY.register(self.temperature)
        REGISTRY.register(self.humidity)
        REGISTRY.register(self.co2)
        REGISTRY.register(self.tvoc)
        REGISTRY.register(self.ethoh)
        REGISTRY.register(self.aqi)


    def parseMessage(self, message):
        pubKey = ed25519.Ed25519PublicKey.from_public_bytes(self.pubKey)
        pubKey.verify(message[-64:], message[:-64])
        
        if message[:self._DEVICE_TYPE_LEN] != self.typeID:
            raise ValueError("Device type does not match")
        message = message[self._DEVICE_TYPE_LEN:]
        
        uniqueID = readBytes(message[:self._UNIQUE_ID_LEN])
        message  = message[self._UNIQUE_ID_LEN:]
        
        self.time    = readBytes(message[:self._TIME_LEN])
        message = message[self._TIME_LEN:]
        
        #battery = message[:_BATTERY_LEN]
        #message = message[_BATTERY_LEN:]
        
        temperature = readBytes(message[:self._TEMPERATURE_LEN])
        temperature /= self._TEMPERATURE_FACTOR
        temperature -= self._TEMPERATURE_OFFSET
        message     = message[self._TEMPERATURE_LEN:]

        humidity = readBytes(message[:self._HUMIDITY_LEN])
        humidity /= self._HUMIDITY_FACTOR
        message  = message[self._HUMIDITY_LEN:]

        co2     = readBytes(message[:self._CO2_LEN])
        message = message[self._CO2_LEN:]

        tvoc    = readBytes(message[:self._TVOC_LEN])
        message = message[self._TVOC_LEN:]

        ethoh   = readBytes(message[:self._ETHOH_LEN])
        message = message[self._ETHOH_LEN:]

        aqi     = readBytes(message[:self._AQI_LEN])
        message = message[self._AQI_LEN:]

        labels = {'unique_id': uniqueID, 'device_type': int(seld.typeID)}
        self.uniqueID.labels(**labels).set(uniqueID)
        self.time.labels(**labels).set(time)
        self.temperature.labels(**labels).set(temperature)
        self.humidity.labels(**labels).set(humidity)
        self.co2.labels(**labels).set(co2)
        self.tvoc.labels(**labels).set(tvoc)
        self.ethoh.labels(**labels).set(ethoh)
        self.aqi.labels(**labels).set(aqi)
