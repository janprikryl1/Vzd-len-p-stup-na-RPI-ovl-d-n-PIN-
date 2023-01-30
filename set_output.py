from sys import argv
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD


if __name__ == "__main__":
    pins = argv[1:4]
    output = argv[4:7]

    GPIO.cleanup()  # Vymazání minulé konfigurace

    # Nastavení pinů jako výstupní
    for i in range(len(pins)):
        GPIO.setup(int(pins[i]), GPIO.OUT)
        GPIO.output(int(pins[i]), int(output[i]))
