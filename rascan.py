import websocket
import json
from GTMain import App
import threading
import time

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
		self.templates = []
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
				print("Check Starting")
				threading.Thread(name="CS1", target=self.app.scanLoop, args=()).start()
				self.th["cs_0"][len(self.th["cs_0"])-1].start()
			else:
				if templates["success"] == True and len(resp["results"]) > 0:
					self.sth.append(
						threading.Thread(
							name="", 
							target=self.app.setTemplate, 
							args=(resp["results"][0]["fptemplate"], resp["results"][0]["users"]["id"], self.ws, )))
					self.sth[0].start()
					self.sth[0].join()
					self.ctr += 1
					if resp["from"] == resp["total"]-1:
						print("Check Starting")
						threading.Thread(name="CS2", target=self.app.scan, args=()).start()
					else:
						print(resp["from"])
						print(resp["total"]-1)
				else:
					print("Check Starting")
					threading.Thread(name="CS3", target=self.app.scan, args=()).start()
		elif resp == "re-init":
			print("Re-initializing Sensor")
			self.app.stopScan = True
			time.sleep(3)
			self.app.stopScan = False
			self.templates = []
			self.initialize()
		else:
			print(templates)
			self.app.sensor.LED(False)
			print("Enrollment Starting")
			self.app.stopScan = True
			time.sleep(3)
			self.app.stopScan = False
			NFP1 = threading.Thread(name="NFP1", target=self.app.enroll, args=(tempId, self.ws, ))
			NFP1.start()

	def on_error(self, ws, error):
		print(error)

	def on_close(self, ws):
		print("### Socket Closed ###")

	def on_open(self, ws):
		print("### Socket Open ###")
		self.initialize()

	def initialize(self):
		self.ws.send('{"command": "initialize"}')
		print("### Initializing Rascan ###")

if __name__ == '__main__':
	Rascan()
