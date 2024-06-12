import socket
from flask import Flask, jsonify
import base64
from picamera2 import Picamera2, Preview
from time import sleep
import datetime
import random


app = Flask(__name__)
picam0 = Picamera2(0)

@app.route('/')
def home():
    return 'Hello, this is the Flask server!'

@app.route('/get_image')
def get_image():
    picam0.start_preview(Preview.QTGL)
    picam0.start()
    sleep(1)
    picam0.capture_file("img.png")
    picam0.stop()
    picam0.stop_preview()
    with open('img.png', 'rb') as f:
        image_data = f.read()
    # Convert image data to base64 string
    base64_image = base64.b64encode(image_data).decode('utf-8')

    # Return image data as JSON
    return jsonify({'base64Data': base64_image, 'prediction': "dddd"})

@app.route('/update')
def update():
    # Get current time in the desired format
    current_time = datetime.datetime.now().strftime('%d %b %Y %H:%M')

    # Generate a random number for humidity
    humidity = random.randint(0, 99)

    # Return current time and humidity as JSON
    return jsonify({'time': current_time, 'humidity': humidity})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)
