# USAGE
# python3 pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

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
import pygame
import RPi.GPIO as GPIO
from queue import Full, Queue, Empty
from threading import Thread, Event
#from usb_barcode_scanner import barcode_reader

Pistola = 18
Puerta = 31

#Se declaran los GPIO como salida, ya que,se les entrega energía
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Puerta, GPIO.OUT)
GPIO.setup(Pistola, GPIO.OUT)

def abrirpuerta():
    GPIO.output(Puerta, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(Puerta, GPIO.LOW)
    time.sleep(0.2)

def activarpistola():
    GPIO.output(Pistola, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(Pistola, GPIO.LOW)
    time.sleep(0.2)


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

def detectar(detector,data,vs,resultado_queue: Queue,resultado_event:Event,stop_event:Event,resultado_scanner:Queue,resultado_scanner_event:Event):
    # loop over frames from the video file stream
    pygame.init()
   
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
            resultado_scanner_event.clear()

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
                print(name)
                if name == "No registrado":
                    resultado_event.set()
                    resultado_queue.put_nowait(name)    
                    voz("0",name)
                    time.sleep(5)
                else:
                    name,code=name.split("-")
                    print(code)
                    voz("1",name)
                    resultado_queue.put_nowait("pedir")
                    resultado_event.set()
                    timeFin = time.time()+7 #tiempo de ahora más 5 segundos
                    #resultado_queue.put("pedir",True,1000)
                    timeNow = time.time()
                    while((not resultado_scanner_event.is_set()) and (timeFin>timeNow)):
                        timeNow = time.time()
                    
                    print("salio del while")
                    if resultado_scanner_event.is_set():
                        print("salio del while pq hay codigo")
                        codigo = resultado_scanner.get()
                        codigo=seccionar_rut(codigo)
                        print("Codigo entregado: ",codigo)
                        if codigo == code:
                            print("llegó ",name)
                            resultado_event.set()
                            resultado_queue.put_nowait("Si registrado")
                            voz("2",name)
                        else:
                            print("llegó ",name," pero no coincide el codigo")
                            resultado_event.set()
                            resultado_queue.put_nowait("No registrado")
                            voz("-1",name)
                    else:
                        
                        print("llegó",name," pero no puso el carnet")
                    #pedir_codigo(name)
                contador_detecciones = 0 
                
                resultado_scanner_event.clear()
            names.append(name)

def voz(code,name):
    #code = 0, no registrado
    #code = -1, qr no coincide
    #code = 1, pide QR
    #code = 2, qr coincide
    archivo = "Audios/Bienvenido "+name+".ogg"
        
    #engine = pyttsx3.init()
    if code == "0":
        pygame.mixer.Sound('No se encuentra registrado en nuestra base de datos.ogg').play()
    elif code == "-1":
        #pygame.mixer.Sound('').play()
        pygame.mixer.Sound('Audios/Los datos no coinciden.ogg').play()
    elif code== "1":
        pygame.mixer.Sound('Audios/acercar-cedula.ogg').play()
    else:
        pygame.mixer.Sound(archivo).play()
        """
        if name=="Nacho":
            pygame.mixer.Sound('Bienvenido ignacio.ogg').play()
        elif name =="Pablo":
            pygame.mixer.Sound('Bienvenido pablo.ogg').play()
        elif name =="Vicho":
            pygame.mixer.Sound('Bienvenido vicente.ogg').play()
        elif name =="Antonio":
            pygame.mixer.Sound('Bienvenido antonio.ogg').play()
         """        
"""
def pedir_codigo(name):    
    nombre,codigo_real = name.split('-')
    codigo_scanner = scanner()
    timeFin = time.time() +5
    while(time.time() < timeFin):
        linea = barcode_reader()
"""
def seccionar_rut (linea):
    #print("entró al seccionar rut")
    #httpsÑ--portal.sidiv.registrocivil.cl-docstatus_RUN¿19407673'8/type¿CEDULA/serial¿109746456/mrz¿109746456296051872605188
    #httpsÑ--portal.sidiv.registrocivil.cl-docstatus_RUN¿19407673'8/type¿CEDULA/serial¿109746456/mrz¿109746456296051872605188
    print("codigo que llego: ",linea)
#    linea = linea.rstrip()
    linea = linea.replace("]","|")
    linea = linea.replace("'","-")
#    print(type(linea[0]))
    print("linea 0 a 4 char ",linea[0:4])
    if (len(linea.split("RUN")) == 2):
        #leyó carné nuevo
        linea = linea.split("RUN")[1].split("/")[0].split("-")[0][1:]
        return linea
    elif (len(linea) == 8):
        #leyó algo de 8 digitos, veamos si es el del nacho
        if linea == "16832974":
            return linea
        else:
            return "error"
    else:
        return "error"  
    


class App:
    def __init__(self, window, resultado_queue:Queue, resultado_event: Event,resultado_scanner:Queue,resultado_scanner_event:Event):
        print("iniciando UI")
        self.window = window
        self.font = Font(family="Arial",size=40)
        #self.window.overrideredirect(True)
        self.window.wm_attributes("-fullscreen","true")
        self.resultado_evento = resultado_event
        self.resultado_queue = resultado_queue
        self.resultado_scanner= resultado_scanner
        self.resultado_scanner_event = resultado_scanner_event
        self.fontStyle = Font(family="Arial", size=18)
        # Create a canvas that can fit the above video source size
        self.imagen=PhotoImage(file="logo-sit-blanco.png")
        self.label = tkinter.Label(window,compound=tkinter.CENTER,bg="black")
        self.lector = tkinter.Text(window, width = 1,height=1,fg="black",bg="black")
        self.lector.bind('<Return>', self.callback)
        self.label.pack()
        self.lector.pack()
        self.lector.focus_set()
        #self.lector.lift(self.window)
        self.code=""
        #self.lector.pack_forget()
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 300
        self.num=0
        self.update()
        self.delay_codigo = 5000
        #self.window
        self.window.mainloop()
    
    def callback(self,event):
        self.code=self.lector.get("1.0","end-1c")
        print("Lectura del scanner: ",self.code)
        self.resultado_scanner.put_nowait(self.code)
        self.resultado_scanner_event.set()
        self.code=""
        self.lector.delete("1.0","end-1c")
        time.sleep(0.1)
        self.delay_codigo = 0

    def update(self):
        try:
            #print("update")
            hora = time.strftime("%H:%M")
            self.delay_codigo = 5000
            self.lector.pack_forget()
            if self.resultado_evento.is_set():
                res = self.resultado_queue.get()
                self.resultado_evento.clear()
                if res == "pedir":
                    self.lector.pack(fill=tkinter.BOTH,expand=True,)
                    #print("está en el while del la gui")
                    #self.label.pack_forget()
                    #self.lector.configure(state=tkinter.NORMAL)
                    self.lector.focus_set()
                    txt = "\n\n\n\n\n\n\n\n\n\n\n"+hora
                    self.imagen=PhotoImage(file="ponga-carnet.png")
                    self.label.configure(image=self.imagen,text=txt,fg="white",font=self.font)
                    self.label.image=self.imagen
                    #while(not self.resultado_scanner_event.is_set() and timeFinal>time.time()):
                     #   time.sleep(0.3)
                      #  print("entro al final")
                    self.window.after(self.delay_codigo,self.update)
                else:
                    archivo = "logo-sit-rojo.png" if res == "No registrado" else "logo-sit-verde.png"
                    self.imagen=PhotoImage(file=archivo)
                    self.label.configure(image=self.imagen,text="\n\n\n\n\n\n\n\n\n\n\n"+hora,fg="white",font=self.font)
                    self.label.image=self.imagen
                    tiempo = 4500 if res == "No registrado" else 4500 
                    self.window.after(tiempo,self.update)
            else:
                txt = "\n\n\n\n\n\n\n\n\n\n\n"+hora
                self.imagen=PhotoImage(file="logo-sit-blanco.png")
                self.label.configure(image=self.imagen,text=txt,fg="white",font=self.font)
                self.label.image=self.imagen
                #time.sleep(0.3)
                self.window.after(self.delay,self.update)
        except Empty:
            pass



def main():
    detector,data,vs= cargarModelo()
    #detectar(detector,data,vs)
    resultado_queue = Queue()
    resultado_scanner = Queue()
    resultado_scanner_event = Event()
    resultado_event= Event()

    stop_event= Event()
    
#    App(tkinter.Tk(), resultado_queue,pausa_event,cargando_event)


    try:
        #Hilo de ejecuíón que se encarga del procesamiento
        Thread(name="hilo2",target=detectar, args=[detector,data,vs,resultado_queue,resultado_event,stop_event,resultado_scanner,resultado_scanner_event]).start()
        #Hilo principal del codigo, se encarga de la UI, Tkinter no funciona bien en otro hilo que no sea el principal 
        App(tkinter.Tk(), resultado_queue,resultado_event,resultado_scanner,resultado_scanner_event)
    finally:
        print("APRETANDO STOP")
        #si se cierra la ui se gatilla el evento Stop, el que también detiene el procesamiento
        stop_event.set()


if __name__ == "__main__":
    main()
