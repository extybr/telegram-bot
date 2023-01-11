import RPi.GPIO as GPIO


class Led:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.OUT)

    def set_led_on_off(self, level):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(25, GPIO.OUT)
        if level == 1:
            GPIO.output(25, GPIO.HIGH)
        elif level == 0:
            GPIO.output(25, GPIO.LOW)
