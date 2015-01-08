import sensorbus

class Sensor(object):
	def __init__(self,bus,uid):
		self.uid = uid
		self.bus = bus
		self.type = self.getType()
		self.properties = {}
		pass

	def getType(self):
		return self.bus.get(self.uid,"get type")

	def getData(self):
		return str(properties).replace(":","=").replace("'",'"')

	def getProperty(self,key):
		return self.bus.get(self.uid,"get {0}".format(key))

	def setProperty(self,key,value):
		self.bus.set(self.uid,"set {0} {1}".format(key,value))

	def update(self):
		items = self.bus.get(self.uid,"list").split(' ')
		while " " in items:
			items.remove(" ")
		while "" in items:
			items.remove("")

		for item in items:
			try:
				a = self.getProperty(item);
				self.properties[item] = float(a) #float(self.getProperty(item))
			except ValueError:
				print("unable to convert string '{0}' to float, item = '{1}'".format(a,item))
