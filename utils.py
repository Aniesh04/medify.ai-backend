import requests
from os import environ as env 
import google.generativeai as genai

genai.configure(api_key=env["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")

def get_transcriptions(audio_pth: str) -> str:

    with open(audio_pth, "rb") as f:
        response = requests.post(
            "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions",
            headers={"Authorization": f'Bearer {env["FW_TOKEN"]}'},
            files={"file": f},
            data={
                "model": "whisper-v3-turbo",
                "temperature": "0",
                "vad_model": "silero",
                "preprocessing": "none",
                "language": "en",
            },
        )

    if response.status_code == 200:
        text_dict = response.json()
        # print(str(text_dict["text"]))
        return str(text_dict["text"])
    else:
        print(f"Error: {response.status_code}", response.text)
        return None
    
    
def get_suggest(user_prompt: str) -> str:

    input = f"""
    You are Medical Domain Expert. The input given to you is the patient query of the audio recorded by a single patient about the symptoms and queries mentioned by the patient. 
    Make a detailed analysis on the symptoms of the patient and suggest a best solution to the patient. 
    **Firstly, understand the age group of the patient which will be generally mentioned in the text transcription and incase if it is not mentioned in the text transcription, suggest the solutions by recommending multiple solutions to all the important age groups. **

    If the issue can be resolved with any physical exercise, or any physical movement suggest that one. Try to suggest the dosage of the recommended medicine as mild as possible. If the symptoms signal a very risky/dangerous signs recommend the user to consult the respective doctor.
    The response to patient should be in the following order:
    1) The possible reasons for the cause(disease/any other health issue).
    2) Recommended solution for the cause.
    3) Recommended medicine. (Suggest medicine that is available in India)
    4) The need of consulting a doctor.


    Based on the above instructions, give medical advice to the following patient query:
    {user_prompt}

    If the patient query is not related to any medical query or medical topic reply:
    "I am a medical chatbot"
    """

    response = model.generate_content(input)

    return str(response.text)