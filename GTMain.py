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

	def enroll(self, tempId, ws):
		confirmation = self.sensor.startEnrollment(tempId)
		if confirmation["ACK"]:
			self.sensor.LED(True)
			if self.__capture_the_lights__():
				efr = self.sensor.enrollmentFirst()
				self.sensor.LED(False)
				time.sleep(2)
				if efr["ACK"]:
					self.sensor.LED(True)
					if self.__capture_the_lights__():
						esr = self.sensor.enrollmentSecond()
						self.sensor.LED(False)
						time.sleep(2)
						if esr["ACK"]:
							self.sensor.LED(True)
							if self.__capture_the_lights__():
								etr = self.sensor.enrollmentThird()
								self.sensor.LED(False)
								if etr["ACK"]:
									print("Successfully enrolled.")
									template = self.generateTemplate(tempId)
									if template[0]["ACK"]:
										ws.send('{ "command": "save", "template": "'+ base64.b64encode(template[0][1]["Data"]).decode() +'", "id":"'+tempId+'", "message": "Finger Template is confirmed"}')
									else:
										ws.send(template[1])
								else:
									if efr["Parameter"] == "NACK_ENROLL_FAILED":
										print("Failed to enroll please try again")
									elif efr["Parameter"] == "NACK_BAD_FINGER":
										print("Bad fingprint captured.")
									else:
										print(str(tempId) +" is Already used and duplication occur.!")
						else:
							if efr["Parameter"] == "NACK_ENROLL_FAILED":
								print("Failed to enroll please try again")
							else:
								print("Bad fingprint captured.")
				else:
					if efr["Parameter"] == "NACK_ENROLL_FAILED":
						print("Failed to enroll please try again")
					else:
						print("Bad fingprint captured.")
		else:
			if confirmation["Parameter"] == "NACK_DB_IS_FULL":
				print("Database is full.")
			elif confirmation["Parameter"] == "NACK_INVALID_POS":
				print(str(tempId) +" must be 0 <> 999.")
			else:
				print(str(tempId) +" is Already used.")
		
		self.sensor.LED(False)
		print("Enroll terminitation.")

	def scan(self):
		while not self.stopScan:
			self.sensor.LED(True)
			if self.__capture_the_lights__():
				indentify = self.sensor.security()
				print(indentify)
				self.sensor.LED(True)
			else:
				self.sensor.LED(False)
				break;

	def delete(self, tempId):
		de = self.sensor.rmById(tempId)
		if de["ACK"]:
			print(str(tempId) + " is Successfully deleted.")
		elif not de["ACK"] and de["Parameter"] == "NACK_IS_NOT_USED":
			print(str(tempId) + " is available.")

	def deleteAll(self):
		de = self.sensor.rmAll()
		if de["ACK"]:
			print("Successfull Deletion.")
		elif not de["ACK"] and de["Parameter"] == "NACK_DB_IS_EMPTY":
			print("Already emtpy.")

	def generateTemplate(self, tempId):
		template = self.sensor.generateTemplateById(tempId)
		if template[0]["ACK"]:
			return [template, None];
		else:
			if template[0]["Parameter"] == "NACK_IS_NOT_USED":
				print(str(tempId) +" is not used.")
				return [template, '{"command": "error", "message": '+str(tempId) +'" is not used."}']
			else:
				print(str(tempId) +" must be 0 <> 999.")
				return [template, '{"command": "error", "message": '+str(tempId) +'"  must be 0 <> 999."}']

	def setTemplate(self, template, tempID, ws):
		stresponse = self.sensor.setTemplate(base64.b64decode(template.encode()), tempID)
		if not stresponse[0]["ACK"] and not stresponse[1]["ACK"]:
			ws.send('{ "command": "error",  "message": "'+stresponse[0]["Parameter"]+', "id":"'+str(tempID)+'",}')

	# def enroll(self, ws):
	# 	self.sensor.LED(True)
	# 	time.sleep(0.1)
	# 	if self.__capture_the_lights__():
	# 		template = self.sensor.genTemplate()
	# 		print(template[0])
	# 		print(template[1])

	# 		time.sleep(0.2)
	# 		if self.__capture_the_lights__():
	# 			confirmation = self.sensor.indentify(template[1]['Data'])
	# 			print (confirmation)
	# 			if confirmation[1]["ACK"] == True:
	# 				ws.send('{ "command": "save", "template": "'+ base64.b64encode(template[1]["Data"]).decode() +'", "message": "Finger Template is confirmed"}')
	# 			else:
	# 				ws.send('{ "command": "IFPT", "message": "failed to acknowledge the finger template!"}')
	# 				# self.enroll(ws)
	# 	else:
	# 		self.enroll(ws)

	# 	print ("terminitation")
	# 	time.sleep(3)
	# 	self.sensor.LED(False)
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

	# def scanLoop(self, rascan):
	# 	while not self.stopScan:
	# 		self.sensor.LED(True)
	# 		time.sleep(0.5)
	# 		if len(rascan.templates) > 0:
	# 			if self.__capture_the_lights__():
	# 				self.sensor.LED(False)
	# 				# for template in rascan.templates:
	# 				# 	confirmation = self.sensor.indentify(base64.b64decode(template["fptemplate"].encode()))
	# 				# 	print(confirmation)
	# 				# 	if confirmation[1]["ACK"]:
	# 				# 		print(template["user_id"])
	# 				# 		print(template["id"])
	# 				threads = [threading.Thread(name="TP"+str(i), target=self.processor, args=(rascan.templates, i,)) for i in range(10) ]

	# 				for thread in threads:
	# 					thread.start()

	# 				time.sleep(3)

	# 				for thread in threads:
	# 					thread.join()

	# 				# while threading.active_count() != 3:
	# 				# 	print(threading.active_count(), " <- Active Account")
					
	# 				# self.stopScan = True
	# 			else:
	# 				self.sensor.LED(False)
	# 				break;
	# 		else:
	# 			rascan.ws.send('{ "command": "error", "message": "No Templates available or the rascan is not initialized properly!"}')
	# 			self.stopScan = True;

	# 		if self.stopScan:
	# 			break

	# 		# self.stopScan = False;
		
	# 	print ("Stop Scanning")

	# def processor(self, template, start):
	# 	print(len(template), start, len(template)-1)

	# 	while start <= len(template)-1:
	# 		confirmation = self.sensor.indentify(base64.b64decode(template[start]["fptemplate"].encode()))
	# 		print(confirmation)
	# 		if confirmation[1]["ACK"]:
	# 			print(template[start]["user_id"])
	# 			print(template[start]["id"])
	# 		start = start + 10
	# 		if start > len(template)-1:
	# 			break;

	# 	print(start, "End")