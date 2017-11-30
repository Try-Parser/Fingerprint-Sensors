from GTSensor import GTSensor
import time

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=5.0)

		_initialization_response = self.sensor.initialize(True)

		self.sensor.LED(True)
		println(_initialization_response)
		self.sensor.LED(False)

		time.sleep(0.5)
		self.sensor.LED(True)
		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(56700)
		print(baudrateResult)
		self.sensor.LED(False)

app=App()




