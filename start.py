import senserver

def main():
	server = senserver.SenServer("",80)
	server.run()

if __name__ == "__main__":
	main()