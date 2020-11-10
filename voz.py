import pyttsx3
import sys
import cv2
import os
import time


def textTovoice(texto):
    imagen=cv2.imread("Base/latam_horizontal.jpg",1)
    cv2.namedWindow("Reserva", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Reserva",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Reserva",imagen)
    # Se inicia el motor de voz
    engine = pyttsx3.init()
    #txtTovoice = input("Ingresa tu texto => ")
    # Se genera la voz a partir de un texto
    engine.setProperty('rate',140)
    #print(texto)
    engine.say("Tus datos biométricos no coinciden. Porfavor contacte a alguien de la empresa.")
    # Se reproduce la voz
    engine.runAndWait()
    

def embarque(nombre):
    list_person = os.listdir("dataset/")
    for p in list_person:
        #print(p+" "+nombre)
        face_name = p.split("-")[1]
        #print('FaceName: '+face_name)
        #print('Variable Nombre: '+nombre)
        #print('Variable File: '+p)
        if nombre == p:
            if os.path.exists("C:/Users/vicen/Desktop/Python/Embarque/images/{}.png".format(face_name)):
                imagen=cv2.imread("Negro-green.png",1)
                cv2.namedWindow("Reserva", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Reserva",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Reserva",imagen)
                # Se inicia el motor de voz
                engine = pyttsx3.init()
                # Se genera la voz a partir de un texto
                engine.setProperty('rate',140)
                #print(texto)
                engine.say("{}, Bienvenido".format(face_name))
                # Se reproduce la voz
                engine.runAndWait()
                time.sleep(3)                
                break
            else:
                imagen=cv2.imread("Negro-red.png",1)
                cv2.namedWindow("Reserva", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Reserva",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Reserva",imagen)
                # Se inicia el motor de voz
                engine = pyttsx3.init()
                # Se genera la voz a partir de un texto
                engine.setProperty('rate',140)
                # print(texto)
                engine.say("{}, No estas registrado dentro de la base de datos, porfavor contáctate con alguien del equipo de sit".format(face_name))
                # Se reproduce la voz
                engine.runAndWait()

if __name__ == "__main__":
    textTovoice(sys.argv[1])
