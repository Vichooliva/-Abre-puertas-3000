import serial, time
import subprocess

arduino = serial.Serial('COM9', 115200)
time.sleep(2)
while True:
   rawString = arduino.readline()
   string = str(rawString).split("'")[1].split("\\")[0]
   print(string)
   if (int(string)) < 180:
      process1 = subprocess.Popen(['python', 'recognize_video.py --detector face_detection_model --embedding-model openface_nn4.small2.v1.t7 --recognizer output\\recognizer.pickle --le output\\le.pickle'])
      break
#arduino.close()
