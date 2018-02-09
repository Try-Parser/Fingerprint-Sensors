import websocket
import json
from GTMain import App
import threading
import time

class Rascan:
	def  __init__(self):
		websocket.enableTrace(True)
		self.ws = websocket.WebSocketApp(
			"ws://192.168.254.101:8081/rascan/socket", 
			on_message = self.on_message, 
			on_error = self.on_error, 
			on_close = self.on_close)

		self.app = App()
		self.ws.on_open = self.on_open
		self.terminator = False
		self.templates = []
		self.th = { "cs_0": [], "cs_1": [], "cs_2": [], "nfp_0":[] }

		w1 = threading.Thread(target=self.ws.run_forever)
		w1.start()

	# def on_message(self, ws, message):
	# 	templates = json.loads(message)
	# 	resp = templates["response"]
	# 	if templates["message"] == "NFP":
	# 		self.templates.append(resp)
	# 		print("Enrollment Starting")
	# 		t4 = threading.Thread(target=self.app.enroll, args=(self.ws,))
	# 		t4.start()
	# 	else:
	# 		if templates["success"] == True and len(resp["results"]) > 0:
	# 			print("Inserting template to memory")
	# 			self.templates.append(resp["results"][0])
	# 			if resp["from"] == resp["total"]-1:
	# 				print("Enrollment Starting")
	# 				t3 = threading.Thread(target=self.app.enroll, args=(self.ws,))
	# 				t3.start()
	# 			else:
	# 				print(resp["from"])
	# 				print(resp["total"]-1)
	# 		else:
	# 			print("Enrollment Starting")
	# 			t2 = threading.Thread(target=self.app.enroll, args=(self.ws,))
	# 			t2.start()

	def on_message(self, ws, message):
		templates = json.loads(message)
		resp = templates["response"]
		print(resp)
		if resp != "ISR" and resp != "re-init": 
			if templates["message"] == "NFP":
				self.templates.append(resp)
				print("Check Starting")
				self.th["cs_0"].append(threading.Thread(name="CS1", target=self.app.scanLoop, args=(self,)))
				self.th["cs_0"][len(self.th["cs_0"])-1].start()
			else:
				if templates["success"] == True and len(resp["results"]) > 0:
					print("Inserting template to memory")
					self.templates.append(resp["results"][0])
					if resp["from"] == resp["total"]-1:
						print("Check Starting")
						print(self.th)
						self.th["cs_1"].append(threading.Thread(name="CS2", target=self.app.scanLoop, args=(self,)))
						self.th["cs_1"][len(self.th["cs_1"])-1].start()
					else:
						print(resp["from"])
						print(resp["total"]-1)
				else:
					print("Check Starting")
					cs_2 = self.th["cs_2"]
					self.th["cs_2"].append(threading.Thread(name="CS3", target=self.app.scanLoop, args=(self,)))
					self.th["cs_2"][len(self.th["cs_2"])-1].start()
		elif resp == "re-init":
			print("Re-initializing Sensor")
			self.app.stopScan = True
			time.sleep(3)
			self.app.stopScan = False
			self.templates = []
			self.initialize()
		else:
			self.app.sensor.LED(False)
			print("Enrollment Starting")
			self.app.stopScan = True
			time.sleep(3)
			self.app.stopScan = False
			NFP1 = threading.Thread(name="NFP1", target=self.app.enroll, args=(self.ws,))
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
