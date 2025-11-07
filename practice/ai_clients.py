from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def get_ai_model(prefer="openai"):

    if prefer == "openai":
        try:
            return ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        except Exception:
            pass

    # fallback
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
