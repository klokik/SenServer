import serial
import os

class SensorBus(object):
	def __init__(self,devices,rate):
		self.devices = devices
		self.rate = rate
		self.connected = False

	def connect(self):
		if self.connected:
			return

		print("Not connected, connecting to SensorBus")
		while not self.connected:
			print(self.devices)
			device_list = list(filter(os.path.exists,self.devices))

			for dev in device_list:
				port = serial.Serial()
				port.baudrate = self.rate
				port.port = dev
				port.timeout = 0.1

				try:
					port.open()
					self.serial = port
					self.connected = True
					print("Serial port {0} succesfully opened".format(port.portstr))
					return
				except serial.SerialException as e:
					print("Unable to open serial port ({0},{1})".format(port.portstr,e))
					continue
			else:
				print("Waitig for valid serial port to appear")
				sleep(1)

	def close(self):
		pass

	def get(self,uid,line):
		self.serial.write(bytearray(line+"\n","ascii"))
		self.serial.flush()
		line = self.serial.readline().decode("utf-8")
		if line.endswith("\r\n"):
			line = line[:-2]

		return line

	def set(self,uid,line):
		if not self.connected:
			self.connect()
		print(line)
		self.serial.write(bytearray(line+"\n","ascii"))
		self.serial.flush()

	def getDevices(self):
		return [0]