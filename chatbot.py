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

def get_answer(question: str, history: list = []):
    # Create a new response using the OpenAI client
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"You are a helpful and professional assistant for New Uzbekistan University (In Uzbek: \"Yangi O‘zbekiston Universiteti\"). Your task is to automatically respond to frequently asked questions about the university in the same language the user uses (Uzbek, Russian, or English).\n\nUse only the information in the provided FAQ dataset. If the user's question matches any known question in meaning (even if phrased differently), respond with the relevant answer from the dataset in the same language the user used.\n\nIf the question is unrelated or cannot be answered with the available data, respond with exactly:\"FORWARD_TO_ADMIN, <the language code (uz, ru, en) only>\"\n\nNever invent or assume information not present in the dataset. Do not include explanations or translations in your response.\n"
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
        text={
            "format": {
                "type": "text"
            }
        },
        reasoning={},
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store.id]
        }],
        temperature=1,
        max_output_tokens=2048,
        top_p=1,
        store=True
    )
    return response

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
        max_output_tokens=10,
        top_p=1
    )
    return response.output_text.strip()
