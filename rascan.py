import websocket
import json
from GTMain import App
import threading

class Rascan:
	def  __init__(self):
		websocket.enableTrace(True)
		self.ws = websocket.WebSocketApp(
			"ws://localhost:8081/rascan/socket", 
			on_message = self.on_message, 
			on_error = self.on_error, 
			on_close = self.on_close)

		self.app = App()
		self.ws.on_open = self.on_open
		self.terminator = False
		self.templates = []

		t1 = threading.Thread(target=self.ws.run_forever)
		t1.start()

	def on_message(self, ws, message):
		print(message)
		templates = json.loads(message)
		if templates["success"] == True and len(templates["results"]) > 0:
			self.templates.append(templates["results"][0])
		else:
			threading.Thread(target=self.app.scanLoop).start()


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