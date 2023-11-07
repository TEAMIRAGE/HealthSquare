from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import vertexai
from vertexai.language_models import TextGenerationModel
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import pymongo
from bson import ObjectId
from google.cloud import storage
import os

app = Flask(__name__ if __name__ != "__main__" else "your_module_name")
CORS(app)

vertexai.init(project="linear-yen-400506", location = "us-central1")