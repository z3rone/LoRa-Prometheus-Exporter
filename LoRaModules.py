from cryptography.hazmat.primitives.asymmetric import ed25519
from ByteRead import readBytes
import os
import mysql.connector
from datetime import datetime
import time

def getNodeClass(type_id):
    if type_id == 0x01:
        return Module_ENS160_AHT21
    if type_id == 0x02:
        return Module_VEML7700
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

    _mysql_conn = None

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
        db_config = {
            'host':     os.getenv('MYSQL_HOST',     'localhost'),
            'user':     os.getenv('MYSQL_USER',     'grafana'),
            'password': os.getenv('MYSQL_PASSWORD', 'grafana'),
            'database': os.getenv('MYSQL_DATABASE', 'grafana')
        }
        self._mysql_conn = mysql.connector.connect(**db_config)


    def _store_datapoint(self, metric_name, value, timestamp, labels):
        cursor = self._mysql_conn.cursor()
        insert_query = 'INSERT INTO metrics (timestamp, metric, value, tags) VALUES (FROM_UNIXTIME(%s), %s, %s, %s)'
        labels_string = ",".join([ f"{key}={value}" for key, value in labels.items() ])
        values = (timestamp, metric_name, value, labels_string)
        cursor.execute(insert_query, values)
        self._mysql_conn.commit()
        cursor.close()

    def parseMessage(self, message):
        _datapoint_time = int(time.time())

        pubKey = ed25519.Ed25519PublicKey.from_public_bytes(self.pubKey)
        pubKey.verify(message[-64:], message[:-64])
        
        #if message[:self._DEVICE_TYPE_LEN] != self.typeID:
        #    raise ValueError("Device type does not match")
        message = message[self._DEVICE_TYPE_LEN:]
        
        _uniqueID = readBytes(message[:self._UNIQUE_ID_LEN])
        message  = message[self._UNIQUE_ID_LEN:]
        
        _time    = readBytes(message[:self._TIME_LEN])
        message = message[self._TIME_LEN:]
        
        #battery = message[:_BATTERY_LEN]
        #message = message[_BATTERY_LEN:]
        
        _temperature = readBytes(message[:self._TEMPERATURE_LEN])
        _temperature /= self._TEMPERATURE_FACTOR
        _temperature -= self._TEMPERATURE_OFFSET
        message     = message[self._TEMPERATURE_LEN:]

        _humidity = readBytes(message[:self._HUMIDITY_LEN])
        _humidity /= self._HUMIDITY_FACTOR
        message  = message[self._HUMIDITY_LEN:]

        _co2     = readBytes(message[:self._CO2_LEN])
        message = message[self._CO2_LEN:]

        _tvoc    = readBytes(message[:self._TVOC_LEN])
        message = message[self._TVOC_LEN:]

        _ethoh   = readBytes(message[:self._ETHOH_LEN])
        message = message[self._ETHOH_LEN:]

        _aqi     = readBytes(message[:self._AQI_LEN])
        message = message[self._AQI_LEN:]

        labels = {'unique_id': hex(_uniqueID), 'device_type': hex(int.from_bytes(self.typeID, byteorder='little'))}
        self._store_datapoint('irs_lora_unique_id',   _uniqueID,    _datapoint_time, labels)
        self._store_datapoint('irs_lora_time',        _time,        _datapoint_time, labels)
        self._store_datapoint('irs_lora_temperature', _temperature, _datapoint_time, labels)
        self._store_datapoint('irs_lora_humidity',    _humidity,    _datapoint_time, labels)
        self._store_datapoint('irs_lora_co2',         _co2,         _datapoint_time, labels)
        self._store_datapoint('irs_lora_tvoc',        _tvoc,        _datapoint_time, labels)
        self._store_datapoint('irs_lora_ethoh',       _ethoh,       _datapoint_time, labels)
        self._store_datapoint('irs_lora_aqi',         _aqi,         _datapoint_time, labels)

class Module_VEML7700:
    _DEVICE_TYPE_LEN = 1
    _UNIQUE_ID_LEN   = 8
    _BATTERY_LEN     = 1
    _LUX_LEN         = 4
    _SIGNATURE_LEN   = 64

    _LUX_FACTOR = 100.0
    _BATTERY_FACTOR = 100.0
    
    _mysql_conn = None

    typeID = bytes([0x02])
    uniqueID = None
    battery = None
    lux = None

    pubKey = bytes([185, 185, 210, 10, 252, 37, 248, 37, 157, 194, 141, 137, 58, 217, 3, 31, 6, 147, 230, 156, 152, 252, 192, 225, 180, 231, 227, 180, 105, 225, 249, 127])


    def __init__(self):
        labels = ['unique_id', 'device_type']
        db_config = {
            'host':     os.getenv('MYSQL_HOST',     'localhost'),
            'user':     os.getenv('MYSQL_USER',     'grafana'),
            'password': os.getenv('MYSQL_PASSWORD', 'grafana'),
            'database': os.getenv('MYSQL_DATABASE', 'grafana')
        }
        self._mysql_conn = mysql.connector.connect(**db_config)


    def _store_datapoint(self, metric_name, value, timestamp, labels):
        cursor = self._mysql_conn.cursor()
        insert_query = 'INSERT INTO metrics (timestamp, metric, value, tags) VALUES (%s, %s, %s, %s)'
        labels_string = ",".join([ f"{key}={value}" for key, value in labels.items() ])
        values = (timestamp, metric_name, value, labels_string)
        cursor.execute(insert_query, values)
        self._mysql_conn.commit()
        cursor.close()


    def parseMessage(self, message):
        _datapoint_time = int(time.time())

        pubKey = ed25519.Ed25519PublicKey.from_public_bytes(self.pubKey)
        pubKey.verify(message[-64:], message[:-64])
        
        #if message[:self._DEVICE_TYPE_LEN] != self.typeID:
        #    raise ValueError("Device type does not match")
        message = message[self._DEVICE_TYPE_LEN:]
        
        _uniqueID = readBytes(message[:self._UNIQUE_ID_LEN])
        message  = message[self._UNIQUE_ID_LEN:]
        
        _battery = int.from_bytes(message[:self._BATTERY_LEN], byteorder='big')
        _battery /= self._BATTERY_FACTOR
        message = message[self._BATTERY_LEN:]

        _lux = int.from_bytes(message[:self._LUX_LEN], byteorder='big')
        _lux /= self._LUX_FACTOR
        message = message[self._LUX_LEN:]

        labels = {'unique_id': hex(_uniqueID), 'device_type': hex(int.from_bytes(self.typeID, byteorder='little'))}
        self._store_datapoint('irs_lora_unique_id',   _uniqueID,    _datapoint_time, labels)
        self._store_datapoint('irs_lora_lux',         _lux,         _datapoint_time, labels)
