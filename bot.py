from google import genai
from google.genai import types

# ⚠️ کلید جدید خود را اینجا وارد کنید
API_KEY = "AQ.Ab8RN6KNcpLEzX1iThuvuyhHfcMO7zQsEHoe5EFTrxas3TQ26g"

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works in a few words",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant."
    )
)

print(response.text)
