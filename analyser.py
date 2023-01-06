import socket
import select
import sys
import time
import getopt
import os
import math
from datetime import datetime
import operator
import asyncio
import websockets
import subprocess
import json
import os.path
import threading
import functools

clear = lambda: os.system('clear')

hamming84=[0x15,0x02,0x49,0x5E,0x64,0x73,0x38,0x2F,0xD0,0xC7,0x8C,0x9B,0xA1,0xB6,0xFD,0xEA]
hamming_8_4_inverse = [
    0x01, 0xff, 0x01, 0x01, 0xff, 0x00, 0x01, 0xff,
    0xff, 0x02, 0x01, 0xff, 0x0a, 0xff, 0xff, 0x07,
    0xff, 0x00, 0x01, 0xff, 0x00, 0x00, 0xff, 0x00,
    0x06, 0xff, 0xff, 0x0b, 0xff, 0x00, 0x03, 0xff,
    0xff, 0x0c, 0x01, 0xff, 0x04, 0xff, 0xff, 0x07,
    0x06, 0xff, 0xff, 0x07, 0xff, 0x07, 0x07, 0x07,
    0x06, 0xff, 0xff, 0x05, 0xff, 0x00, 0x0d, 0xff,
    0x06, 0x06, 0x06, 0xff, 0x06, 0xff, 0xff, 0x07,
    0xff, 0x02, 0x01, 0xff, 0x04, 0xff, 0xff, 0x09,
    0x02, 0x02, 0xff, 0x02, 0xff, 0x02, 0x03, 0xff,
    0x08, 0xff, 0xff, 0x05, 0xff, 0x00, 0x03, 0xff,
    0xff, 0x02, 0x03, 0xff, 0x03, 0xff, 0x03, 0x03,
    0x04, 0xff, 0xff, 0x05, 0x04, 0x04, 0x04, 0xff,
    0xff, 0x02, 0x0f, 0xff, 0x04, 0xff, 0xff, 0x07,
    0xff, 0x05, 0x05, 0x05, 0x04, 0xff, 0xff, 0x05,
    0x06, 0xff, 0xff, 0x05, 0xff, 0x0e, 0x03, 0xff,
    0xff, 0x0c, 0x01, 0xff, 0x0a, 0xff, 0xff, 0x09,
    0x0a, 0xff, 0xff, 0x0b, 0x0a, 0x0a, 0x0a, 0xff,
    0x08, 0xff, 0xff, 0x0b, 0xff, 0x00, 0x0d, 0xff,
    0xff, 0x0b, 0x0b, 0x0b, 0x0a, 0xff, 0xff, 0x0b,
    0x0c, 0x0c, 0xff, 0x0c, 0xff, 0x0c, 0x0d, 0xff,
    0xff, 0x0c, 0x0f, 0xff, 0x0a, 0xff, 0xff, 0x07,
    0xff, 0x0c, 0x0d, 0xff, 0x0d, 0xff, 0x0d, 0x0d,
    0x06, 0xff, 0xff, 0x0b, 0xff, 0x0e, 0x0d, 0xff,
    0x08, 0xff, 0xff, 0x09, 0xff, 0x09, 0x09, 0x09,
    0xff, 0x02, 0x0f, 0xff, 0x0a, 0xff, 0xff, 0x09,
    0x08, 0x08, 0x08, 0xff, 0x08, 0xff, 0xff, 0x09,
    0x08, 0xff, 0xff, 0x0b, 0xff, 0x0e, 0x03, 0xff,
    0xff, 0x0c, 0x0f, 0xff, 0x04, 0xff, 0xff, 0x09,
    0x0f, 0xff, 0x0f, 0x0f, 0xff, 0x0e, 0x0f, 0xff,
    0x08, 0xff, 0xff, 0x05, 0xff, 0x0e, 0x0d, 0xff,
    0xff, 0x0e, 0x0f, 0xff, 0x0e, 0x0e, 0xff, 0x0e
];

async def hello(websocket, path):
	last_sent = 0;
	last_recv = 0;
	
	lastCounter = {"bsdpF1":0}
	
	while True:
		if len(data) > 0:
			try:
				await websocket.send(json.dumps({"message":"pageRoll","data":data}))
			except Exception as e:
				print (e);
				break;
		
		if bsdpF1["serial"] != lastCounter["bsdpF1"]:
			try:
				await websocket.send(json.dumps({"message":"bsdpF1","data":bsdpF1}))
				lastCounter["bsdpF1"] = bsdpF1["serial"]
			except Exception as e:
				print (e);
				break;
		
		await asyncio.sleep(0.01)

def interfaceTest():
	print("Started the Analyser Websocket")
	
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	
	userinterfaceserver = functools.partial(hello)
	
	start_server = websockets.serve(userinterfaceserver, "127.0.0.1", 5680)
	
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()

# 8,1,2,3,4,5,6,7,Filler,Data
magazineShareCount = [0,0,0,0,0,0,0,0,0,0,0]
linesPerField = 16
linesToCount = linesPerField * 300
pageCounter={}

bsdpF1 = {"serial":0,"initialPage":"Unknown","networkIdent":"Unknown","time":"Unknown","reserved":[00,00,00,00],"statusDisplay":"Unknown"}

PRIMARYIP = "127.0.0.1"
PRIMARYPORT = 19761

try:
	opts, args = getopt.getopt(sys.argv[1:],"p:l:")
except getopt.GetoptError as err:
	print(err)
	sys.exit(2)

interface = threading.Thread(target=interfaceTest)
interface.start()

