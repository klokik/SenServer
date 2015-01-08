import sensor
import sensorbus
from functools import partial
import threading
import http.server
import socketserver
import datetime


class SenHTTPRequestHander(http.server.BaseHTTPRequestHandler):
	sen_server_inst = None

	def do_GET(self):
		if self.path == "/favicon.ico":
			self.send_response(404)
			return

		self.send_response(200)
		self.send_header("Content-type", "text/plain")
		self.end_headers()

		tokens = self.path.split("?")

		response = "dildo"

		try:
			if tokens[0] == "/sensors":
				response = str(self.sen_server_inst.bus.getDevices())

			if tokens[0] == "/data":
				k1, v1 = tokens[1].split("=")
				if k1 == "uid" and (int(v1) in self.sen_server_inst.actual):
					response = str(self.sen_server_inst.actual[int(v1)]).replace("'",'"')

			if tokens[0] == "/history":
				k1, v1 = tokens[1].split("=")
				if k1 == "uid" and (int(v1) in self.sen_server_inst.history):
					response = str(self.sen_server_inst.history[int(v1)]).replace("'",'"')
		except Exception as e:
			pass

		self.wfile.write(response.encode("utf-8"))
		pass

	def do_POST(self):
		self.send_response(202)
		self.send_header("Content-type", "text/plain")
		self.end_headers()

		response = "dildo"
		try:
			tokens = self.path.split("?")

			if tokens[0] == "/set":
				k1, v1 = tokens[1].split("=")
				k2, v2 = tokens[2].split("=")
				if k1 == "uid":
					self.sen_server_inst.sensors[int(v1)].setProperty(k2,float(v2))
					response = "OK"
		except Exception as e:
			print(e)
			pass

		self.wfile.write(response.encode("utf-8"))

class SenServer(object):
	def __init__(self,address="",port=80):
		self.address = address
		self.port = port

		self.bus = sensorbus.SensorBus(["/dev/ttyUSB0","/dev/ttyUSB1"],115200)
		self.running = False

		self.timer_interval = 2
		self.history = {}
		self.actual = {}
		self.sensors = {}

	def run(self):
		SenHTTPRequestHander.sen_server_inst = self
		print("Waiting for address to free, and creating server")
		while True:
			try:
				self.httpd = socketserver.TCPServer((self.address,self.port),SenHTTPRequestHander)
				break
			except PermissionError:
				print("You have not enough permissions to serve it")
				return
			except OSError:
				time.sleep(5)

		self.bus.connect()
		for dev in self.bus.getDevices():
			self.sensors[dev] = sensor.Sensor(self.bus,dev)
			self.history[dev] = []

		self.running = True
		self.runTimer()

		while self.running:
			try:
				self.httpd.handle_request()
			except KeyboardInterrupt:
				print("Stopping server")
				self.stop()

		self.httpd.socket.close()
		print("Done")

	def runTimer(self):
		for key,item in self.sensors.items():
			item.update()
			self.actual[item.uid] = item.properties
			self.actual[item.uid]["datetime"] = str(datetime.datetime.now())
			self.history[item.uid].append(self.actual[item.uid])

		if self.running:
			self.timer = threading.Timer(self.timer_interval,self.runTimer)
			self.timer.start()

	def stop(self):
		self.running = False
		self.bus.close()