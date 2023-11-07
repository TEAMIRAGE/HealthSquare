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

def classify_tumor_image(image_path):
    # Define the labels
    labels = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']

    # Load the model
    loaded_model = load_model("tumor_classification_model.h5")

    # Load and preprocess the tumor image
    tumor_image = cv2.imread(image_path)
    tumor_image = cv2.resize(tumor_image, (150, 150))
    tumor_image = np.expand_dims(tumor_image, axis=0)

    # Make predictions on the tumor image
    predictions = loaded_model.predict(tumor_image)
    predicted_class_index = np.argmax(predictions)
    predicted_class = labels[predicted_class_index]

    return predicted_class

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

    # Check if the average values are between 30 and 62
    if all(29 <= average <= 40 for average in channel_averages):
        return True
    else:
        return False

@app.route("/tumor-Processing-result/<img_name>", methods=['GET'])
def tumour_process(img_name):
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
        



        if is_radiograph(image_path):
            # Classify the tumor image
            predicted_class = classify_tumor_image(image_path)

            if os.path.exists(destination_file_name):
                os.remove(destination_file_name)
                print(f"File {destination_file_name} has been deleted.")
            else:
                print(f"The file {destination_file_name} does not exist.")

            print("Predicted class:", predicted_class)
            return jsonify({"message": predicted_class}), 201
        else:
            print("Wrong image")

            if os.path.exists(destination_file_name):
                os.remove(destination_file_name)
                print(f"File {destination_file_name} has been deleted.")
            else:
                print(f"The file {destination_file_name} does not exist.")

            return jsonify({"message": "Wrong Image"}), 201
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500




if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=6000)





        
        
        
