import RPi.GPIO as GPIO
import time
from picamera import PiCamera
from PIL import Image

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
camera = PiCamera()
camera.resolution = (640, 480)

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

# Programa principal
try:
    # Iniciar la cámara
    camera.start_preview()
    time.sleep(2)  # Esperar 2 segundos para que la cámara se estabilice

    while True:
        #adelante()
        # Capturar imagen
        #camera.capture('imagen.jpg')
        #image = Image.open('imagen.jpg')
        #image.show()

        # Medir distancia
        distancia = medir_distancia()
        print("Distancia: %.2f cm" % distancia)

        # Controlar motores según la distancia medida
        if distancia > 10:  # Si la distancia es mayor a 10 cm, avanzar
            adelante()
        else:  # Si la distancia es menor o igual a 10 cm, retroceder
            atras()

        time.sleep(1)

except KeyboardInterrupt:
    detener()
    camera.stop_preview()
    GPIO.cleanup()

