#!/usr/bin/python3
from prometheus_client import start_http_server, Summary
from cryptography.hazmat.primitives.asymmetric import ed25519
from LoRaRF import SX127x
import RPi.GPIO as GPIO
import signal
import sys
import os
import time

import LoRaModules


def cleanup(signal, frame):
    print("GPIO cleanup")
    GPIO.cleanup()  # Clean up GPIO resources
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def verifiyMessage(message):
    pubKey = bytes([185, 185, 210, 10, 252, 37, 248, 37, 157, 194, 141, 137, 58, 217, 3, 31, 6, 147, 230, 156, 152, 252, 192, 225, 180, 231, 227, 180, 105, 225, 249, 127])
    pubKey = ed25519.Ed25519PublicKey.from_public_bytes(pubKey)
    try:
        pubKey.verify(message[-64:], message[:-64])
    except Exception as e:
        return False
    return True


def getUniqueID(message):
    return int.from_bytes(message[1:9], byteorder='big', signed=False)
    

start_http_server(8000)
nodes = {}


try:
    LoRa = SX127x()
    LoRa.begin(bus=0, cs=0, reset=27, irq=22)
    LoRa.setFrequency(868000000)
    
    while True:
        LoRa.request()
        LoRa.wait(0.1)
        message = bytes([])
        while LoRa.available() > 0:
            byte = LoRa.read()
            message += bytes([byte])
        if verifiyMessage(message):
            nodeID = getUniqueID(message)
            if not nodeID in nodes.keys():
                nodes[nodeID] = LoRaModules.getNodeClass(message[0])()
                print(f"New node: {hex(nodeID)}")
            if os.environ.get('DEBUG', False):
                print(message.hex(' '))
            nodes[nodeID].parseMessage(message)
        time.sleep(0.01)
        
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
GPIO.cleanup()
