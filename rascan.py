import websocket
import json
from GTMain import App
import threading
import time
import uuid

class Rascan:
	def  __init__(self):
		websocket.enableTrace(True)
		self.ws = websocket.WebSocketApp(
			"ws://192.168.254.103:8081/rascan/socket", 
			on_message = self.on_message, 
			on_error = self.on_error, 
			on_close = self.on_close)

		self.app = App()
		self.ws.on_open = self.on_open
		self.terminator = False
		self.sth = []
		self.ctr = 0

		w1 = threading.Thread(target=self.ws.run_forever)
		w1.start()

	def on_message(self, ws, message):
		templates = json.loads(message)
		resp = templates["response"]
		print(resp)
		if resp != "ISR" and resp != "re-init": 
			if templates["message"] == "NFP":
				self.app.stopScan = True
				print("Template synchronizing")
				self.sth.append(
					threading.Thread(
						name=str(uuid.uuid4()), 
						target=self.app.setTemplate, 
						args=(resp["fptemplate"], resp["user_id"], self.ws, )))
				self.sth[self.ctr].start()
				self.sth[self.ctr].join()
				self.ctr += 1
				self.app.stopScan = False
				print("Check Starting")
				threading.Thread(name=str(uuid.uuid4()), target=self.app.scan, args=()).start()
			else:
				if templates["success"] == True and len(resp["results"]) > 0:
					self.sth.append(
						threading.Thread(
							name=str(uuid.uuid4()), 
							target=self.app.setTemplate, 
							args=(
								resp["results"][0]["fptemplate"],
								resp["results"][0]["users"]["id"],
								self.ws, )))
					self.sth[self.ctr].start()
					self.sth[self.ctr].join()
					self.ctr += 1
					if resp["from"] == resp["total"]-1:
						print("Check Starting")
						threading.Thread(name=str(uuid.uuid4()), target=self.app.scan, args=()).start()
					else:
						print(resp["from"])
						print(resp["total"]-1)
				else:
					print("Check Starting")
					threading.Thread(name=str(uuid.uuid4()), target=self.app.scan, args=()).start()
		elif resp == "re-init":
			print("Re-initializing Sensor")
			self.app.stopScan = True
			time.sleep(4)
			self.app.stopScan = False
			self.initialize()
		elif resp == "ISR":
			cmd = json.loads(templates["message"])
			self.app.sensor.LED(False)
			print("Enrollment Starting")
			self.app.stopScan = True
			time.sleep(4)
			self.app.stopScan = False
			self.sth.append(threading.Thread(name=str(uuid.uuid4()), target=self.app.enroll, args=(cmd["id"], self.ws, )))
			self.sth[self.ctr].start()
			self.sth[self.ctr].join()
			self.ctr += 1		
			self.sth.append(threading.Thread(name=str(uuid.uuid4()), target=self.app.scan, args=()))
			self.sth[self.ctr].start()
			self.sth[self.ctr].join()
			self.ctr += 1

	def on_error(self, ws, error):
		print(error)

	def on_close(self, ws):
		print("### Socket Closed ###")

	def on_open(self, ws):
		print("### Socket Open ###")
		self.initialize()

	def initialize(self):
		self.ws.send('{"command": "init", "type": "scanner"}')
		resp = self.app.deleteAll()
		print(resp)
		print("### Initializing Rascan ###")

if __name__ == '__main__':
	Rascan()
