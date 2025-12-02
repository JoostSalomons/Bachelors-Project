from openai import OpenAI
import os
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")

client = OpenAI(api_key=API_KEY)

response = client.responses.create(
    model="gpt-4o-mini",
    input="Houd je van roblox? Houd in jouw antwoord er rekening mee dat je praat tegen een kind van 7 tot 10 jaar oud")

print(response.output_text)