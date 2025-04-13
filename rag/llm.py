from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, RAG_PROMPT_TEMPLATE


def call_groq_llm(question: str, context: str) -> str:
    """Send context + question to Groq and return the answer."""
    client = Groq(api_key=GROQ_API_KEY)

    prompt = RAG_PROMPT_TEMPLATE.format(question=question, context=context)

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=GROQ_MODEL,
    )

    return response.choices[0].message.content.strip()
