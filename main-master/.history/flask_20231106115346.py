from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import cv2
import tensorflow
import keras
from keras.models import load_model
import sys
import mimetypes
from google.cloud import storage
from dotenv import dotenv_values
import requests

config = dotenv_values("config.env")

app = Flask(__name__ if __name__ != "__main__" else "your_module_name")
CORS(app)



@app.route("/fracture-Processing-result/<img_name>", methods=['GET'])
def fracture_process(img_name):
    try:
        print("Image get name: ",img_name)
