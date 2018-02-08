import websocket
import json
from GTMain import App
import threading

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
		self.counter = 0;

		t1 = threading.Thread(target=self.ws.run_forever)
		t1.start()

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
		print(templates)
		resp = templates["response"]
		if templates["message"] == "NFP":
			self.templates.append(resp)
			print("Enrollment Starting")
			t4 = threading.Thread(target=self.app.scanLoop, args=(self,))
			t4.start()
		else:
			if templates["success"] == True and len(resp["results"]) > 0:
				print("Inserting template to memory")
				self.templates.append(resp["results"][0])
				if resp["from"] == resp["total"]-1:
					print("Enrollment Starting")
					t3 = threading.Thread(target=self.app.scanLoop, args=(self,))
					t3.start()
				else:
					print(resp["from"])
					print(resp["total"]-1)
			else:
				print("Enrollment Starting")
				t2 = threading.Thread(target=self.app.scanLoop, args=(self,))
				t2.start()

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
