from GTSensor import GTSensor
import time
import base64
import websocket
import json
import threading

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)
		self.stopScan = False
		_initialization_response = self.sensor.initialize(True, True)
		time.sleep(0.5)

		print(_initialization_response)

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
			print(self.stopScan, "wtf?")
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
		self.sensor.LED(True)
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
					ws.send('{ "command": "save", "template": "'+ base64.b64encode(template[1]["Data"]).decode() +'", "message": "Finger Template is confirmed"}')
				else:
					ws.send('{ "command": "IFPT", "message": "failed to acknowledge the finger template!"}')
					# self.enroll(ws)
		else:
			self.enroll(ws)

		print ("terminitation")
		self.sensor.LED(False)
		# self.sensor.close()
		# exit(1)


	# def security(self, templates):
	# 	self.multiPool.map(self.processor, templates)

	# def scanLoop(self):
	# 	while not self.stopScan:
	# 		self.sensor.LED(True)
	# 		time.sleep(0.5)
	# 		if self.__capture_the_lights__():
	# 			template = self.sensor.genTemplate()
	# 			self.sensor.LED(False)
	# 			time.sleep(0.5)
	# 			print(template)
	# 		else:
	# 			self.sensor.LED(False)
	# 			break;

	# 		if self.stopScan:
	# 			break

	# 	print ("stop scanning")

	def scanLoop(self, rascan):
		while not self.stopScan:
			self.sensor.LED(True)
			time.sleep(0.5)
			if len(rascan.templates) > 0:
				if self.__capture_the_lights__():
					self.sensor.LED(False)
					threads = [threading.Thread(name="TP"+str(i), target=self.processor, args=(rascan.templates, i,)) for i in range(10) ]

					for thread in threads:
						thread.start()
				else:
					self.sensor.LED(False)
					break;
			else:
				rascan.ws.send('{ "command": "error", "message": "No Templates available or the rascan is not initialized properly!"}')
				self.stopScan = True;

			if self.stopScan:
				break
		
		print ("Stop Scanning")

	def processor(self, template, start):
		print(len(template), start, len(template)-1)

		while start <= len(template)-1:
			print(base64.b64decode(template[start]["fptemplate"].encode()))
			confirmation = self.sensor.indentify(base64.b64decode(template[start]["fptemplate"].encode()))
			print(confirmation)
			# if confirmation[1]["ACK"]:
			# print(template[start]["user_id"])
			# print(template[start]["id"])
			start = start + 10
			if start > len(template)-1:
				break;

		print(start, "End")