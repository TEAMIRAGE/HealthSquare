from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import numpy as np
from PIL import Image
import cv2
from keras.models import load_model
from google.cloud import storage
import requests



app = Flask(__name__ if __name__ != "__main__" else "your_module_name")
CORS(app)


def download_blob(bucket_name, source_blob_name, destination_file_name, service_account_file):
    # Instantiate a client using the service account key file
    client = storage.Client.from_service_account_json(service_account_file)

    # Get the bucket containing the object
    bucket = client.get_bucket(bucket_name)

    # Specify the object to be downloaded
    blob = bucket.blob(source_blob_name)

    # Download the object to a file
    blob.download_to_filename(destination_file_name)
    print(f"Downloaded {source_blob_name} to {destination_file_name}.")

def is_radiograph(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Check the number of color channels in the image
    num_channels = image.shape[2]

    # Calculate the average value for each channel
    channel_averages = []
    for channel in range(num_channels):
        channel_average = np.mean(image[:, :, channel])
        channel_averages.append(channel_average)

    # Check if the average values are between 30 and 40
    if all(31 <= average <= 62 for average in channel_averages):
        return True
    else:
        return False

def preprocess_data(img_path, img_size=256):
    img = Image.open(img_path).convert('L')
    img = img.resize((img_size, img_size))
    img = np.array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=-1)
    return img

# Load the saved model from the file
model = load_model('my_model.h5')

# Function to check if the image has a fracture
def has_fracture(image_path):
    if not is_radiograph(image_path):
        return None

    img = preprocess_data(image_path, img_size=256)
    prediction = model.predict(np.array([img]))
    predicted_class = np.argmax(prediction)
    fracture_present = predicted_class == 1
    return fracture_present

@app.route("/fracture-Processing-result/<img_name>", methods=['GET'])
def fracture_process(img_name):
    try:
        print("Image get name: ",img_name)
        bucket_name = 'criticalstrike1'
        source_blob_name = img_name
        destination_file_name = f'save/{source_blob_name}'
        service_account_file = 'pure-silicon-390116-5d3c01f54cc0.json'
        image_path = destination_file_name

        # Call the function to download the object
        download_blob(bucket_name, source_blob_name, destination_file_name, service_account_file)
        print("file saved")
        fracture_result = has_fracture(image_path)

        if os.path.exists(destination_file_name):
            os.remove(destination_file_name)
            print(f"File {destination_file_name} has been deleted.")
        else:
            print(f"The file {destination_file_name} does not exist.")

        if fracture_result is None:
            print("The provided image is not Correct.")
            return jsonify({"The provided image is not Correct."}), 201
        elif fracture_result:
            print("Fracture is present.")
            return jsonify({"Fracture is present."}), 201
        else:
            print("No fracture is detected.")
            return jsonify({"No fracture is detected."}), 201
    except Exception as e:
        print(e)
        return jsonify({ "Error occurred"}), 500




if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8000)





        
        
        
