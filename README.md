# ANPR Parking Barrier

## Overview
This project implements an Automatic Number Plate Recognition (ANPR) system integrated with a parking barrier, serving as both an entry and exit gate. Vehicle license plates are detected using a YOLO-based model, and the text is accurately extracted using PaddleOCR. The system automatically calculates parking fees based on the entry and exit times. Payment can be made in two ways: via RFID cards, simulating contactless payment cards, or automatically using a linked payment card based on the license plate number for registered users. The included web application allows clients to view their parking history, link their payment card to a license plate, and check their balance. Administrators have access to parking statistics, an interactive chart of customer activity, and tools for database management. This project is a final assignment for the Embedded Systems course.

## Technologies

<img src="https://img.shields.io/badge/YOLO-111F68?logo=yolo" height="30"> <img src="https://img.shields.io/badge/PaddleOCR-0062B0?logo=paddlepaddle" height="30">
<img src="https://img.shields.io/badge/ONNX-005CED?logo=onnx" height="30">
<img src="https://img.shields.io/badge/NCNN-005CED" height="30">
<img src="https://img.shields.io/badge/Flask-grey?logo=flask" height="30">
<img src="https://img.shields.io/badge/Bootstrap-222629?logo=bootstrap" height="30">
<img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite" height="30">
<img src="https://img.shields.io/badge/Raspberry Pi-A22846?logo=raspberrypi" height="30">
<img src="https://img.shields.io/badge/Arduino-00878F?logo=arduino" height="30">


## Demo Video
[![Watch video](https://github.com/user-attachments/assets/84e7dd66-ff3e-41a2-9949-2de1365909f7)](https://www.youtube.com/watch?v=ajk0i43y1Kg)

## Features
* **Automatic Number Plate Recognition (ANPR):** Uses a YOLO-based model and PaddleOCR to detect and read vehicle license plates.
* **Automated Barrier Control:** Opens and closes the barrier based on vehicle verification.
* **RFID-Based Payment Simulation:** Supports simulated contactless payments for parking fees.
* **Real-Time Fee Calculation:** Determines parking costs based on entry and exit timestamps.
* **Infrared Sensor for Vehicle Detection:** Ensures safe barrier operation by detecting vehicle presence.
* **LCD and LED Indicators:** Displays system messages and visual signals for users.
* **Web-Based Management Dashboard:** Allows customers to track their parking history, manage vehicle registrations, and check balances.
* **Administrator Tools:** Provides parking statistics, interactive activity charts, and database management functionalities.
* **SQLite Database Integration:** Stores vehicle records and user data.
* **Flask-Based Web Application:** Provides a user-friendly interface for both customers and administrators.
* **Bootstrap-Based UI:** Enhances the web interface with responsive design and modern styling.

## Hardware Components
* **Raspberry Pi 5** - Main processing unit.
* **Cytron Maker Uno (compatible with Arduino Uno)** - Microcontroller used for servo control.
* **Servo Motor Feetech FS5103B** - Provides precise and reliable movement for the parking barrier.
* **RFID Module MF RC522** - Used for contactless payment simulation.
* **Infrared Beam Break Sensor** - Detects vehicle presence for barrier control.
* **USB Camera** - Provides real-time video feed and captures images for license plate recognition.
* **LCD Display with I2C Converter LCM1602** - Displays real-time system messages.
* **LED Indicators** – Indicate system status and notifications.
* **Power Supply for Raspberry Pi 5** - Provides necessary power for Raspberry Pi 5.

## Project Images
<table>
  <tr>
    <td colspan="2" align="center">
      <img src="https://github.com/user-attachments/assets/cfe09478-c383-4c6c-8e96-4f3bccdfb5f2" alt="Image 1">
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/def10316-dc85-41a4-b4ef-28c08b9c1e4e" alt="Image 2">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/2687398d-29ef-4b8c-9e2d-56afc091c05f" alt="Image 3">
    </td>
  </tr>
    <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/8e1918c1-3105-46a0-a930-89f95bfebe91" alt="Image 4">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/50d89f35-bce0-48be-a83c-db4215b30841" alt="Image 5">
    </td>
  </tr>
    </tr>
    <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/01136b19-1972-453f-a4b6-9ce487abbfcf" alt="Image 6">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/1a9f3e49-9533-420b-a024-ed457908a6fd" alt="Image 7">
    </td>
  </tr>  </tr>
    <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/39f5b536-f8c3-43d6-bfe6-ce6a73754077" alt="Image 8">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/491bedba-5210-4d06-af0a-3c885d686c4d" alt="Image 9">
    </td>
  </tr>  </tr>
    <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/8095aeda-8c6e-422f-9d77-53dca86ecf17" alt="Image 10">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/1fa6871e-62f2-4f01-94fc-59caaf9d2206" alt="Image 11">
    </td>
  </tr>  </tr>
    <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/3effbf2c-3294-4c62-83b8-0a8bb1429de9" alt="Image 12">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/4e7a5f88-edb1-4762-a1e7-4649fe52a914" alt="Image 13">
    </td>
  </tr>
</table>


## License
This project is licensed under the **[GNU General Public License v3.0](LICENSE)**.