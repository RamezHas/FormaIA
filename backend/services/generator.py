import os
import httpx

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat-v3-0324"  # Gemini 2.5 Pro Experimental

async def generate_course_content(topic: str, level: str = "débutant") -> dict:
    prompt = f"""
    Génère un cours structuré sur le thème suivant : '{topic}'.
    Niveau : {level}.
    Structure :
    - Titre du cours
    - Plan détaillé
    - Résumé
    - Contenu principal
    Réponds en français.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_API_URL, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        raise

async def generate_qcm_content(topic: str, level: str = "débutant") -> dict:
    prompt = f"""
    Génère 5 questions QCM sur le thème suivant : '{topic}'.
    Niveau : {level}.
    Pour chaque question, propose 4 choix de réponses (A, B, C, D) et indique la bonne réponse.
    Réponds en français et structure la réponse en JSON :
    [
      {{
        "question": "...",
        "choices": ["A ...", "B ...", "C ...", "D ..."],
        "answer": "A"
      }},
      ...
    ]
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return {"qcm": content}
