from flask import Flask, request, jsonify
from flask_cors import CORS
import vertexai
from vertexai.language_models import TextGenerationModel
import requests

app = Flask(__name__ if __name__ != "__main__" else "your_module_name")
CORS(app)

vertexai.init(project = "linear-yen-400506", location = "us-central1")
parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison")

@app.route("")