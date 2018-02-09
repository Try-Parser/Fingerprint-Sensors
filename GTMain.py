from GTSensor import GTSensor
import time
from multiprocessing import Pool
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

		self.multiPool = Pool(10)
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
			print(self.stopScan)
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
					self.multiPool.map(self.processor, rascan.templates)
					# for i in rascan.templates:
					# p0 = threading.Thread(target=self.processor, args=(rascan.templates, 0,))
					# p1 = threading.Thread(target=self.processor, args=(rascan.templates, 1,))
					# p2 = threading.Thread(target=self.processor, args=(rascan.templates, 2,))
					# p3 = threading.Thread(target=self.processor, args=(rascan.templates, 3,))
					# p4 = threading.Thread(target=self.processor, args=(rascan.templates, 4,))
					# p5 = threading.Thread(target=self.processor, args=(rascan.templates, 5,))
					# p6 = threading.Thread(target=self.processor, args=(rascan.templates, 6,))
					# p7 = threading.Thread(target=self.processor, args=(rascan.templates, 7,))
					# p8 = threading.Thread(target=self.processor, args=(rascan.templates, 8,))
					# p9 = threading.Thread(target=self.processor, args=(rascan.templates, 9,))
					# p0.start()
					# p1.start()
					# p2.start()
					# p3.start()
					# p4.start()
					# p5.start()
					# p6.start()
					# p7.start()
					# p8.start()
					# p9.start()					
					# p0.join()
					# p1.join()
					# p2.join()
					# p3.join()
					# p4.join()
					# p5.join()
					# p6.join()
					# p7.join()
					# p8.join()
					# p9.join()
				else:
					self.sensor.LED(False)
					break;
			else:
				rascan.ws.send('{ "command": "error", "message": "No Templates available or the rascan is not initialized properly!"}')
				self.stopScan = True;

			if self.stopScan:
				break
		
		self.stopScan = False;
		print ("stop scanning")

	def processor(self, template):
		print(len(template), start)
		# while start <= len(template)-1:
		confirmation = self.sensor.indentify(base64.b64decode(template["fptemplate"].encode()))
		print(confirmation)
		if confirmation[1]["ACK"]:
			print(template["user_id"])
			print(template["id"])
		# start = start + 10

	def __getstate__(self):
		self_dict = self.__dict__.copy()
		del self_dict['multiPool']
		return self_dict

	def __setstate__(self, state):
		self.__dict__.update(state)