#system imports
import os
import time
import curses
import sys
import atexit
import math
from time import sleep

#make sure the camera is not in use
os.system("kill $(ps aux | grep '[c]amera' | awk '{print $2}')")


#camera module imports
import picamera


#imports from bot
from discovery_bot import pins
from discovery_bot import Movement
from discovery_bot import Ultrasound
from discovery_bot import Servo
from discovery_bot import light
from discovery_bot import infrared
from discovery_bot import Button
from discovery_bot import Buzzer


#camera init
camera = picamera.PiCamera()
camera.vflip = True


#calibrate servos
c_left = Servo(pins.SERVO_LEFT_MOTOR)
c_right = Servo(pins.SERVO_RIGHT_MOTOR)
c_left.set_normalized(0.5)
c_right.set_normalized(0.5)


movement = Movement()
servo = Servo()

#initialize the Buzzer
buzzer = Buzzer()

#initialize the ultrasound
usound = Ultrasound()

#initialize the physical button press event
b = Button()

#Clean up on exiting so that the motors are off and the image is destroyed.
@atexit.register
def goodbye():
        print "You are killing the PyNet"
        #os.system("rm *.jpg")
        movement.stop()
      
def takePicture(name = 0):
    buzzer.on()
    sleep(0.025)
    buzzer.off()
    print("Picture Taken")
    camera.capture(str(name) + ".jpg")
    sleep(0.025) 
        
def botLeft(time = 0.05, ignore = True):
    if (time != 0):
        movement.stop()
        sleep(0.15)
    
    if (ignore == False):
        firstDistance = getDistance()
    else:
        firstDistance = 0
    
    movement.setMotorSpeed(pins.SERVO_LEFT_MOTOR, -100)
    movement.setMotorSpeed(pins.SERVO_RIGHT_MOTOR, 100)
    
    sleep(time)
    if(time != 0):
        movement.stop()
        sleep(0.1)
    return (firstDistance, getDistance())
    
def botRight(time = 0.05, ignore = True):
    if(time != 0):
        movement.stop()
        sleep(0.15)
    
    if (ignore == False):
        firstDistance = getDistance()
    else:
        firstDistance = 0
    
    movement.setMotorSpeed(pins.SERVO_LEFT_MOTOR, 100)
    movement.setMotorSpeed(pins.SERVO_RIGHT_MOTOR, -100)
    sleep(time)
    if (time != 0):
        movement.stop()
        sleep(0.1)
    
    return (firstDistance, getDistance())
    
def botForward(speed = 100):
    movement.setMotorSpeed(pins.SERVO_LEFT_MOTOR, int(100 * (speed / 100)))
    movement.setMotorSpeed(pins.SERVO_RIGHT_MOTOR, int(70 * (speed / 100)))
    return getDistance()

def botBackward(speed = 100):
    movement.setMotorSpeed(pins.SERVO_LEFT_MOTOR, int(-100 * (speed / 100)))
    movement.setMotorSpeed(pins.SERVO_RIGHT_MOTOR, int(-70 * (speed / 100)))
    return getDistance()

# getDistance
# return: Gives a measurement back in cm on how far closest object is (Accurate up to 80cm)
#                       if 100 is returned then a valid distance couldn't be found (Could be to far out)
def getDistance(debug = False):
    distance = 0
    distanceList = []
    for x in range(0, 20):
        
        distance = usound.read()
            
        distanceList.append(distance)
        
    distanceList.sort()
    if (len(distanceList) % 2 != 0):
        distance = distanceList[int(math.floor(len(distanceList) / 2))] + distanceList[int(math.ceil(len(distanceList) / 2))]
        distance = distance / 2
    else:
        distance = distanceList[int(len(distanceList) / 2)]
    
    if debug == True:
        print("-----")
        print(x + 1, " values were read and sorted")
        print(distanceList)
        print("\nThe median is ", distance)
        print("-----")
    return distance   



