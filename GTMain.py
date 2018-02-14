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
									if template[0][0]["ACK"]:
										payload = '{ "command": "ST", "template": "'+ base64.b64encode(template[0][1]["Data"]).decode() +'", "id":'+str(tempId)+', "message": "Finger Template is confirmed"}'
										print(payload)
										ws.send(payload)
									else:
										ws.send(template[1])
								else:
									if efr["Parameter"] == "NACK_ENROLL_FAILED":
										ws.send('{ "command": "error", "message": "Failed to enroll please try again.", "id": "'+str(tempId)+'"}')
										print("Failed to enroll please try again")
									elif efr["Parameter"] == "NACK_BAD_FINGER":
										ws.send('{ "command": "error", "message": "Bad fingprint captured.", "id": "'+str(tempId)+'"}')
										print("Bad fingprint captured.")
									else:
										ws.send('{ "command": "error", "message": "'+str(tempId)+' is Already used and duplication occur.", "id": "'+str(tempId)+'"}')
										print(str(tempId) +" is Already used and duplication occur.!")
						else:
							if efr["Parameter"] == "NACK_ENROLL_FAILED":
								ws.send('{ "command": "error", "message": "Failed to enroll please try again.", "id": "'+str(tempId)+'"}')
								print("Failed to enroll please try again")
							else:
								ws.send('{ "command": "error", "message": "Bad fingprint captured.", "id": "'+str(tempId)+'"}')
								print("Bad fingprint captured.")
				else:
					if efr["Parameter"] == "NACK_ENROLL_FAILED":
						ws.send('{ "command": "error", "message": "Failed to enroll please try again.", "id": "'+str(tempId)+'"}')
						print("Failed to enroll please try again")
					else:
						ws.send('{ "command": "error", "message": "Bad fingprint captured.", "id": "'+str(tempId)+'"}')
						print("Bad fingprint captured.")
		else:
			if confirmation["Parameter"] == "NACK_DB_IS_FULL":
				ws.send('{ "command": "error", "message": "Database is full.", "id": "'+str(tempId)+'"}')
				print("Database is full.")
			elif confirmation["Parameter"] == "NACK_INVALID_POS":
				ws.send('{ "command": "error", "message": "'+str(tempId)+' must be 0 <> 999.", "id": "'+str(tempId)+'"}')
				print(str(tempId) +" must be 0 <> 999.")
			else:
				ws.send('{ "command": "error", "message": "'+str(tempId)+' is Already used.", "id": "'+str(tempId)+'"}')
				print(str(tempId) +" is Already used.")
		
		self.sensor.LED(False)
		print("Enroll terminitation.")

	def scan(self, ws):
		while not self.stopScan:
			self.sensor.LED(True)
			if self.__capture_the_lights__():
				indentify = self.sensor.security()
				cmd = ''
				if indentify["ACK"]:
					cmd = '{ "command": "auth", "message": "Acknowledge Finger.", "id": "'+str(indentify["Parameter"])+'" , "type": "true"}'
				else:
					cmd = '{ "command": "auth", "message": "'+indentify["Parameter"]+'", "type": "false" }'
				ws.send(cmd)
				print(indentify)
				self.sensor.LED(False)
			else:
				break;

		self.sensor.LED(False)

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
				return [template, '{"command": "error", "message": "'+str(tempId) +' is not used."}']
			else:
				print(str(tempId) +" must be 0 <> 999.")
				return [template, '{"command": "error", "message": "'+str(tempId) +'  must be 0 <> 999."}']

	def setTemplate(self, template, tempID, ws):
		stresponse = self.sensor.setTemplate(base64.b64decode(template.encode()), tempID)
		if not stresponse[0]["ACK"] and not stresponse[1]["ACK"]:
			ws.send('{ "command": "error",  "message": "'+stresponse[0]["Parameter"]+'", "id":"'+str(tempID)+'" }')

		print("setTmplate Response Below")
		print(stresponse)