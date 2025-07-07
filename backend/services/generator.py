import os
import httpx

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"  

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

import json

async def generate_qcm_content(topic: str, level: str = "débutant") -> dict:
    prompt = f"""
Tu es un générateur de QCM. Génère exactement 5 questions à choix multiples sur le thème : "{topic}".
Niveau : {level}.
Structure la réponse exclusivement comme une liste JSON **valide**, sans aucun texte supplémentaire, sans introduction, sans code block.

Format attendu :
[
  {{
    "question": "Quel est ... ?",
    "choices": ["A. ...", "B. ...", "C. ...", "D. ..."],
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

        # Remove code blocks if present (e.g., ```json ... ```)
        if content.startswith("```"):
            content = content.strip().strip("`").split("json")[-1].strip()

        # Try parsing the JSON content
        try:
            parsed_qcm = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur de parsing JSON: {e}\nContenu reçu:\n{content}")

        # Optional: return as string if you want to parse later in Streamlit
        # return {"qcm": json.dumps(parsed_qcm)}

        # Return directly as parsed object (recommended)
        return {"qcm": parsed_qcm}
