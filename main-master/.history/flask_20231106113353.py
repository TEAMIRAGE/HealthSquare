from flask import Flask, request, jsonify
from flask_cors import CORS

import requests

app = Flask(__name__ if __name__ != "__main__" else "your_module_name")
CORS(app)


parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison")

@app.route("/fracture-Processing-result/<img_name>", methods=['GET'])
def fracture_process(img_name):
    try:
        print("Image get name: ",img_name)
