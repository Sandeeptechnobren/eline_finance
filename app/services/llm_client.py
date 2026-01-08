from openai import OpenAI
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.services.llm_prompt import SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def call_llm(user_input: str, session_context: dict):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
User input: {user_input}
Session context: {session_context}
"""
        }
    ]

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0
    )

    return response.choices[0].message.content