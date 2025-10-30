from openai import OpenAI
import google.generativeai as genai
from .config import settings

# --- OpenAI ---
openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- Gemini ---
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")


def ask_openai(messages):
    response = openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def ask_gemini(messages):
    user_text = ""
    for m in messages:
        if m["role"] == "user":
            user_text = m["content"]

    res = gemini_model.generate_content(user_text, stream=True)
    answer = ""
    for chunk in res:
        if chunk.text:
            answer += chunk.text
    return answer
