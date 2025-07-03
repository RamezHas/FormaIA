import openai
from transformers import pipeline

# Use the OpenAI-compatible client
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def test_huggingface():
    try:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        result = summarizer("This is a long article that needs summarizing.", max_length=30, min_length=10, do_sample=False)
        print("✅ Hugging Face working. Summary:", result[0]['summary_text'])
    except Exception as e:
        print("❌ Hugging Face error:", str(e))

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
    test_huggingface()
