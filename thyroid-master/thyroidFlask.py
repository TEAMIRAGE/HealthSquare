from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
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
from google.oauth2 import service_account

app = Flask(__name__ if __name__ != "__main__" else "your_module_name")
CORS(app)
credentials = service_account.Credentials.from_service_account_file('pure-silicon-390116-5d3c01f54cc0.json')
vertexai.init(project="pure-lantern-424212-u7", location="us-central1",credentials=credentials)
parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison")


@app.route("/thyroidReport-manual-Processing-result", methods=['POST'])
def thyroid_report():
    try:
        T3 = request.args.get('thyroidReport_t3')
        T4 = request.args.get('thyroidReport_t4')
        THS = request.args.get('thyroidReport_ths')
        userId = request.args.get('userId')

        # Create the input text with sysargs values
        input_text = f"""input:My Thyroid Report values of "TOTAL TRIIODOTHYRONINE(T3)" is {T3},
        "TOTAL THYROXIN(T4)" is {T4},"THYROID STIMULATING HORMONE(THS)" is {THS} give me the full diagnosis of the report"""

        # Generate the response
        response = model.predict(input_text, **parameters)

        # Print or use the response as needed
        # print(response)

        current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_directory = "save/"

        # Create a PDF document
        pdf_filename = os.path.join(output_directory, current_date_time + "_thyroid_report.pdf")
        document = SimpleDocTemplate(pdf_filename, pagesize=letter)

        # Create a list to hold the elements to be added to the PDF
        elements = []

        # Define paragraph styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = ParagraphStyle(
            'Heading1',
            fontSize=16,
            alignment=1,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            textColor=colors.black,
        )
        normal_style = styles['Normal']

        # Add title
        title = Paragraph("Thyroid Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 24))

        # Get the ObjectId string from command-line arguments
        target_object_id_str = userId
        # Convert the ObjectId string to ObjectId
        target_object_id = ObjectId(target_object_id_str)
        # Replace with your MongoDB Atlas connection string
        connection_string = "mongodb+srv://teammiragencer2024:miragemeansgenjutsu@cluster0.yz9vwrs.mongodb.net/" \
                            "DiagnoScan?retryWrites=true&w=majority"
        # Create a MongoDB client
        client = pymongo.MongoClient(connection_string)
        # Access the desired database
        db = client.get_database("DiagnoScan")
        # Access the desired collection
        collection = db.get_collection("userdetails")

        # Define the query to find the document by ObjectId
        query = {"_id": target_object_id}

        # Retrieve the document with the specified ObjectId
        user_document = collection.find_one(query)
        user_name = str(user_document.get("name"))
        dob = user_document.get("dateOfBirth")
        # Calculate the current date
        current_date = datetime.now().date()

        # Calculate the age
        age = str(current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day)))
        # Get the current date
        current_date = datetime.now().strftime("%B %d, %Y")

        # Add patient information
        patient_info = Paragraph(
            f"<b>Patient:</b> {user_name}<br/>"
            f"<b>AGE:</b> {age}<br/>"
            "<b>Gender:</b> Male<br/>"
            "<b>Date of Report:</b>" + current_date,
            normal_style
        )
        elements.append(patient_info)
        elements.append(Spacer(1, 12))

        # Define blood test results using sys arguments
        thyroid_test_results = [
            ("Test Name", "Result", "Reference Range"),
            ("TOTAL TRIIODOTHYRONINE(T3)", f"{T3}", "80-200 ng/dL"),
            ("TOTAL THYROXIN(T4)", f"{T4}", "0.8-1.8 ng/dL"),
            ("THYROID STIMULATING HORMONE(THS)", f"{THS}", "0.4-4.0 mIU/L"),
        ]

        # Create a table with test results
        data = [thyroid_test_results[0]]
        data.extend([Paragraph(cell, normal_style) for cell in row] for row in thyroid_test_results[1:])
        test_result_table = Table(data, colWidths=[2.5 * inch, 1.5 * inch, 2 * inch])
        test_result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(test_result_table)
        elements.append(Spacer(1, 24))

        #response_text = response.response_text if hasattr(response, "response_text") else str(response)

        # Now, create the diagnosis string
        diagnosis = Paragraph(f"Diagnosis: <b>{response.text}</b>", normal_style)
        elements.append(diagnosis)
        elements.append(Spacer(1, 12))

        # Add "generated by medilabs.com" at the bottom corner
        generated_by = Paragraph("Generated by Health<super>2</super>", ParagraphStyle(
            'Normal',
            fontSize=10,
            textColor=colors.grey,
            alignment=2  # Right-aligned
        ))
        elements.append(generated_by)

        # Build the PDF document
        document.build(elements)

        # Specify the path to your service account key JSON file
        key_path = "pure-silicon-390116-5d3c01f54cc0.json"
        # Initialize the Google Cloud Storage client with the service account key
        client = storage.Client().from_service_account_json(key_path)
        # Upload the PDF to a Google Cloud Storage bucket
        bucket_name = "criticalstrike1"
        gcs_object_name = f"{current_date_time}_ThyroidReport.pdf"  # Updated object name format
        # Initialize a GCS client
        # Get the bucket
        bucket = client.get_bucket(bucket_name)
        # Upload the file to GCS
        blob = bucket.blob(gcs_object_name)
        blob.upload_from_filename(pdf_filename)  # Use the correct PDF filename

        print(gcs_object_name.replace(" ", ""))

        # Define the new collection name
        new_collection_name = "thyroidreportcollections"
        user_object_id = ObjectId(target_object_id_str)
        # Access the new collection (or create it if it doesn't exist)
        new_collection = db.get_collection(new_collection_name)
        current_date = datetime.now()
        # Define three sample documents
        document1 = {
            "date": current_date,
            "Imagename": gcs_object_name,
            "UserId": user_object_id
        }

        # Insert the document into the new collection
        new_collection.insert_one(document1)
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
            print(f"File {pdf_filename} has been deleted.")
        else:
            print(f"The file {pdf_filename} does not exist.")
        return jsonify({"message": gcs_object_name}), 201
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.route('/')
def home():
    return "Welcome to the Home Page!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)