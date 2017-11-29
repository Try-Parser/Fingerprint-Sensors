import serial
import time
import struct

global ser

comm_struct = lambda: '<BBHIH'
data_struct = lambda x: '<BBH' + str(x) + 's'
checksum_struct = lambda: '<H'

ser = serial.Serial('/dev/ttyAMA0', baudrate=57600, timeout=2)

cmd = 0x22
ID = 1
deviceID = 0x01

def writePacket(cmd, parameter, deviceID = deviceID):
	packet = bytearray(struct.pack(comm_struct(), 0x55, 0xAA, deviceID, ID, cmd))
	checksum = sum(packet)
	packet += bytearray(struct.pack(checksum_struct(), checksum))

	result = len(packet) == ser.write(packet)
	ser.flush()

	return result

result = writePacket(0x12, 1)

while True:
	print (result)
