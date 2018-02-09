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
					# self.multiPool.map(self.processor, rascan.templates)
					# for i in rascan.templates:

					threads = [threading.Thread(name="TP"+str(i), target=self.processor, args=(rascan.templates, i,)) for i in range(10) ]

					for thread in threads:
						thread.start()

					for thread in threads:
						thread.join()
					# TP0 = threading.Thread(name="TP0", target=self.processor, args=(rascan.templates, 0,))
					# TP1 = threading.Thread(name="TP1", target=self.processor, args=(rascan.templates, 1,))
					# TP2 = threading.Thread(name="TP2", target=self.processor, args=(rascan.templates, 2,))
					# TP3 = threading.Thread(name="TP3", target=self.processor, args=(rascan.templates, 3,))
					# TP4 = threading.Thread(name="TP4", target=self.processor, args=(rascan.templates, 4,))
					# TP5 = threading.Thread(name="TP5", target=self.processor, args=(rascan.templates, 5,))
					# TP6 = threading.Thread(name="TP6", target=self.processor, args=(rascan.templates, 6,))
					# TP7 = threading.Thread(name="TP7", target=self.processor, args=(rascan.templates, 7,))
					# TP8 = threading.Thread(name="TP8", target=self.processor, args=(rascan.templates, 8,))
					# TP9 = threading.Thread(name="TP9", target=self.processor, args=(rascan.templates, 9,))

					# TP0.setDaemon(True)
					# TP1.setDaemon(True)
					# TP2.setDaemon(True)
					# TP3.setDaemon(True)
					# TP4.setDaemon(True)
					# TP5.setDaemon(True)
					# TP6.setDaemon(True)
					# TP7.setDaemon(True)
					# TP8.setDaemon(True)
					# TP9.setDaemon(True)	

					# TP0.start()
					# TP1.start()
					# TP2.start()
					# TP3.start()
					# TP4.start()
					# TP5.start()
					# TP6.start()
					# TP7.start()
					# TP8.start()
					# TP9.start()	

					# TP0.join()
					# TP1.join()
					# TP2.join()
					# TP3.join()
					# TP4.join()
					# TP5.join()
					# TP6.join()
					# TP7.join()
					# TP8.join()
					# TP9.join()
				else:
					self.sensor.LED(False)
					break;
			else:
				rascan.ws.send('{ "command": "error", "message": "No Templates available or the rascan is not initialized properly!"}')
				self.stopScan = True;

			if self.stopScan:
				break
		
		self.stopScan = False;
		self.sensor.LED(False)
		print ("Stop Scanning")

	def processor(self, template, start):
		print(len(template), start, len(template)-1)
		while start <= len(template)-1:
			print(template[start]["fptemplate"])
			confirmation = self.sensor.indentify(base64.b64decode(template[start]["fptemplate"].encode()))
			print(confirmation)
			if confirmation[1]["ACK"]:
				print(template[start]["user_id"])
				print(template[start]["id"])
			start = start + 10
		print(start, "End")