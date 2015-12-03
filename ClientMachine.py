#!/usr/bin/python           # This is the client 
#V0.21

# If you call the program with an IP as a command line argument it will connect to that ip instead of using the file
# Toggle variable inputOrder from 1 to 0 to run with opposite pairs of walls
# Now shouldn't result in GUI reading everything at once

#Issues:
#			Pretty sure a couple chunks of code can now be cut by turning type into a variable earlier on
#				Window and Door sections once had varying parameters and now they're the same apart from type
#			ISSUE: UNABLE TO DETERMINE CORRECTNESS OF OBJECTS ON FIRST WALL
#			presently assuming we are getting dimensions in order that we received for wall


#####IMPORTS#####
import socket
import ipaddress
import sys
import re
import os
#####END IMPORTS#####

#####FUNCTIONS#####
def redoOldFile(file):
   file.seek(0,0)
   lines = file.readlines()
   file.seek(0)
   file.truncate()
   n = 0
   while (n<len(lines)):
      if(lines[n] == "]\n" or lines[n] == "]" or lines[n] == "  }\n"):
         pass
      else:
         file.write(lines[n])
      n = n + 1
   
def fOutput(file, x1, x2, y1, y2, type):
   redoOldFile(file)
   file.write("  },\n")
   file.write("  {\n")     
   file.write("    \"y2\": " + str(y2) + ",\n")
   file.write("    \"type\": \"" + str(type) + "\",\n")
   file.write("    \"x2\": " + str(x2) + ",\n")
   file.write("    \"y1\": " + str(y1) + ",\n")
   file.write("    \"x1\": " + str(x1) + "\n")
   file.write("  }\n")
   file.write("]")
   file.flush()
   os.fsync(file.fileno())
   return
   
def fOutputNoComma(file, x1, x2, y1, y2, type):
   redoOldFile(file)
   file.write("  {\n")     
   file.write("    \"y2\": " + str(y2) + ",\n")
   file.write("    \"type\": \"" + str(type) + "\",\n")
   file.write("    \"x2\": " + str(x2) + ",\n")
   file.write("    \"y1\": " + str(y1) + ",\n")
   file.write("    \"x1\": " + str(x1) + "\n")
   file.write("  }\n")
   file.write("]")
   file.flush()
   os.fsync(file.fileno())
   return

###Ensures that objects being placed within room do not exceed room boundaries
def checkDimensioning(x1, x2, y1, y2, maxX, maxY):
   finalDimensions = [x1,x2,y1,y2]
   if(int(x1) > int(maxX) and int(maxX) != 0):
      finalDimensions[0] = maxX
   elif(int(x1) < 0):
      finalDimensions[0] = 0
   if(int(x2) > int(maxX) and int(maxX) != 0):
      finalDimensions[1] = maxX
   elif(int(x2) < 0):
      finalDimensions[1] = 0
   if(int(y1) > int(maxY) and int(maxY) != 0):
      finalDimensions[2] = maxX
   elif(int(y1) < 0):
      finalDimensions[2] = 0
   if(int(y2) > int(maxY) and int(maxY) != 0):
      finalDimensions[3] = maxX
   elif(int(y2) < 0):
      finalDimensions[3] = 0
   
   return finalDimensions
#####END FUNCTIONS#####

#####VARIABLE SETUP#####
s = socket.socket()         # Create a socket
port = 12345                # Reserve a port
ipLine = "192.168.2.109"
f = open('data.txt', 'w+') 	#Wipes old file
mess = "The beginning"
wallCount = 0
needComma = 0
wallY = 0
wallX = 0
pDimensions = [0,0,0,0]
connectionSuccess = 0
pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
objectLocation = [0,0]
windowLoc  = [0,0] 	#0-unitialized, first number corresponds to wall		
doorLoc = [0,0]

inputOrder = 1 #0 = opposite walls, 1 = clockwise walls
#####END VARIABLE SETUP#####

#####CONNECTION STUFF#####
if (len(sys.argv)<2):

   print("Attempting to connect to the default ip of : "+ ipLine)

else:
   ipLine = sys.argv[1]
   print("Attempting to connect to ip : " + ipLine)
   while(pattern.match(ipLine) == None):
      print("The only acceptable argument that can be given to this program is an IP\n Please enter the IP of the server you wish to connect to.")
      ipLine = input()
   
while(connectionSuccess == 0):
   try:
      s.connect((ipLine, port))
      connectionSuccess = 1
   except TimeoutError:
      connectionSuccess = 0
      print("Connection timed out, are you sure you entered the correct IP?")
      ipLine = ""
      while(pattern.match(ipLine) == None):
         print("The only acceptable argument that can be given to this program is an IP\n Please enter the IP of the server you wish to connect to.")
         ipLine = input()
		 
print("Connected! Processing data input")

f.write("[\n")
f.write("\n]\n")


#####END CONNECTION STUFF#####

