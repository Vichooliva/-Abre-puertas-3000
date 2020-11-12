import RPi.GPIO as GPIO
import time

pistola = 18
Puerta = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(led, GPIO.OUT)
GPIO.setup(switch, GPIO.IN)

for i in range(10):
    GPIO.output(pistola, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(pistola, GPIO.LOW)
    time.sleep(0.2)
    print('Switch status = ', GPIO.input(Puerta))

GPIO.cleanup()

If pin 18 is connected to an LED and pin 31 to a switch, as it is on my little GPIO learning board, we can see the LED flashing and the program will report the status of the switch.

There are a number of additional features related to input pins. We can enable the internal pullup or pulldown resistors on the Raspberry Pi by passing an additional parameter when we call setup, e.g.

GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)