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
        input_text = f"""input:My Blood Report values of "White Blood Cell" is {sysargs_values['WBC']},
        "Red Blood Cell" is {sysargs_values['RBC']},"Hemoglobin" is {sysargs_values['HGB']},
        "Hematocrit"is {sysargs_values['HCT']},"MCV"is {sysargs_values['MCV']},
        "MCH" is {sysargs_values['MCH']},"MCHC" is {sysargs_values['MCHC']},
        "Platelet" is {sysargs_values['PLT']},"Neutrophils" is {sysargs_values['NE']},
        "Lymphocytes" is {sysargs_values['LY']},"Monocytes" is {sysargs_values['MO']},
        "Eosinophils" is {sysargs_values['EO']} give me a brief diagnosis"""

        # Generate the response
        response = model.predict(input_text, **parameters)
        print(response.text)

        current_date_time = datetime.now().strftime("%Y%m%d%H%M%S")

        

        
         



        return jsonify({"message": response.text}), 201

    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=7000)








        