while(True):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((PRIMARYIP,PRIMARYPORT))

	sock.sendall(bytes("HELO", "utf-8"))
	starttime = time.time()
	lineCount=0
	while(True):
		inputready, outputready, exceptready = select.select([sock], [], [], 0 )
		if inputready:
			data = []
			for line in range(linesPerField):
				received = sock.recv(42)
				byte1 = hamming_8_4_inverse[received[0]]
				byte2 = hamming_8_4_inverse[received[1]]

				magazineN = (byte1 & ~(1 << 3))
				packetN = ((byte2 << 1) + ((byte1 & ~(7)) >> 3))

				if(magazineN == 0 and packetN == 25):
					magazineShareCount[8] += 1
				elif(packetN == 30 and magazineN == 0):	# Packet 8/30 (BSDP)
					designationCode = hamming_8_4_inverse[received[2]]
					ipU = hamming_8_4_inverse[received[3]]	# initial page units
					ipT = hamming_8_4_inverse[received[4]]	# Initial page tens
					ipS1 = hamming_8_4_inverse[received[5]]	# Initial page subcode 1
					ipS3 = hamming_8_4_inverse[received[7]]	# Inital page subcode 3
					
					s2M1byte = hamming_8_4_inverse[received[6]]
					s4M23byte = hamming_8_4_inverse[received[8]]
					
					ipS2 = (s2M1byte & ~(1 << 3))
					ipS4 = (s4M23byte & ~(1 << 3))
					
					ipM = ((s2M1byte & ~(3)) >> 3) + ((s4M23byte & ~(3)) >> 2)
					
					if(designationCode == 0):	# Format 1 BSDP
						bsdpF1["serial"] += 1
						bsdpF1["initialPage"] = format(ipM,'x') + format(ipT,'x') + format(ipU,'x') + ":" + format(ipS4,'x') + format(ipS3,'x') + format(ipS2,'x') + format(ipS1,'x')
						bsdpF1["statusDisplay"] = str(received[22:41])
						nic = (received[9] + received[10])
						toc = received[10]
						
				elif(packetN == 30 or packetN == 31):
					magazineShareCount[9] += 1
					#sys.stdout.buffer.write(received)
				elif(packetN == 0):
					pUnits = hamming_8_4_inverse[received[2]]
					pTens = hamming_8_4_inverse[received[3]]
					
					data.append({"mag":magazineN,"pTens":pTens,"pUnits":pUnits})
					
					#print("P" + str(magazineN) + str(pTens) + str(pUnits))
					if(pUnits == 15 and pTens == 15):
						magazineShareCount[10] += 1
					else:
						magazineShareCount[magazineN] += 1
						pageNumber = str(magazineN) + str(pTens) + str(pUnits)
						
						if pageNumber in pageCounter:
							pageCounter[pageNumber]["lastCycle"] = pageCounter[pageNumber]["thisCycle"]
							pageCounter[pageNumber]["thisCycle"] = datetime.now()
							pageCounter[pageNumber]["cycleTime"] = pageCounter[pageNumber]["thisCycle"] - pageCounter[pageNumber]["lastCycle"]
						else:
							pageCounter[pageNumber] = {"thisCycle":datetime.now()}
					
				else:
					magazineShareCount[magazineN] += 1

				if(lineCount > linesToCount):
					clear()
					lineCount = 0

					print("VBI Bandwidth Utilisation Analyser\n")
					fillerPct = ((magazineShareCount[8]/linesToCount)*100)
					print("8/25:	 		" + str(math.floor(fillerPct)) + "%")

					tFillPct = ((magazineShareCount[9]/linesToCount)*100)
					print("TFH:		 	" + str(tFillPct) + "%")

					dataPct = ((magazineShareCount[9]/linesToCount)*100)
					print("M/30 & M/31:            " + str(dataPct) + "%")

					print("\nPage Related Packets")

					Pct = ((magazineShareCount[1]/linesToCount)*100)
					print("1/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[2]/linesToCount)*100)
					print("2/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[3]/linesToCount)*100)
					print("3/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[4]/linesToCount)*100)
					print("4/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[5]/linesToCount)*100)
					print("5/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[6]/linesToCount)*100)
					print("6/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[7]/linesToCount)*100)
					print("7/yy:          		" + str(math.floor(Pct)) + "%")

					Pct = ((magazineShareCount[0]/linesToCount)*100)
					print("8/yy:          		" + str(math.floor(Pct)) + "%")
					
					print()
					
					if "1ff" in pageCounter:
						if "cycleTime" in pageCounter["1ff"]:
							print(pageCounter["1ff"]["cycleTime"])
							
					if "2ff" in pageCounter:
						if "cycleTime" in pageCounter["2ff"]:
							print(pageCounter["2ff"]["cycleTime"])
							
					if "3ff" in pageCounter:
						if "cycleTime" in pageCounter["3ff"]:
							print(pageCounter["3ff"]["cycleTime"])
							
					if "4ff" in pageCounter:
						if "cycleTime" in pageCounter["4ff"]:
							print(pageCounter["4ff"]["cycleTime"])
							
					if "5ff" in pageCounter:
						if "cycleTime" in pageCounter["5ff"]:
							print(pageCounter["5ff"]["cycleTime"])
							
					if "6ff" in pageCounter:
						if "cycleTime" in pageCounter["6ff"]:
							print(pageCounter["6ff"]["cycleTime"])
					
					if "7ff" in pageCounter:
						if "cycleTime" in pageCounter["7ff"]:
							print(pageCounter["7ff"]["cycleTime"])
							
					if "8ff" in pageCounter:
						if "cycleTime" in pageCounter["8ff"]:
							print(pageCounter["8ff"]["cycleTime"])

					lastMagShare = magazineShareCount
					magazineShareCount = [0,0,0,0,0,0,0,0,0,0,0]
				else:
					lineCount += 1
		time.sleep(0.02 - ((time.time() - starttime) % 0.02))
