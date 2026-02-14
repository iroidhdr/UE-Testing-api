from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

response = client.chat.completions.create(
    model="llama3:latest",
    messages=[
        {"role": "user", "content": "Hello, simply say 'OK'."}
    ]
)

print(response.choices[0].message.content)
