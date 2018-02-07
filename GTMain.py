from GTSensor import GTSensor
import time
from multiprocessing import Pool
import base64
import websocket
import json

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)
		self.stopScan = False
		_initialization_response = self.sensor.initialize(True, True)
		time.sleep(0.5)

		print(_initialization_response)

		self.multiPool = Pool(5)
		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(57600)
		print ("Setting is done testing for LED lights")
		self.sensor.LED(True)
		time.sleep(0.5)
		self.sensor.LED(False)

		self.template = ""

	def __capture_the_lights__(self): 
		while True:
			procced = False

			if self.stopScan:
				return False

			if self.sensor.senseFinger()[0]['Parameter'] == 0:
				procced = True
			
			if procced:
				print ("Capturing Fingerprint")
				time.sleep(0.1)
				if self.sensor.captureFinger(True)['ACK']:
					return True

	def enroll(self, ws):
		print("Enrollment Starting")
		# self.sensor.LED(True)
		time.sleep(0.1)
		if self.__capture_the_lights__():
			template = self.sensor.genTemplate()
			print(template[0])
			print(template[1])

			time.sleep(0.2)
			if self.__capture_the_lights__():
				confirmation = self.sensor.indentify(template[1]['Data'])
				print (confirmation)
				if confirmation[1]["ACK"] == True:
					ws.send('{ "command": "save", "template": '+ base64.standard_b64encode(template[1]["Data"]) +', "message": "Finger Template is confirmed"}')
				else:
					ws.send('{ "command": "error", "message": "failed to acknowledge the finger template!"}')
					self.enroll(rascan)

				#logical process
		else:
			self.enroll()

		print ("terminitation")
		self.sensor.LED(False)
		# self.sensor.close()
		# exit(1)

	# def processor(self, template):
	# 	confirmation = self.sensor.indentify(tempate["fptemplate"])

	# def security(self, templates):
	# 	self.multiPool.map(self.processor, templates)

	def scanLoop(self):
		while not self.stopScan:
			self.sensor.LED(True)
			time.sleep(0.5)
			if self.__capture_the_lights__():
				template = self.sensor.genTemplate()
				self.sensor.LED(False)
				time.sleep(0.5)
				print(template)
			else:
				self.sensor.LED(False)
				break;

			if self.stopScan:
				break

		print ("stop scanning")