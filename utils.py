import requests
from os import environ as env 


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
    