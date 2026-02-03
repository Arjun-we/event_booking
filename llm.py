from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

# Initialize client
client = genai.Client(api_key=API_KEY)

def generate_answer(user_query, retrieved_docs):
    context = "\n".join([
        f"- {v['name']} ({v['category']}): {v['description']} | Cost ₹{v['cost']} | Capacity {v['capacity']}"
        for v in retrieved_docs
    ])

    prompt = f"""
You are EventBot, an event planning assistant.

RULES (IMPORTANT):
- Do NOT assume budget or guest count.
- If budget or guests are missing, ask ONE short follow-up question.
- Keep answers under 120 words.
- Do NOT add introductions or marketing text.
- Use simple bullet points only.
- Be precise and relevant.

AVAILABLE VENDOR DATA:
{context}

USER QUESTION:
{user_query}

RESPONSE FORMAT (STRICT):
- If information is missing:
  Ask a single clear question.
- Else:
  Event Type:
  Guests:
  Budget:
  Recommended Vendors:
    - Venue:
    - Catering:
    - Decoration:
    - Photography:
"""


    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    return response.text
