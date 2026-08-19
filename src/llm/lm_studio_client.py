from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234"
)

response = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b",
    messages=[
        {"role": "user", "content": "Hello DeepSeek!"}
    ]
)

print(response.choices[0].message.content)
