import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def chat(prompt):
    for _ in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash", contents=prompt
            )
            return response.text

        except ServerError:
            print("google servers busy, retrying...")
            time.sleep(2)

    return "sorry, google's servers are overloaded right now."
