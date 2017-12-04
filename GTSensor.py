import serial
import struct
from GTEnum import GT521F5
import logging

class GTSensor:
	def __init__(
			self, 
			port, 
			baudrate = 9600, 
			timeout = 2,
			*args, **kwargs):

		try: 
			self.address = GT521F5.OPEN.value
			self.serial = serial.Serial(
				port = port, 
				baudrate = baudrate, 
				timeout = timeout,
				*args, **kwargs)

			self.usb_timeout = timeout

		except Exception as e:
			logging.error ("Unidentified execption: "+ str(e))
			logging.warning ("Auto-shutdown application.")
			exit(1)

	def writePacket(self, cmd, param):
		packet = bytearray(struct.pack(GT521F5.COMM_STRUCT(), 0x55, 0xAA, self.address, param, cmd))
		checksum = sum(packet)
		packet += bytearray(struct.pack(GT521F5.CHECK_SUM_STRUCT(), checksum))

		result = len(packet) == self.serial.write(packet)
		self.serial.flush()

		return result

	def decode_command(self, rxPacket):
		response = {
			'Header'	: None,
			'DeviceID'	: None,
			'ACK'		: None,
			'Parameter' : None,
			'Checksum'	: None
		}

		if rxPacket == b'':
			response['ACK'] = False
			return response

		if rxPacket[0] == GT521F5.CMD_DATA_1.value and rxPacket[1] == GT521F5.CMD_DATA_2.value:
			return self.decode_data(rxPacket)

		checksum = sum(struct.unpack(GT521F5.CHECK_SUM_STRUCT(), rxPacket[-2:]))
		rxPacket = rxPacket[:-2]
		response['Checksum'] = sum(rxPacket) == checksum

		try:
			rxPacket = struct.unpack(GT521F5.COMM_STRUCT(), rxPacket)
		except Exception as e:
			raise Exception(str(e) + ' ' + str(rxPacket[0]))

		response['Header'] = hex(rxPacket[0])[2:] + hex(rxPacket[1])[2:]
		response['DeviceID'] = hex(rxPacket[2])[2:]
		response['ACK'] = rxPacket[4] != 0x31
		response['Parameter'] = errors[rxPacket[3]] if (not response['ACK'] and rxPacket[3] in errors) else rxPacket[3]

		return response

	def decode_data(self, rxPacket):
		response = {
			'Header'	: None,
			'DeviceID'	: None,
			'Data'		: None,
			'Checksum'	: None
		}

		if rxPacket == b'':
			response['ACK'] = False
			return response

		if rxPacket[0] == GT521F5.CMD_STRT_1.value and rxPacket[1] == GT521F5.CMD_STRT_2.value:
			return self.decode_command(rxPacket)

		checksum = sum(struct.unpack(GT521F5.CHECK_SUM_STRUCT(), rxPacket[-2:]))
		rxPacket = rxPacket[:-2]

		chk = sum(rxPacket)
		chk &= 0xffff

		response['Checksum'] = chk == checksum

		data_len = len(rxPacket) - 4

		rxPacket = struct.unpack(GT521F5.DATA_STRUCT(data_len), rxPacket)
		response['Header'] = hex(rxPacket[0])[2:] + hex(rxPacket[1])[2:]
		response['DeviceID'] = hex(rxPacket[2])[2:]
		response['Data'] = rxPacket[3]

		return response

	def receivedPacket(self, packetLength = 12):
		rxPacket = self.serial.read(packetLength)
		return self.decode_command(rxPacket)

	def encode_data(self, data, length, address):
		txPacket = bytearray([
			GT521F5.CMD_DATA_1.value,
			GT521F5.CMD_DATA_2.value,
			address,
			data
		])

		checksum = sum(txPacket)
		txPacket += bytearray(struct.pack(GT521F5.CHECK_SUM_STRUCT(), checksum))
		return txPacket

	def receivedData(self, packetLength):
		rxPacket = self.serial.read(1+1+2+packetLength+2)

		return self.decode_data(bytearray(rxPacket))

	def writeData(self, data, packetLength):
		txPacket = self.encode_data(data, packetLength, GT521F5.OPEN.value)
		result = len(packet) == self.serial.write(txPacket)
		self.serial.flush()
		return result

	# commands
	def initialize(self, extra_info = False, check_baudrate = False):
		if check_baudrate:
			self.serial.timeout = 0.5
			for baudrate in (self.serial.baudrate,) + self.serial.BAUDRATES:
				if 9600 <= baudrate <= 115200:
					self.serial.baudrate = baudrate
					if not self.writePacket(self.address, extra_info*1):
						raise RuntimeError("Couldn't send 'Open' packet!")

					response = self.receivedPacket()
					if response['ACK']:
						response['Parameter'] = baudrate
						break

			if self.serial.baudrate > 115200:
				raise RuntimeError("Couldn't find appropriate baudrate!")
		else:
			self.writePacket(self.address, extra_info*1)
			response = self.receivedPacket()
		data = None
		if extra_info:
			data = self.receivedData(16+4+4)
		self.serial.timeout  = self.usb_timeout
		return [response, data]


	def close(self):
		if self.writePacket(GT521F5.CLOSE.value, GT521F5.DEFAULT.value):
			return self.receivedPacket()
		else:
			raise RuntimeError("Couldn't send packet.")

	def LED(self, on):
		if self.writePacket(GT521F5.CMOS_LED.value, on*1):
			return self.receivedPacket()
		else:
			raise RuntimeError("Couldn't send packet.")

	def setBaudrate(self, baudrate):
		if self.writePacket(GT521F5.SET_BAUDRATE.value, baudrate):
			response = self.receivedPacket()
			self.serial.baudrate = baudrate
			return response
		else:
			raise RuntimeError("Couldn't send packet.")

	def captureFinger(self, hd = False):
		if hd:
			self.serial.timeout = 10

		if self.writePacket(GT521F5.CAPTURE_IMAGE.value, hd*1):
			self.serial.timeout = self.usb_timeout
			return self.receivedPacket()
		else:
			raise RuntimeError("Couldn't send packet.")

	def genTemplate(self):
		if self.writePacket(GT521F5.MAKE_TEMPLATE.value, GT521F5.DEFAULT.value):
			response = self.receivedPacket()
		else:
			raise RuntimeError("Couldn't send packet.")

		self.serial.timeout = 10
		data = self.receivedData(498)
		self.serial.timeout = self.usb_timeout

		return [response, data]


	def indentify(self, template):
		if self.writePacket(GT521F5.IDENTIFY_TEMPLATE.value, GT521F5.IDENTIFY_TEMPLATE_PARAM.value):
			response = self.receivedPacket()
		else:
			raise RuntimeError("Couldn't send packet.")

		if self.writeData(b"\x01\x01" + template, 500):
			data = self.receivedPacket()
		else:
			raise RuntimeError("Couldn't send packet (data)")

		return [response, data]

	def senseFinger(self):
		if self.writePacket(GT521F5.DETECT_FINGER.value, GT521F5.DEFAULT.value):
			return [self.receivedPacket(), None]
		else:
			raise RuntimeError("Couldn't send packet.")
