import RPi.GPIO as GPIO
import time
from picamera import PiCamera

# Configurar los pines GPIO para los motores
ena_pin = 2  # Pin para controlar la velocidad del motor izquierdo
in1_pin = 3  # Pin de dirección 1 del motor izquierdo
in2_pin = 4  # Pin de dirección 2 del motor izquierdo
enb_pin = 17  # Pin para controlar la velocidad del motor derecho
in3_pin = 27  # Pin de dirección 1 del motor derecho
in4_pin = 22  # Pin de dirección 2 del motor derecho

# Configurar el sensor de distancia (ultrasonico)
trigger_pin = 5  # Pin de disparo del sensor de distancia
echo_pin = 6  # Pin de eco del sensor de distancia

# Configurar la cámara
camera = PiCamera()
camera.resolution = (640, 480)  # Resolución de la cámara

# Configurar los pines GPIO como salida
GPIO.setmode(GPIO.BCM)
GPIO.setup(ena_pin, GPIO.OUT)
GPIO.setup(in1_pin, GPIO.OUT)
GPIO.setup(in2_pin, GPIO.OUT)
GPIO.setup(enb_pin, GPIO.OUT)
GPIO.setup(in3_pin, GPIO.OUT)
GPIO.setup(in4_pin, GPIO.OUT)

# Crear objetos PWM para controlar la velocidad de los motores
ena_pwm = GPIO.PWM(ena_pin, 100)
enb_pwm = GPIO.PWM(enb_pin, 100)

# Funciones de control de los motores
def adelante(velocidad):
    GPIO.output(in1_pin, GPIO.HIGH)
    GPIO.output(in2_pin, GPIO.LOW)
    GPIO.output(in3_pin, GPIO.HIGH)
    GPIO.output(in4_pin, GPIO.LOW)
    ena_pwm.ChangeDutyCycle(velocidad)
    enb_pwm.ChangeDutyCycle(velocidad)
    print("adelante")

def atras(velocidad):
    GPIO.output(in1_pin, GPIO.HIGH)
    GPIO.output(in2_pin, GPIO.LOW)
    GPIO.output(in3_pin, GPIO.HIGH)
    GPIO.output(in4_pin, GPIO.LOW)
    ena_pwm.ChangeDutyCycle(velocidad)
    enb_pwm.ChangeDutyCycle(velocidad)
    print("atras")

def izquierda():
    GPIO.output(in1_pin, GPIO.HIGH)
    GPIO.output(in2_pin, GPIO.LOW)
    GPIO.output(in3_pin, GPIO.LOW)
    GPIO.output(in4_pin, GPIO.HIGH)
    print("izquierda")

def derecha():
    GPIO.output(in1_pin, GPIO.LOW)
    GPIO.output(in2_pin, GPIO.HIGH)
    GPIO.output(in3_pin, GPIO.HIGH)
    GPIO.output(in4_pin, GPIO.LOW)
    print("derecha")

def parar():
    GPIO.output(in1_pin, GPIO.LOW)
    GPIO.output(in2_pin, GPIO.LOW)
    GPIO.output(in3_pin, GPIO.LOW)
    GPIO.output(in4_pin, GPIO.LOW)
    print("parar")

# Configurar los objetos PWM con un ciclo de trabajo del 0% (detener los motores)
ena_pwm.start(0)
enb_pwm.start(0)

# Función para medir la distancia con el sensor ultrasonico
def medir_distancia():
    GPIO.setup(trigger_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)

    GPIO.output(trigger_pin, GPIO.LOW)
    time.sleep(0.1)

    GPIO.output(trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trigger_pin, GPIO.LOW)

    while GPIO.input(echo_pin) == 0:
        start_time = time.time()

    while GPIO.input(echo_pin) == 1:
        end_time = time.time()

    tiempo_total = end_time - start_time
    distancia = tiempo_total * 34300 / 2

    distancia = round(distancia, 2)

    return distancia

try:
    camera.start_preview()

    while True:
        distancia = medir_distancia()
        print(f"Distancia: {distancia} cm")
        adelante(100)
        
        if distancia < 40:
            print("ingreso")
            parar()
            time.sleep(0.5)

            if distancia <= 30:
                derecha()
                time.sleep(0.5)
            else:
                izquierda()
                time.sleep(0.5)
        else:
            adelante(100)  # Velocidad del motor: 50%

        time.sleep(0.1)  # Ajustar la frecuencia de actualización del video

except KeyboardInterrupt:
    GPIO.cleanup()
    camera.stop_preview()
