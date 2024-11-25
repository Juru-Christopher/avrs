from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, flash
import cv2
import sqlite3
import numpy as np
from datetime import datetime
import logging
import os
import pytesseract

app = Flask(__name__)
app.secret_key = 'parkingsystem2024'  # Replace with your secret key

# Camera URLs (0 for the first camera detected on your system)
camera_01 = 0  # Adjust if you have more than one camera
camera_02 = 1 

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize the main database
def init_db():
    try:
        with sqlite3.connect('./database/parking_system.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    camera TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS validated_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL
                )
            ''')
            conn.commit()
    except Exception as e:
        logging.error(f"Database initialization error: {e}")

# Database function to fetch logs
def get_vehicle_logs():
    try:
        with sqlite3.connect("./database/parking_system.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT plate, timestamp, camera FROM vehicle_log ORDER BY timestamp DESC LIMIT 10")
            logs = cursor.fetchall()
        return logs
    except Exception as e:
        logging.error(f"Error fetching vehicle logs: {e}")
        return []

# Database function to fetch validated entries
def get_validated_entries():
    try:
        with sqlite3.connect("./database/parking_system.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT plate, timestamp, status FROM validated_entries ORDER BY timestamp DESC LIMIT 10")
            entries = cursor.fetchall()
        return entries
    except Exception as e:
        logging.error(f"Error fetching validated entries: {e}")
        return []

# Function to preprocess the image
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 30, 200)
    return edged

# Function to find the license plate contour
def find_license_plate_contour(edged):
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.018 * peri, True)
        if len(approx) == 4:
            return approx
    return None

# Function to extract the license plate
def extract_license_plate(image, contour):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    new_image = cv2.drawContours(mask, [contour], 0, 255, -1)
    new_image = cv2.bitwise_and(image, image, mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    
    cropped = image[topx:bottomx + 1, topy:bottomy + 1]
    return cropped, (topx, topy, bottomx, bottomy)

# Function to recognize text from the license plate
def recognize_text(image):
    text = pytesseract.image_to_string(image, config='--psm 8')
    return text.strip()

# Function to log detected plates into the database
def log_plate_to_db(plate, camera):
    try:
        with sqlite3.connect('./database/parking_system.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vehicle_log (plate, camera) VALUES (?, ?)", (plate, camera))
            conn.commit()
    except Exception as e:
        logging.error(f"Error logging plate to database: {e}")

# Streaming video feed from the attached camera (OpenCV)
def generate_video_feed(camera):
    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        logging.error(f"Could not open video device ")
        return

    while True:
        success, frame = cap.read()
        if not success:
            logging.error("Failed to capture frame")
            break

        processed_frame = preprocess_image(frame)
        contour = find_license_plate_contour(processed_frame)

        if contour is not None:
            cropped_plate, (topx, topy, bottomx, bottomy) = extract_license_plate(frame, contour)
            plate_text = recognize_text(cropped_plate)

            # Draw rectangle around the detected plate
            cv2.rectangle(frame, (topy, topx), (bottomy, bottomx), (0, 255, 0), 2)
            # Put the detected plate text above the rectangle
            cv2.putText(frame, plate_text, (topy, topx - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Print X and Y coordinates at the bottom of the frame
            cv2.putText(frame, f'X: {topy}, Y: {topx}', (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['userId']
    password = request.form['password']
    
    if user_id == 'admin' and password == '1234':
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials, please try again.')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    logs = get_vehicle_logs()
    validated_entries = get_validated_entries()
    return render_template('index.html', logs=logs, validated_entries=validated_entries)

@app.route('/camera_views')
def camera_views():
    return render_template('cameraViews.html')
    
@app.route('/video_1')
def video_1():
    return Response(generate_video_feed(camera_01), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_2')
def video_2():
    return Response(generate_video_feed(camera_02), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs')
def logs():
    logs = get_vehicle_logs()
    return jsonify(logs)

@app.route('/validated_entries')
def validated_entries():
    entries = get_validated_entries()
    return jsonify(entries)

if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=4000, debug=True)