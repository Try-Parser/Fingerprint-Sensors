import serial
import time
import struct
import RPi.GPIO as GPIO
from time import sleep
global ser

comm_struct = lambda: '<BBHIH'
data_struct = lambda x: '<BBH' + str(x) + 's'
checksum_struct = lambda: '<H'

Data_Start_Code_2 = 0x5A
Data_Start_Code_2 = 0xA5
CMD_Code_1 = 0x55
CMD_Code_2 = 0xAA

ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=2)

GPIO.setmode(GPIO.BCM)
INPUT_PIN = 17
INPUT_PIN2 = 18

GPIO.setup(INPUT_PIN, GPIO.OUT)
GPIO.setup(INPUT_PIN2, GPIO.OUT)

GPIO.add_event_detect(INPUT_PIN2, GPIO.FALLING, callback=inputLow, bouncetime=200);

def inputLow(channel):
	print(channel);
    print('0');

while True:
	print('3.3');
	sleep(1);  


# time.sleep(1)
# cmd = 0x22
# ID = 1
# deviceID = 0x01

# def writePacket(cmd, param, deviceID = deviceID):
# 	packet = bytearray(struct.pack(comm_struct(), 0x55, 0xAA, deviceID, param, cmd))
# 	checksum = sum(packet)
# 	packet += bytearray(struct.pack(checksum_struct(), checksum))

# 	result = len(packet) == ser.write(packet)
# 	ser.flush()

# 	return result

# def receivedPacket(packetLn = 12):
# 	while not ser.readable():
# 		print("aw")

# 	rxPacket = ser.read(packetLn)
# 	print(rxPacket)

# def onLED(tf):
# 	result = writePacket(0x12, tf*1)

# 	if result:
# 		receivedPacket()


# # ser.timeout = 10

# result = writePacket(0x01, 0x0)
# if result:
# 	receivedPacket()
# time.sleep(0.5)


# result = writePacket(0x04, 57600)
# if result:
# 	ser.baudrate = 57600
# 	receivedPacket()
# time.sleep(0.5)


# onLED(True)

# _ = input("Press Enter to continue...")
# ser.timeout = 10
# result = writePacket(0x60, 0x01)

# if result:
# 	receivedPacket()
# 	ser.timeout = 5

# onLED(False)


# print ("Generating Template..")

# result = writePacket(0x61, 0x00)

# ser.timeout = 10

# if result:
# 	rxPacket = ser.read(1+1+2+498+2)
# 	ser.timeout = 5
# 	print (rxPacket)

