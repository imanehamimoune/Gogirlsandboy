from openai import OpenAI

LM_STUDIO_BASE_URL = "LOCALHOST:PORT"  # Replace with the actual base URL of your LM Studio instance
LM_STUDIO_MODEL = "MODEL_NAME"  # Replace with the actual model name you want to use

def chat(messages: list[dict]) -> str:

    client = OpenAI(
        base_url=LM_STUDIO_BASE_URL
    )

    response = client.chat.completions.create(
        model=LM_STUDIO_MODEL,
        messages=messages
    )

    content = response.choices[0].message.content

    if content is None:
        raise RuntimeError("LM Studio returned an empty response.")

    return content
