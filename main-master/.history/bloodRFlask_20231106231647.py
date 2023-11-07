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
parameters = {
    "max_output_tokens" :1024,
    "temperature" : 0.2,
    "top_p": 0.8,
    "top_k": 40
}

model = TextGenerationModel.from_pretrained("text-bison")




@app.route("/api/manual/UploadData", methods=['POST'])
def blood_report():
    try:
        bloodReport_hemoglobin = request.args.get('bloodReport_hemoglobin')
        bloodReport_rbc = request.args.get('bloodReport_rbc')
        bloodReport_hematocrit = request.args.get('bloodReport_hematocrit')
        bloodReport_wbc = request.args.get('bloodReport_wbc')
        bloodReport_neutrophils = request.args.get('bloodReport_neutrophils')
        bloodReport_lymphocytes = request.args.get('bloodReport_lymphocytes')
        bloodReport_monocytes = request.args.get('bloodReport_monocytes')
        bloodReport_eosinophils = request.args.get('bloodReport_eosinophils')
        bloodReport_platelet = request.args.get('bloodReport_platelet')
        bloodReport_mcv = request.args.get('bloodReport_mcv')
        bloodReport_mch = request.args.get('bloodReport_mch')
        bloodReport_mchc = request.args.get('bloodReport_mchc')
        userId = request.args.get('userId')

        # Create the input text with sysargs values
        input_text = f"""input:My Blood Report values of "White Blood Cell" is {bloodReport_wbc},
        "Red Blood Cell" is {bloodReport_rbc},"Hemoglobin" is {bloodReport_hemoglobin},
        "Hematocrit"is {bloodReport_hematocrit},"MCV"is {bloodReport_mcv},
        "MCH" is {bloodReport_mch},"MCHC" is {bloodReport_mchc},
        "Platelet" is {bloodReport_platelet},"Neutrophils" is {bloodReport_neutrophils},
        "Lymphocytes" is {bloodReport_lymphocytes},"Monocytes" is {bloodReport_monocytes},
        "Eosinophils" is {bloodReport_eosinophils} give me a brief diagnosis"""

        # Generate the response
        response = model.predict(input_text, **parameters)
        print(response.text)

        current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")

        output_directory = "resources/bufferFile/"

        # Create a PDF document
        pdf_filename = os.path.join(output_directory, current_date_time + "_blood_report.pdf")
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
        title = Paragraph("Blood Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 24))

        # Get the ObjectId string from command-line arguments
        target_object_id_str = sys.argv[13]
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
        blood_test_results = [
            ("Test Name", "Result", "Reference Range"),
            ("Hemoglobin", f"{bloodReport_hemoglobin}", "Male: 14 - 16 g%<br/>Female: 12 - 14 g%"),
            ("RBC Count", f"{bloodReport_rbc}", "4.35 - 5.65 Mcl"),
            ("MCV", f"{bloodReport_mcv}", "80 - 99 fl"),
            ("MCH", f"{bloodReport_mch}", "28 - 32 pg"),
            ("MCHC", f"{bloodReport_mchc}", "30 - 40 %"),
            ("WBC Count", f"{bloodReport_wbc}", "4000 - 11000 /cu.mm"),
            ("Neutrophils", f"{bloodReport_neutrophils}", "40 - 75 %"),
            ("Lymphocytes", f"{bloodReport_lymphocytes}", "20 -45 %"),
            ("Eosinophils", f"{bloodReport_eosinophils}", "00 - 06 %"),
            ("Monocytes", f"{bloodReport_monocytes}", "00 - 10 %"),
            ("Platelet Count", f"{bloodReport_platelet}", "150000 - 450000 / cu.mm"),
        ]

        # Create a table with test results
        data = [blood_test_results[0]]
        data.extend([Paragraph(cell, normal_style) for cell in row] for row in blood_test_results[1:])
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

        response_text = response.response_text if hasattr(response, "response_text") else str(response)

        # Now, create the diagnosis string
        diagnosis = Paragraph(f"Diagnosis: <b>{response_text}</b>", normal_style)
        elements.append(diagnosis)
        elements.append(Spacer(1, 12))

        # Add "generated by medilabs.com" at the bottom corner
        generated_by = Paragraph("Generated by Medilabs.com", ParagraphStyle(
            'Normal',
            fontSize=10,
            textColor=colors.grey,
            alignment=2  # Right-aligned
        ))
        elements.append(generated_by)

        # Build the PDF document
        document.build(elements)

        # Upload the PDF to a Google Cloud Storage bucket
        bucket_name = "criticalstrike1"
        gcs_object_name = f"{current_date_time}_BloodReport.pdf"  # Updated object name format
        # Initialize a GCS client
        client = storage.Client()
        # Get the bucket
        bucket = client.get_bucket(bucket_name)
        # Upload the file to GCS
        blob = bucket.blob(gcs_object_name)
        blob.upload_from_filename(pdf_filename)  # Use the correct PDF filename

        print(gcs_object_name.replace(" ", ""))

        # Define the new collection name
        new_collection_name = "bloodreportcollections"
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

        # print(f"Added to MongoDB collection.")



        
         



        return jsonify({"message": response.text}), 201

    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=7000)








        