#####MESSAGE HANDLING#####
while mess != "THE END":				#while server says there is more to come
   mess = s.recv(1024).decode('utf-8') 	#accept input

   if mess != "THE END":   #write input to file
   ###Default assumption was opposite walls will be provided (ie Left/Right/Top/Bot)
   ###
      
      if mess[1] == 'A':
         #It's a wall
         if wallCount == 0:
            result = ''.join([i for i in mess if i.isdigit()])
            fOutputNoComma(f, 0, 0, 0, result, "Wall")
            wallCount = wallCount + 1
            wallY = result
         elif wallCount == 1:
            if(inputOrder == 1):
               #Fill in Second, third, and final Wall
               result = ''.join([i for i in mess if i.isdigit()])
               fOutput(f, 0, result, wallY, wallY, "Wall")
               wallX = result
               fOutput(f, wallX, wallX, 0, wallY, "Wall")
               fOutput(f, 0, wallX, 0, 0, "Wall")
            wallCount = wallCount + 1
         elif wallCount == 2:
            if(inputOrder == 0):
               result = ''.join([i for i in mess if i.isdigit()])
               fOutput(f, 0, result, wallY, wallY, "Wall")
               wallX = result
               fOutput(f, wallX, wallX, 0, wallY, "Wall")
               fOutput(f, 0, wallX, 0, 0, "Wall")
            wallCount = wallCount + 1
         elif wallCount == 3:
            wallCount = wallCount + 1
         else:
            print("ERROR, MORE THAN 4 WALLS MARKED")
      elif mess[1] == 'I':
         #It's a window
         result = ''.join([i for i in mess if i.isdigit()])

         if(windowLoc[0] == 0):
            if(wallCount == 0 or wallCount > 4):
               print("WALL NOT MARKED FIRST")
            elif(wallCount == 1): #first horizontal wall
               windowLoc[0] = 1
               windowLoc[1] = 	result;	   
               
            elif(wallCount == 2): #on 0,0 - x,0 wall
               windowLoc[0] = 2
               windowLoc[1] = 	result;	   
               
            elif(wallCount == 3): #on 0,0 - 0,y wall
               windowLoc[0] = 3
               windowLoc[1] = 	result;	   
               
            elif(wallCount == 4): #on x,0 - x,y wall
               windowLoc[0] = 4
               windowLoc[1] = 	result
               
         elif(windowLoc[0] == 1):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(windowLoc[1], result, wallY, wallY, wallX, wallY)
            elif(inputOrder == 1):
               pDimensions = checkDimensioning(windowLoc[1], result, 0, 0, wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Window")

         elif(windowLoc[0] == 2):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(windowLoc[1], result, 0, 0, wallX, wallY)
            elif(inputOrder == 1):
               pDimensions = checkDimensioning(wallX, wallX, windowLoc[1], result, wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Window")

         elif(windowLoc[0] == 3):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(0, 0, windowLoc[1], result, wallX, wallY)
            elif(inputOrder == 1):
               pDimensions = checkDimensioning(max(int(wallX) - int(windocLoc[1]),0), max(int(wallX) - int(result), 0), wallY, wallY, wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Window")

         elif(windowLoc[0] == 4):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(wallX, wallX, windowLoc[1], result, wallX, wallY)
            elif(inputOrder == 1):
               pDimensions = checkDimensioning(0, 0, max(int(wallY) - int(windowLoc[1]), 0), max(int(wallY) -int(result),0), wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Window")

      elif mess[1] == 'O':
         #Door/Gap
		 
         result = ''.join([i for i in mess if i.isdigit()])

		 
         if(doorLoc[0] == 0):
            if(wallCount == 0 or wallCount > 4):
               print("WALL NOT MARKED FIRST")
            elif(wallCount == 1): #on 0,y - x,y wall
               doorLoc[0] = 1;
               doorLoc[1] = 	result;	   
               
            elif(wallCount == 2): #on 0,0 - x,0 wall
               doorLoc[0] = 2;
               doorLoc[1] = 	result;	   
               
            elif(wallCount == 3): #on 0,0 - 0,y wall
               doorLoc[0] = 3;
               doorLoc[1] = 	result;	   
               
            elif(wallCount == 4): #on x,0 - x,y wall
               doorLoc[0] = 4;
               doorLoc[1] = 	result;	   
               
         elif(doorLoc[0] == 1):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(doorLoc[1], result, wallY, wallY, wallX, wallY)

            elif(inputOrder == 1):
               pDimensions = checkDimensioning(doorLoc[1], result, 0, 0, wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Door")

         elif(doorLoc[0] == 2):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(doorLoc[1], result, 0, 0, wallX, wallY)

            elif(inputOrder == 1):
               pDimensions = checkDimensioning(wallX, wallX, doorLoc[1], result, wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Door")

         elif(doorLoc[0] == 3):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(0, 0, doorLoc[1], result, wallX, wallY)

            elif(inputOrder == 1):
               pDimensions = checkDimensioning(max(int(wallX) - int(doorLoc[1]),0), max(int(wallX) - int(result), 0), wallY, wallY, wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Door")
         elif(doorLoc[0] == 4):
            if(inputOrder == 0):
               pDimensions = checkDimensioning(wallX, wallX, doorLoc[1], result, wallX, wallY)
            elif(inputOrder == 1):
               pDimensions = checkDimensioning(0, 0, max(int(wallY) - int(doorLoc[1]),0), max(int(wallY) - int(result),0), wallX, wallY)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Door")
      elif mess[1] == 'E':
         #It is a lectern
         print("FOUND A LECTERN PART")
         result = ''.join([i for i in mess if i.isdigit()])
         if objectLocation[0] == 0:
            print("0=0")
            objectLocation[0] = result
         elif objectLocation[1] == 0:
            print("1=0")
            objectLocation [1] = result
            pDimensions = checkDimensioning(int(objectLocation[0]), int(objectLocation[0]) + 40, int(result), int(result) +40, wallX, wallY)
            print(pDimensions)
            fOutput(f, pDimensions[0], pDimensions[1], pDimensions[2], pDimensions[3], "Lectern")
      else:
         #Unknown
         print("UNKNOWN CODE")

   else:
      print("Received Program Closure Code")
#####END MESSAGE HANDLING#####

s.close()                   # Close the socket when done
f.close()