import serial
import time
import struct

global ser

comm_struct = lambda: '<BBHIH'
data_struct = lambda x: '<BBH' + str(x) + 's'
checksum_struct = lambda: '<H'

ser = serial.Serial('/dev/ttyAMA0', baudrate=57600, timeout=5.0)

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

def decode_command_packet(packet):
    response = {
        'Header': None,
        'DeviceID': None,
        'ACK': None,
        'Parameter': None,
        'Checksum': None        
    }
    _debug = packet
    if packet == '': # Nothing to decode
        response['ACK'] = False
        return response

    # Check if it is a data packet:
    if packet[0] == 0x5A and packet[1] == 0xA5:
        return decode(packet)

    # Strip the checksum and get the values out
    checksum = sum(struct.unpack(checksum_struct(), packet[-2:])) # Last two bytes are checksum
    packet = packet[:-2]
    response['Checksum'] = sum(packet) == checksum # True if checksum is correct

    try:
        packet = struct.unpack(comm_struct(), packet)
    except Exception as e:
        raise Exception(str(e) + ' ' + str(packet[0]))

    response['Header'] = hex(packet[0])[2:] + hex(packet[1])[2:]
    response['DeviceID'] = hex(packet[2])[2:]
    response['ACK'] = packet[4] != 0x31 # Not NACK, might be command
    # response['Parameter'] = packet[3] if response['ACK'] else errors[packet[3]]
    response['Parameter'] = errors[packet[3]] if (not response['ACK'] and packet[3] in errors) else packet[3]

    return response

def decode(packet):
    response = {
        'Header': None,
        'DeviceID': None,
        'Data': None,
        'Checksum': None        
    }
    if packet == '':
        response['ACK'] = False
        return response
    # Check if it is a command packet:
    if packet[0] == 0x55 and packet[1] == 0xAA:
        return decode_command_packet(packet)
    
    # Strip the checksum and get the values out
    checksum = sum(struct.unpack(checksum_struct(), packet[-2:])) # Last two bytes are checksum
    packet = packet[:-2]

    # Data sum might be larger than the checksum field:
    chk = sum(packet)
    chk &= 0xffff
    response['Checksum'] = chk == checksum # True if checksum is correct
    
    data_len = len(packet) - 4 # Exclude the header (2) and device ID (2)

    packet = struct.unpack(data_struct(data_len), packet)
    response['Header'] = hex(packet[0])[2:] + hex(packet[1])[2:]
    response['DeviceID'] = hex(packet[2])[2:]
    response['Data'] = packet[3]
    # print packet
    return response

def receivedPacket(response_len = 12):
	serialResp = ser.read(response_len)
	return decode_command_packet(bytearray(serialResp))


# result = writePacket(cmd, ID, deviceID)

if writePacket(0x51, 0x00):
	result = receivedPacket()

	print (result)
