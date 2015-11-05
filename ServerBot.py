#!/usr/bin/python          

import socket              
import time

mess = b"Thank you for connecting"

continueStatus = "y"


s = socket.socket()         
host = '0.0.0.0'
port = 12345                
s.bind((host, port))
escape = 0 
cLine = 0
maxLineCount = 0       

s.listen(5)                 
c, addr = s.accept()     	# Establish connection with client.
print ('Got connection from', addr)
while(escape == 0):
   cLine = 0
   f = open("Example.txt", 'r')

   for line in f:
      if (line == "PROGRAMEND"):
         escape = 1
         print("Escape trigger\n")
      elif (cLine < maxLineCount):
         cLine = cLine+1
      else:
         mess = line.encode('utf-8')
         c.send(mess)
         cline = cLine + 1
      time.sleep(4)
   maxLineCount = cLine
   f.close()

mess = "THE END".encode('utf-8')
c.send(mess)
c.close()              		# Close the connection