import RPi.GPIO as GPIO


class Led:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.OUT)

    @classmethod
    def set_led_on_off(cls, level: bool) -> None:
        """ Включение/выключение светодиода (реле) """
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(25, GPIO.OUT)
        if level:
            GPIO.output(25, GPIO.HIGH)
        elif not level:
            GPIO.output(25, GPIO.LOW)
