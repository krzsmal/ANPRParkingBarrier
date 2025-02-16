from ultralytics import YOLO
from time import sleep
import logging
import cv2
import os
from utils.helper import database_init, read_license_plate, lcd_message, is_beam_connected, handle_leds, read_rfid_with_timeout, control_barrier, blink_leds
import multiprocessing
from collections import deque

os.nice(-20)

license_plate_detector = YOLO('ncnn_model')

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

logging.getLogger('ultralytics').setLevel(logging.ERROR)
logger = logging.getLogger("Barrier_Logger")
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logger.addHandler(handler)

db_connection, db_cursor = database_init()

# Controls barrier access based on entry type (entry/exit)
def handle_barrier_access(entry_type, lcd_line1, lcd_line2, license_plate_number):
    if not is_beam_connected():
        lcd_message("BLAD CZYJNIKA:", "ZAKRYTY")
        timeout_counter = 0
        while (not is_beam_connected()):
            sleep(0.1)
            timeout_counter += 1
            if timeout_counter == 300:
                return
            elif timeout_counter % 10 == 0:
                remaining_time = 30 - int(timeout_counter / 10)
                if remaining_time >= 10:
                    lcd_message("BLAD CZYJNIKA:", f"ZAKRYTY     {remaining_time} S")
                else:
                    lcd_message("BLAD CZYJNIKA:", f"ZAKRYTY      {remaining_time} S")

        lcd_message(lcd_line1, lcd_line2)

    blink_process = multiprocessing.Process(target=blink_leds, args=(4, False, False,))
    blink_process.start()
    control_barrier(True)
    time_elapsed = 0
    while (is_beam_connected()):
        sleep(0.1)
        time_elapsed += 1
        if entry_type == 1 and time_elapsed >= 300:
            lcd_message("      STOP", "")
            blink_process = multiprocessing.Process(target=blink_leds, args=(4, True, True,))
            blink_process.start()
            control_barrier(False)
            blink_process.join()
            return
    while (not is_beam_connected()):
        sleep(0.1)
    blink_process.join()
    db_cursor.execute('INSERT INTO przejazdy (nr_rejestracyjny, wjazd) VALUES (?, ?)',
                      (license_plate_number, entry_type))
    db_connection.commit()
    lcd_message("      STOP", "")
    blink_process = multiprocessing.Process(target=blink_leds, args=(4, True, True,))
    blink_process.start()
    control_barrier(False)
    blink_process.join()


# Handles vehicle exit, calculates fee, and processes payment.
def process_exit(license_plate_number):
    db_cursor.execute("SELECT strftime('%s', (datetime('now', 'localtime'))) - strftime('%s', data) AS time_difference FROM przejazdy WHERE nr_rejestracyjny = ? ORDER BY data DESC LIMIT 1", (license_plate_number,))
    time_spent = (db_cursor.fetchone())[0]
    fee = 0.5 * float(time_spent)

    db_cursor.execute('SELECT nr_karty FROM rejestracje_karty WHERE nr_rejestracyjny = ?', (license_plate_number,))
    card_number = db_cursor.fetchone()
    if card_number is not None:
        card_number = int(card_number[0])
    if card_number is None:
        lcd_message(f"KWOTA: {fee} ZL", "PRZYLOZ KARTE")
        card_number = read_rfid_with_timeout(15)
        if card_number is None:
            lcd_message("TRANSAKCJA", "NIEUDANA")
            sleep(3)
            return

    db_cursor.execute("SELECT saldo FROM bank WHERE nr_karty = ?", (str(card_number),))
    balance = db_cursor.fetchone()
    if balance is not None:
        balance = float(balance[0])
    else:
        lcd_message("TRANSAKCJA", "NIEUDANA")
        sleep(3)
        return

    if balance < fee:
        lcd_message("BRAK", "SRODKOW")
        sleep(3)
        return

    db_cursor.execute("UPDATE bank SET saldo=saldo-? WHERE nr_karty = ?", (fee, str(card_number),))
    db_connection.commit()

    lcd_line1 = "ZAPLACONO:"
    lcd_line2 = (str(fee) + " ZL")
    lcd_message(lcd_line1, lcd_line2)
    handle_barrier_access(0, lcd_line1, lcd_line2, license_plate_number)


# Processes a detected vehicle, determining whether it's entering or exiting.
def handle_vehicle(license_plate_number):
    lcd_message("REJESTRACJA:", license_plate_number)

    for _ in range(2):
        handle_leds(False, False)
        sleep(0.4)
        handle_leds(True, True)
        sleep(0.4)

    db_cursor.execute('SELECT wjazd FROM przejazdy WHERE nr_rejestracyjny = ? ORDER BY data DESC LIMIT 1',
                      (license_plate_number,))
    last_entry = db_cursor.fetchone()
    if last_entry is not None:
        last_entry = int(last_entry[0])
    if last_entry is None or last_entry == 0:
        handle_barrier_access(1, "REJESTRACJA:", license_plate_number, license_plate_number)
    else:
        process_exit(license_plate_number)

    lcd_message("      STOP", "")


# Main loop that captures frames, detects plates, and processes vehicles.
def main():

    frame_available = True
    detections = deque(maxlen=3)
    stable_plate_detected = False
    plate_coordinates = deque(maxlen=10)

    try:
        while frame_available:
            frame_available, frame = camera.read()
            frame = cv2.flip(frame, -1)

            if not frame_available or frame is None or frame.size == 0:
                logger.error("No video source.")
                break

            resized_frame = cv2.resize(frame, (640, 360))
            # cv2.imshow('Camera', resized_frame)

            license_plates = license_plate_detector(resized_frame)[0]

            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate

                if score > 0.6:
                    plate_coordinates.append([x1, y1, x2, y2])

                    x = 10
                    max_dif = 10.0
                    if len(plate_coordinates) == x:
                        for index, row in enumerate(list(plate_coordinates)[:-1]):
                            if (abs(row[0] - plate_coordinates[x - 1][0]) <= max_dif and
                                    abs(row[1] - plate_coordinates[x - 1][1]) <= max_dif and
                                    abs(row[2] - plate_coordinates[x - 1][2]) <= max_dif and
                                    abs(row[3] - plate_coordinates[x - 1][3]) <= max_dif):
                                if index == x - 2:
                                    stable_plate_detected = True
                            else:
                                break

                    if stable_plate_detected:
                        license_plate_crop = resized_frame[int(y1):int(y2), int(x1): int(x2), :]
                        license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                        license_plate_text = read_license_plate(license_plate_crop_gray)
                        # cv2.imshow('Isolated Plate', license_plate_crop_gray)

                        if license_plate_text is not None:
                            detections.append(license_plate_text)
                            # print(f"plate: {license_plate_text}")

                        if len(detections) == 3:
                            best_plate = max(set(detections), key=detections.count)
                            logger.info(f"plate: {best_plate}")
                            detections.clear()

                            handle_vehicle(best_plate)

                        stable_plate_detected = False

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        logger.exception(f"Unhandled exception: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        db_connection.close()


if __name__ == "__main__":
    main()
