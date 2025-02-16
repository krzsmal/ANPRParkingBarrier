import re
import serial
import logging
from paddleocr import PaddleOCR
from gpiozero import PWMSoftwareFallback, Button, LED
import warnings
from time import sleep
from utils.LCD import LCD
from utils.SimpleMFRC522 import SimpleMFRC522
import sqlite3

logging.getLogger('ppocr').setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=PWMSoftwareFallback)

det_model_path = "../onnx_pp_ocr/det.onnx"
rec_model_path = "../onnx_pp_ocr/rec.onnx"
cls_model_path = "../onnx_pp_ocr/cls.onnx"

ocr = PaddleOCR(
    use_onnx=True,
    det_model_dir=det_model_path,
    rec_model_dir=rec_model_path,
    cls_model_dir=cls_model_path,
    use_angle_cls=True,
    det_db_thresh=0.5,
    det_db_box_thresh=0.5,
    det_db_unclip_ratio=2.0,
    use_dilation=True,
    lang="en"
)


# Initialize the database and create necessary tables if they do not exist
def database_init():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bank (
        nr_karty TEXT PRIMARY KEY,
        saldo REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS przejazdy (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nr_rejestracyjny TEXT NOT NULL,
        data DATETIME DEFAULT (datetime('now', 'localtime')),
        wjazd INTEGER NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rejestracje_karty (
        nr_rejestracyjny TEXT PRIMARY KEY,
        nr_karty TEXT NOT NULL
    )
    ''')
    return connection, cursor


# Function to check if the IR beam is connected
def is_beam_connected():
    return beam.is_pressed


# Initialize IR beam sensor
beam = Button(21, pull_up=False)
beam.when_pressed = is_beam_connected
beam.when_released = is_beam_connected


# Function to display messages on the LCD screen
def lcd_message(line1, line2):
    lcd.message(line1, 1)
    lcd.message(line2, 2)


# Function to clear the LCD screen
def lcd_clear():
    lcd.clear()


# Initialize LCD display
lcd = LCD(2, 0x27, True)
lcd_message("      STOP", "")


# Initialize LED pins
led1 = LED(13)
led2 = LED(19)
led1.on()
led2.on()


# Function to control the LEDs
def handle_leds(led1_new, led2_new):
    led1.value = led1_new
    led2.value = led2_new


# Function to make LEDs blink alternately
def blink_leds(sec, left_led, right_led):
    for _ in range(sec):
        handle_leds(True, False)
        sleep(0.5)
        handle_leds(False, True)
        sleep(0.5)
    sleep(0.1)
    handle_leds(left_led, right_led)


# Initialize serial communication with Arduino
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=1)


# Function to control the barrier
def control_barrier(open):
    try:
        if open:
            arduino.write("OPEN".encode())
        else:
            arduino.write("CLOSE".encode())
    except Exception as e:
        print("serial error:", e)


# Initialize RFID reader
reader = SimpleMFRC522()


# Function to read RFID card within a given timeout
def read_rfid_with_timeout(timeout=15):
    elapsed_time = 0
    try:
        while elapsed_time <= timeout * 10:
            id = reader.read_id_no_block()
            if id:
                return id
            sleep(0.1)
            elapsed_time += 1
        return None
    except:
        return None


# Function to process and extract text from a license plate image
def read_license_plate(license_plate_crop):
    detections = ocr.ocr(license_plate_crop, det=True, rec=True, cls=True)
    extracted_text = ''

    if not detections or not detections[0]:
        return None

    max_size = 0
    for detection in detections[0]:
        bbox, (_, _) = detection
        width = ((bbox[1][0] - bbox[0][0]) ** 2 + (bbox[1][1] - bbox[0][1]) ** 2) ** 0.5
        height = ((bbox[3][0] - bbox[0][0]) ** 2 + (bbox[3][1] - bbox[0][1]) ** 2) ** 0.5
        size = max(width, height)
        max_size = max(max_size, size)

    detections[0].sort(key=lambda x: x[0][0][0])

    for detection in detections[0]:
        bbox, (text, score) = detection
        text = text.upper().replace(' ', '')
        text = re.sub(r'[^a-zA-Z0-9]', '', text)

        if 'Q' in text:
            return None

        width = ((bbox[1][0] - bbox[0][0]) ** 2 + (bbox[1][1] - bbox[0][1]) ** 2) ** 0.5
        height = ((bbox[3][0] - bbox[0][0]) ** 2 + (bbox[3][1] - bbox[0][1]) ** 2) ** 0.5
        size = max(width, height)

        if score > 0.85 and size >= max_size / 2 and not text[0].isdigit():
            extracted_text += text

    return extracted_text if len(extracted_text) >= 4 else None
