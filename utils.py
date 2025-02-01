import requests
from os import environ as env 
import google.generativeai as genai
import pvfalcon
import tempfile
import subprocess

genai.configure(api_key=env["GOOGLE_API_KEY"])
model = genai.GenerativeModel("models/gemini-1.5-flash")

def get_transcriptions(audio_pth) -> str:

    if audio_pth is not None:
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
                    # "language": "en",
                },
            )

        if response.status_code == 200:
            text_dict = response.json()
            return str(text_dict["text"])
        else:
            print(f"Error: {response.status_code}", response.text)
            return None
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


def crop_audio(input_file_path: str, start_time: float, end_time: float) -> str:
 
    try:
        output_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        output_path = output_file.name
        output_file.close()

        duration = end_time - start_time
        
        command = [
            'ffmpeg',
            '-i', input_file_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-acodec', 'pcm_s16le',  # Use PCM format for better compatibility
            '-ar', '16000',  # Set sample rate to 16kHz
            '-ac', '1',      # Convert to mono
            '-y',            # Overwrite output file if it exists
            output_path
        ]
        
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if process.returncode != 0:
            print(f"FFmpeg error: {process.stderr.decode()}")
            return None
            
        return output_path
        
    except Exception as e:
        print(f"Error cropping audio: {str(e)}")
        return None


def get_multi_speaker_transcriptions(audio_pth: str):

    speakers_transcription = []
    speaker_list = get_diarization(audio_pth)

    print(speaker_list)

    for speaker in speaker_list:

        speaker_audio_pth = crop_audio(audio_pth, speaker["start_time"], speaker["end_time"])

        speaker_text = get_transcriptions(speaker_audio_pth)

        speaker_data = {"speaker": speaker["speaker"], "text": speaker_text, "start_time": speaker["start_time"], "end_time": speaker["end_time"]}

        speakers_transcription.append(speaker_data)

        print(speaker_data)

    return speakers_transcription


def get_diarization(audio_pth: str):
    speaker_list = []

    try:
        falcon = pvfalcon.create(access_key=env["FALCON_KEY"])

        segments = falcon.process_file(audio_pth)

        for segment in segments:
            temp = {"speaker": segment.speaker_tag, "start_time": float(segment.start_sec), "end_time": float(segment.end_sec)}

            speaker_list.append(temp)

        falcon.delete()

    except pvfalcon.FalconError as e:
        print(f"Error: {e}")
    
    return speaker_list