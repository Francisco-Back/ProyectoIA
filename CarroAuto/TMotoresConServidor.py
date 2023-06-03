import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import pygame
from flask import Flask, render_template, Response

# Configuración de los pines GPIO
ENA = 17  # Pin de habilitación del motor A
IN1 = 27  # Pin de control de dirección del motor A
IN2 = 22  # Pin de control de dirección del motor A
ENB = 23  # Pin de habilitación del motor B
IN3 = 24  # Pin de control de dirección del motor B
IN4 = 25  # Pin de control de dirección del motor B

TRIG = 18  # Pin de salida del sensor ultrasónico TRIG
ECHO = 16  # Pin de entrada del sensor ultrasónico ECHO

# Configuración de los pines GPIO como salida o entrada
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Configuración de la cámara
camera = cv2.VideoCapture(0)
camera.set(3, 640)  # Ancho
camera.set(4, 480)  # Alto

# Inicializar Pygame
pygame.init()

# Crear una ventana para mostrar la imagen
ancho = int(camera.get(3))
alto = int(camera.get(4))
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption('Cámara')

# Crear una aplicación Flask
app = Flask(__name__)

# Función para controlar el movimiento hacia adelante
def adelante():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(ENB, GPIO.HIGH)

# Función para controlar el movimiento hacia atrás
def atras():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(ENB, GPIO.HIGH)

# Función para detener el movimiento de los motores
def detener():
    GPIO.output(ENA, GPIO.LOW)
    GPIO.output(ENB, GPIO.LOW)

# Función para medir la distancia con el sensor ultrasónico
def medir_distancia():
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)
    
    inicio = time.time()
    fin = time.time()
    
    while GPIO.input(ECHO) == 0:
        inicio = time.time()
        
    while GPIO.input(ECHO) == 1:
        fin = time.time()
        
    duracion = fin - inicio
    distancia = (duracion * 34300) / 2
    
    return distancia

# Función para girar la imagen en 180 grados
def girar_imagen(image):
    return np.rot90(image, 2)

# Ruta de inicio del servidor
@app.route('/')
def index():
    return render_template('index.html')

# Función de generación de frames
def generar_frames():
    while True:
        # Capturar imagen de la cámara
        ret, frame = camera.read()

        # Girar la imagen en 180 grados
        frame = girar_imagen(frame)

        # Mostrar la imagen en la ventana
        imagen_pygame = pygame.surfarray.make_surface(frame)
        ventana.blit(imagen_pygame, (0, 0))
        pygame.display.flip()

        # Convertir la imagen a formato JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Ruta para transmitir los frames de la cámara
@app.route('/video_feed')
def video_feed():
    return Response(generar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Programa principal
if __name__ == '__main__':
    try:
        # Iniciar la aplicación Flask en un hilo separado
        app.run(host='0.0.0.0', threaded=True)

        while True:
            # Medir distancia
            distancia = medir_distancia()
            print("Distancia: %.2f cm" % distancia)

            # Controlar motores según la distancia medida
            if distancia > 10:  # Si la distancia es mayor a 10 cm, avanzar
                adelante()
            else:  # Si la distancia es menor o igual a 10 cm, retroceder
                atras()

            time.sleep(0.1)

    except KeyboardInterrupt:
        detener()
        camera.release()
        GPIO.cleanup()
        pygame.quit()

