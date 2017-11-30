import serial
import time
import struct

global ser

comm_struct = lambda: '<BBHIH'
data_struct = lambda x: '<BBH' + str(x) + 's'
checksum_struct = lambda: '<H'

Data_Start_Code_2 = 0x5A
Data_Start_Code_2 = 0xA5
CMD_Code_1 = 0x55
CMD_Code_2 = 0xAA

ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=2)

cmd = 0x22
ID = 1
deviceID = 0x01

def writePacket(cmd, param, deviceID = deviceID):
	packet = bytearray(struct.pack(comm_struct(), 0x55, 0xAA, deviceID, param, cmd))
	checksum = sum(packet)
	packet += bytearray(struct.pack(checksum_struct(), checksum))

	result = len(packet) == ser.write(packet)
	ser.flush()

	return result

def receivedPacket(packetLn = 12):
	rxPacket = ser.read(packetLn)
	print(rxPacket)


result = writePacket(0xF4)

if result:
	receivedPacket()
