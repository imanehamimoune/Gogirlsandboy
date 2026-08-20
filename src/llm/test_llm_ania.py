import json
from openai import OpenAI

LM_STUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "google/gemma-4-12b-qat"  # <-- verify this against /v1/models, see note below


def chat(messages: list[dict]) -> str:
    client = OpenAI(
        base_url=LM_STUDIO_BASE_URL,
        api_key="lm-studio",
    )

    response = client.chat.completions.create(
        model=LM_STUDIO_MODEL,
        messages=messages,
    )

    # Fail loudly with the full response instead of a cryptic TypeError
    if not response.choices:
        raise RuntimeError(
            f"LM Studio returned no choices. Full response:\n"
            f"{json.dumps(response.model_dump(), indent=2)}"
        )

    content = response.choices[0].message.content

    if content is None:
        raise RuntimeError(
            f"LM Studio returned an empty message. Full response:\n"
            f"{json.dumps(response.model_dump(), indent=2)}"
        )

    return content.strip()


if __name__ == "__main__":
    response = chat([
        {"role": "user", "content": "Reply with exactly: CONNECTION SUCCESSFUL"}
    ])

    print("Local LLM response:")
    print(response)