Parking System Application
--------------------------
This is a Flask-based parking system application that uses computer vision and database integration to log and validate vehicle license plates captured by one or more cameras.

Features
--------
  Real-time video feed from multiple cameras.
  License plate detection and recognition using OpenCV and Tesseract.
  Logging of detected license plates into a SQLite database.
  Validation of entries through a web-based dashboard.
  User authentication for secure access to the dashboard.

System Requirements
-------------------
  Python 3.7 or above
  OpenCV 4.x
  SQLite (built into Python)

Python Libraries
----------------
Install the required Python libraries with:
pip install -r requirements.txt
Here are the main libraries:
    Flask
    OpenCV (opencv-python)
    SQLite (built-in Python module)
    PyTesseract
    NumPy

External Dependencies
---------------------
    pip install Flask opencv-python numpy pytesseract

Installation
------------
git clone https://github.com/Juru-Christopher/avrs.git

Set up your Python environment:
-------------------------------
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Ensure Tesseract OCR is installed and added to your system's PATH.

Usage
-----
    Start the application:
    ----------------------
    python app.py
    The app will run on http://0.0.0.0:4000.
    Open the application in a browser at http://localhost:4000.
    Log in using:
        Username: admin
        Password: 1234


    Me : Chris256
    Rep: https://github.com/Juru-Christopher/avrs.git

Acknowledgements
----------------
    Flask Framework
    OpenCV
    Tesseract OCR
