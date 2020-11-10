import cv2
import os
import numpy as np
import time
import shutil

base_dir = os.path.dirname(os.path.realpath(__file__))
cam = cv2.VideoCapture(0)
#video = cv2.VideoCapture('video.mp4')
#cam.set(3,1920)
#cam.set(4,1080)
face_id = input ('\n Nombre:  ')
#cv2.namedWindow("Face_Load")
directorio_base = "{}/dataset/".format(base_dir)
list_person = os.listdir(directorio_base)
print(list_person)

arr = [1]

for p in list_person:
    id_deo = p.split("-")[0]
    nombre = p.split("-")[1]
    arr.append(int(id_deo))
    #print("ID: {}, Nombre: {}".format(id_deo,nombre))

arr.sort()
print(arr)
print("numero maximo:" + str(max(arr)+1))

directorio=directorio_base+str(int(max(arr)+1))+"-"+face_id
print(directorio)
source_img = "{}/Base/avion-022.png".format(base_dir)
destination_img = "{}/images/{}.png".format(base_dir,face_id)
try: 
    shutil.copyfile(source_img, destination_img)
    print('Archivo: '+destination_img)
    print("File copied successfully.") 
  
# If source and destination are same 
except shutil.SameFileError: 
    print("Source and destination represents the same file.") 
  
# If destination is a directory. 
except IsADirectoryError: 
    print("Destination is a directory.") 
  
# If there is any permission issue 
except PermissionError: 
    print("Permission denied.") 
  
# For other errors 
except: 
    print("Error occurred while copying file.") 
face_name = str(max(arr)+1)+"-"+face_id

try:
    os.mkdir(directorio)
except OSError:
    print("La creación del directorio %s falló" % directorio)
else:
    print("Se ha creado el directorio: %s " % directorio)
img_counter = 0
conteo = 1

while True:
    
    ret, frame = cam.read()
    cv2.imshow("Face_Load", frame)
    if not ret:
        break
    k = cv2.waitKey(1)
    #while (video.isOpened()):
        # Capture frame-by-frame 
    #    ret, frame1 = video.read() 
    #    if ret == True: 
   
           # Display the resulting frame 
    #       cv2.imshow('Frame', frame1) 
   
           # Press Q on keyboard to  exit 
    #       if cv2.waitKey(25) & 0xFF == ord('q'): 
    #          break
   
           # Break the loop 
    #       else:  
    #        break

    if img_counter == 140:
        # ESC pressed
        print("Proceso terminado")
        break
    elif conteo == 1:
        # SPACE pressed
        img_name = "{}_{}.png".format(face_name, img_counter)
        cv2.imwrite("{}/{}".format(directorio,img_name), frame)
        print("{} written!".format(img_name))
        img_counter += 1
        time.sleep(0.03)

cam.release()
#video.release()
cv2.destroyAllWindows()