def alignToDistance(shortestDistance):
    
    time = 0.05
    distanceTurn = (0, getDistance())
    threshold = 3
    counter = 0
    while (True):
            
        if (shortestDistance < distanceTurn[1] + threshold and shortestDistance > distanceTurn[1] - threshold):
            movement.stop()
            break
        
        distanceTurn = botRight(time = 0)
    
    
    threshold = 0.5
    botLeftTurn = True
    distanceTurn = botLeft(time)
    while (True):
        
        # A range is found that is close to the shortest point (Straight to the wall)
        if (shortestDistance < distanceTurn[1] + threshold and shortestDistance > distanceTurn[1] - threshold):
            movement.stop()
            break
        
        # Rotates the bot left and right to get the closest to the shortest point (Straight to a wall)
        if (distanceTurn[1] < shortestDistance and botLeftTurn == True):
            botLeftTurn = False
            distanceTurn = botRight(time)
        elif (distanceTurn[1] > shortestDistance and botLeftTurn == True):
            botLeftTurn = True
            distanceTurn = botLeft(time)
        elif (distanceTurn[1] < shortestDistance and botLeftTurn == False):
            botLeftTurn = True
            distanceTurn = botLeft(time)
        elif (distanceTurn[1] > shortestDistance and botLeftTurn == False):
            botLeftTurn = False
            distanceTurn = botRight(time)
        
        #time = time - 0.01
        #if (time <= 0):
            #time = 0.05

        print(distanceTurn[1])  


# Definition: during first runtime straighten the bot
def initialStraighten():
    
    shortestDistance = 100
    distanceTurn = (0, 0)
    
    for x in range(0, 24): #Scan 360 degress approx.

        distanceTurn = botRight()

        print(distanceTurn)
        if (distanceTurn[1] < shortestDistance):
            shortestDistance = distanceTurn[1]
        elif (distanceTurn[1] < shortestDistance):
            shortestDistance = distanceTurn[1]
    
    print("shortestDistance ", shortestDistance)
    # Adjust to shortest distance
    
        
    alignToDistance(shortestDistance)
    sleep(0.5)

# gotoWall : head to wall and stop aprox. 10cm from the wall
def gotoWall():
    print("gotoWall")

    while (botForward() >= 50):
        pass
    
    while (botForward(speed = 100) >= 20):
        pass
    
    
    movement.stop()
    #sleep(1)
    #while (botBackward() <= 28):
        #pass
    
    #movement.stop()
    print("done")
    

# rotateNextWall: face direction to next wall right of botBackward
# pre: Assuming the bot is facing the wall near perfectly straight
def rotateNextWall():

    shortestDistance = 100
    distanceTurn = (100, 100)
    
    print("Running rotateNextWall")
    print(distanceTurn)
    
    # Adjust bot to face the next wall ///
    while (distanceTurn[0] <= distanceTurn[1] or distanceTurn[1] == 100):
            
        distanceTurn = botRight(ignore = False)
        print("1-", distanceTurn)
        
    while (distanceTurn[0] >= distanceTurn[1] or distanceTurn[0] == 100):
        distanceTurn = botRight(ignore = False)
        print("2-", distanceTurn)
    
    shortestDistance = distanceTurn[0]
    
    print("Rotate looking for shortest of ", shortestDistance)
    # ///
    
    alignToDistance(shortestDistance)
    
    
        
if __name__ == "__main__":
    buttonFlag = False
    movement.stop()
    
    menuInput = int(raw_input("1. Ultrasound test\n2. Bot Forward\n3. Start main program\n"))
    # Get into initial position
    
    if menuInput == 1:
        while not raw_input("Enter to get a input"):
            print("Distance is ", getDistance(debug = True))
    elif menuInput == 2:
        while True:
            botForward()
    elif menuInput == 3:       
        initialStraighten()
        gotoWall()
        rotateNextWall()
        
        while True:
            sleep(2)
            name = 0
            while True:
                #if (b.button_pressed() is True): #On/Off control with button
                #if (buttonFlag is True):
                                #buttonFlag = False
                        #else:
                                #buttonFlag = True
                        #movement.stop()
                        #sleep(2.0)
                                    
                #if (buttonFlag is False):            
                gotoWall()
                
                print("Done straighten")
                sleep(0.5)
                
                rotateNextWall()
                movement.stop()
                sleep(0.5)
                takePicture()
                print("Done finding next wall")

                #buttonFlag = False

            #movement.stop()
            #sleep(0.1)
            #buzzer.on()
            #sleep(0.1)
            #buzzer.off()
            #sleep(0.1)
            #buzzer.on()
            #sleep(0.1)
            #buzzer.off()
            #buttonFlag = False
        

                
        