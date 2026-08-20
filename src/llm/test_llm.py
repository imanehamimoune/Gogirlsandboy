from openai import OpenAI

LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "deepseek/deepseek-r1-0528-qwen3-8b"

def chat(messages: list[dict]) -> str:
    client = OpenAI(
        base_url=LM_STUDIO_BASE_URL,
        api_key="lm-studio",
    )

    response = client.chat.completions.create(
        model=LM_STUDIO_MODEL,
        messages=messages,
    )

    content = response.choices[0].message.content

    if content is None:
        raise RuntimeError("LM Studio returned an empty response.")

    return content.strip()


if __name__ == "__main__":
    response = chat([
        {"role": "user", "content": "Reply with exactly: CONNECTION SUCCESSFUL"}
    ])

    print("Local LLM response:")
    print(response)