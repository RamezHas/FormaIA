import openai

# Use the OpenAI-compatible client
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def test_openrouter():
    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "user", "content": "Say hello!"}
            ]
        )

        print("✅ OpenRouter working:")
        print(response.choices[0].message.content)

    except Exception as e:
        print("❌ OpenRouter error:", str(e))


if __name__ == "__main__":
    test_openrouter()
