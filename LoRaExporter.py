#python3
from LoRaRF import SX127x
import RPi.GPIO as GPIO
import signal
import sys
import time

def cleanup(signal, frame):
    print("GPIO cleanup")
    GPIO.cleanup()  # Clean up GPIO resources
    sys.exit(0)
signal.signal(signal.SIGINT, cleanup)

try:
    LoRa = SX127x()
    LoRa.begin(bus=0, cs=0, reset=27, irq=22)
    LoRa.setFrequency(868000000)
    
    while True:
        LoRa.request()
        LoRa.wait()
        message = bytes([])
        while LoRa.available() > 0:
            byte = LoRa.read()
            message += bytes([byte])
            print(hex(byte), end=" ")
        
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
GPIO.cleanup()
