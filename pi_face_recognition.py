# USAGE
# python pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import tkinter
from tkinter import PhotoImage
from tkinter.font import Font
import imutils
import pickle
import time
import cv2
import pyttsx3
from queue import Full, Queue, Empty
from threading import Thread, Event



def cargarModelo():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--cascade", required=True,
        help = "path to where the face cascade resides")
    ap.add_argument("-e", "--encodings", required=True,
        help="path to serialized db of facial encodings")
    args = vars(ap.parse_args())
    print("[INFO] loading encodings + face detector...")
    data = pickle.loads(open(args["encodings"], "rb").read())
    detector = cv2.CascadeClassifier(args["cascade"])

    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    return detector,data,vs

# start the FPS counter
#fps = FPS().start()

def detectar(detector,data,vs,resultado_queue: Queue,resultado_event:Event,stop_event:Event):
    # loop over frames from the video file stream
    contador_fps = 0
    contador_detecciones = 0
    while not stop_event.is_set():
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        contador_fps+=1
        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(160, 160),
            flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        rects = rects
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        #Cotar el rects para que solo haya uno

        if len(rects) > 1:
            rects = rects[:1]
        if contador_fps > 40:
            contador_fps = 0
            contador_detecciones =0

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"],encoding)
            name = "No registrado"
            print("deteccion")
            contador_detecciones+=1
            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)
            # update the list of names
            if contador_detecciones > 3:
                resultado_event.set()
                resultado_queue.put_nowait(name)
                voz(name)
                contador_detecciones = 0 
                resultado_event.clear()
            names.append(name)



class App:
    def __init__(self, window, resultado_queue:Queue, resultado_event: Event):
        print("iniciando UI")
        self.window = window
        self.font = Font(family="Arial",size=40)
        #self.window.overrideredirect(True)
        self.window.wm_attributes("-fullscreen","true")
        self.resultado_evento = resultado_event
        self.resultado_queue = resultado_queue
        self.fontStyle = Font(family="Arial", size=18)
        # Create a canvas that can fit the above video source size
        self.imagen=PhotoImage(file="logo-sit-blanco.png")
        self.label = tkinter.Label(window,compound=tkinter.CENTER)
        self.label.pack()
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 300
        self.num=0
        self.update()
        #self.window
        self.window.mainloop()
        
    def update(self):
        try:
            hora = time.strftime("%H:%M")
            if self.resultado_evento.is_set():
                res = self.resultado_queue.get()
                archivo = "logo-sit-rojo.png" if res == "No registrado" else "logo-sit-verde.png"
                self.imagen=PhotoImage(file=archivo)
                self.label.configure(image=self.imagen,text="\n\n\n\n\n\n\n\n\n\n\n"+hora,fg="white",font=self.font)
                self.label.image=self.imagen
                self.window.after(4000,self.update)
            else:
                txt = "\n\n\n\n\n\n\n\n\n\n\n"+hora
                self.imagen=PhotoImage(file="logo-sit-blanco.png")
                self.label.configure(image=self.imagen,text=txt,fg="white",font=self.font)
                self.label.image=self.imagen
                #time.sleep(0.3)
                self.window.after(self.delay,self.update)
        except Empty:
            pass

def voz(nombre):
    engine = pyttsx3.init()
    # Se genera la voz a partir de un texto
    engine.setProperty('rate',140)
    # print(texto)
    texto=""
    if nombre == "No registrado":
        texto="No estas registrado dentro de la base de datos, porfavor contáctate con alguien del equipo de sit"
    else:
        texto = "Bienvenido a sit electronics "+nombre
        
    engine.say(texto)
    # Se reproduce la voz
    engine.runAndWait()


def main():
    detector,data,vs= cargarModelo()
    #detectar(detector,data,vs)
    resultado_queue = Queue()
    resultado_event= Event()
    stop_event= Event()
#    App(tkinter.Tk(), resultado_queue,pausa_event,cargando_event)


    try:
        #Hilo de ejecuíón que se encarga del procesamiento
        Thread(name="hilo2",target=detectar, args=[detector,data,vs,resultado_queue,resultado_event,stop_event]).start()
        #Hilo principal del codigo, se encarga de la UI, Tkinter no funciona bien en otro hilo que no sea el principal 
        App(tkinter.Tk(), resultado_queue,resultado_event)
    finally:
        print("APRETANDO STOP")
        #si se cierra la ui se gatilla el evento Stop, el que también detiene el procesamiento
        stop_event.set()


if __name__ == "__main__":
    main()