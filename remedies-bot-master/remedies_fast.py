from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import vertexai
from vertexai.language_models import TextGenerationModel
from google.oauth2 import service_account
from pydantic import BaseModel

app = FastAPI()
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Assuming the credentials setup and Vertex AI initialization is similar to Flask's
credentials = service_account.Credentials.from_service_account_file('pure-silicon-390116-5d3c01f54cc0.json')

vertexai.init(project="linear-yen-400506", location="us-central1", credentials=credentials)
parameters = {
    "max_output_tokens": 1024,
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}
model = TextGenerationModel.from_pretrained("text-bison@001")
class UserInput(BaseModel):
    username: str

@app.post('/remedies_ai')
async def remedies_chatbot(user_input: UserInput):
    try:
        response = model.predict(
            f"""input: i am having a headache
        output: Home remedies for a headache are:
        * **Rest.** If you can, lie down in a dark, quiet room.
        * **Apply a cold compress to your forehead or temples.** This can help to reduce inflammation and pain.
        * **Take a warm bath or shower.** The heat can help to relax your muscles and relieve pain.
        * **Drink plenty of fluids.** Dehydration can worsen headaches.
        * **Eat a healthy diet.** Eating plenty of fruits, vegetables, and whole grains can help to keep your blood sugar levels stable and prevent headaches.
        * **Get regular exercise.** Exercise can help to improve your overall health and well-being, which can help to prevent headaches.
        * **Avoid caffeine, alcohol, and other triggers.** If you know what triggers your headaches, avoid those things as much as possible.
        * **See a doctor if your headaches are severe or frequent.** Your doctor can help you determine the cause of your headaches and recommend treatment options.

        input: headache
        output: Home remedies for a headache are:
        * **Rest.** If you can, lie down in a dark, quiet room.
        * **Apply a cold compress to your forehead or temples.** This can help to reduce inflammation and pain.
        * **Take a warm bath or shower.** The heat can help to relax your muscles and relieve pain.
        * **Drink plenty of fluids.** Dehydration can worsen headaches.
        * **Eat a healthy diet.** Eating plenty of fruits, vegetables, and whole grains can help to keep your blood sugar levels stable and prevent headaches.
        * **Get regular exercise.** Exercise can help to improve your overall health and well-being, which can help to prevent headaches.
        * **Avoid caffeine, alcohol, and other triggers.** If you know what triggers your headaches, avoid those things as much as possible.
        * **See a doctor if your headaches are severe or frequent.** Your doctor can help you determine the cause of your headaches and recommend treatment options.

        input: what can you do if you are experiencing a headache
        output: Home remedies for a headache are:
        * **Rest.** If you can, lie down in a dark, quiet room.
        * **Apply a cold compress to your forehead or temples.** This can help to reduce inflammation and pain.
        * **Take a warm bath or shower.** The heat can help to relax your muscles and relieve pain.
        * **Drink plenty of fluids.** Dehydration can worsen headaches.
        * **Eat a healthy diet.** Eating plenty of fruits, vegetables, and whole grains can help to keep your blood sugar levels stable and prevent headaches.
        * **Get regular exercise.** Exercise can help to improve your overall health and well-being, which can help to prevent headaches.
        * **Avoid caffeine, alcohol, and other triggers.** If you know what triggers your headaches, avoid those things as much as possible.
        * **See a doctor if your headaches are severe or frequent.** Your doctor can help you determine the cause of your headaches and recommend treatment options.

        input: anything other than medical
        output: i don\'t have expertise on this matter.

        input: suggest home remedies for heart attack
        output: * **Call 911.** If you are experiencing symptoms of a heart attack, it is important to call 911 immediately. This will allow you to receive medical attention as soon as possible.

        Home Remedies for a heart attack are not a substitute for medical treatment. If you are experiencing symptoms of a heart attack, Please seek medical attention immediately.

        input: {user_input}
        output:
        """,
            **parameters
        )
        print(f"Response from Model: {response.text}")
        return JSONResponse(content={"message": response.text}, status_code=201)
    except Exception as e:
        print("Error occurred: ", e)
        raise HTTPException(status_code=500, detail="Error occurred")
    
@app.get('/')
async def root():
    return {"message": "Welcome to the Home Page!"}
    