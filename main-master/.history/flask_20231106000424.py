from flask import Flask, request, jsonify
from flask_cors import CORS
import vertexai
from vertexai.language_models import TextGenerationModel
import requests

app = Flask(__name__ if __name__ != "__main__" else "your_module_name")