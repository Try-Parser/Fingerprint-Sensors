import serial
import time
import struct

global ser

ser = serial.serial('/dev/ttyAMA0', baudrate=57600, timeout=5.0)

cmd = 0x22
ID = 1
deviceID = 0x01

packet = bytearray(struct.pack(comm_struct(), 0x55, 0xAA, deviceID, ID, cmd))

checksum = sum(packet)
packet += bytearray(struct.pack(checksum_struct(), checksum))

result = len(packet) == serial.write(packet)
serial.flush()

print(result)

