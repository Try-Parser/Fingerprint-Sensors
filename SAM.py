from GTSensor import GTSensor
import time

class App:
	def __init__(self):
		self.sensor = GTSensor('/dev/ttyAMA0', timeout=2, baudrate=9600)

		_initialization_response = self.sensor.initialize(True, True)
		time.sleep(0.5)

		print(_initialization_response)


		print ("Setting baudrate from 9600 to 57600")
		baudrateResult = self.sensor.setBaudrate(57600)
		print ("Setting is done testing for LED lights")
		self.sensor.LED(True)
		time.sleep(0.5)
		self.sensor.LED(False)

	def __capture_the_lights__(self, idx): 
		while True:
			procced = False
			if not idx.isdigit():
				print("Please Enter a number")
				return False

			if self.sensor.senseFinger()[0]['Parameter'] == 0:
				procced = True
			
			if procced:
				print ("Capturing Fingerprint")
				time.sleep(0.1)
				if self.sensor.captureFinger(True)['ACK']:
					return True				

	def enroll(self):
		__id__ = input("Enter ID : ")
		self.sensor.LED(True)
		time.sleep(0.1)
		print ("Please put your finger on the sensor.")

		if __capture_the_lights__(__id__):
			template = self.sensor.genTemplate()

			if __capture_the_lights__(__id__):
				confirmation = self.sensor.indentify(template[1]['Data'])
				print (confirmation)
		else:
			self.enroll()



		# while True:
		# 	procced = False
		# 	if not __id__.isdigit():
		# 		print("Please Enter number")
		# 		self.enroll()

		# 	if self.sensor.senseFinger()[0]['Parameter'] == 0:
		# 		procced = True
			
		# 	if procced:
		# 		print ("Capturing Fingerprint")
		# 		time.sleep(0.1)
		# 		captureResponse = self.sensor.captureFinger(True)
		# 		print (captureResponse)
				
		# 		time.sleep(0.2)
		# 		print ("Generating template")
		# 		template = self.sensor.genTemplate()

		# 		print(template)
		# 		break

		print ("terminitation")
		self.sensor.LED(False)
		self.sensor.close()
		exit(1)


app=App()
app.enroll()




