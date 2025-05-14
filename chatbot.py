from config import Config
from openai import OpenAI

client = OpenAI(
    api_key=Config.OPENAI_API_KEY
)

def create_file(client, file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="assistants"
        )
    return result.id


vector_store = client.vector_stores.create(
    name="knowledge_base"
)

client.vector_stores.files.create(
    vector_store_id=vector_store.id,
    file_id=create_file(client, "faq-newuu.txt"),
)

def get_answer(question: str):
    language = detect_language(question)  # Returns 'uz', 'ru', or 'en'

    system_prompt = f"""You are a helpful and professional assistant for New Uzbekistan University (In Uzbek: "Yangi O‘zbekiston Universiteti").
    Your task is to automatically respond to frequently asked questions about the university in the same language the user uses — Uzbek (uz), Russian (ru), or English (en).

    Use ONLY the information in the provided FAQ dataset. Do not guess or make up answers.

    Do not include formatting with symbols!

    If the question matches any known FAQ (even if phrased differently), respond with the relevant answer from the dataset in the same language the user used.

    Rules:
    - Answer in the language: {language}
    - If the answer is only available in English, translate it into the user’s language before replying.
    - If no relevant answer is found, respond exactly with: "FORWARD_TO_ADMIN, {language}"
    - Do NOT invent, explain, translate, or rephrase anything.
    - Output plain text only — no formatting, explanations, or additional notes.
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": question
                    }
                ]
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store.id]
        }],
        temperature=0,
        max_output_tokens=2048,
        top_p=1,
        store=True
    )
    return response.output_text.strip()

    

def detect_language(text: str) -> str:
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Detect the language of the following text: {text}\n\nReturn the language code (uz, ru, en) only. Do not include any additional text or explanations."
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[],
        temperature=0,
        max_output_tokens=16,
        top_p=1
    )
    return response.output_text.strip()
