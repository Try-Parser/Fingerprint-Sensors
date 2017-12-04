from GTSensor import GTSensor
import time

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)

		_initialization_response = self.sensor.initialize(True)
		time.sleep(0.5)

		print(_initialization_response)


		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(57600)
		time.sleep(0.5)

		self.sensor.LED(True)
		time.sleep(0.5)
		self.sensor.LED(False)
		time.sleep(0.5)
		
		self.sensor.LED(True)
		print(baudrateResult)
		time.sleep(0.5)
		self.sensor.LED(False)
		time.sleep(0.2)

		self.sensor.LED(True)
		_ = input("Place your finger and then press <Enter>")

		cfResp = self.sensor.captureFinger(True)
		print (cfResp)

		time.sleep(0.2)
		print ("Generating template")

		rx = self.sensor.genTemplate()
		print (rx)

		rxPacket = self.sensor.close()
		# print(rxPacket)
		self.sensor.LED(False)

app=App()




