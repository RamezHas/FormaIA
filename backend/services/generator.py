import os
import httpx
from pptx import Presentation
from pptx.util import Inches, Pt
from io import BytesIO
from pptx.dml.color import RGBColor
import json
from pathlib import Path

OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"  

async def generate_course_content(topic: str, level: str = "débutant", model: str = None) -> dict:
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
        "model": model if model else MODEL,
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

async def generate_qcm_content(topic: str, level: str = "débutant", model: str = None) -> dict:
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
        "model": model if model else MODEL,
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

async def generate_presentation_slides(topic: str, level: str = "débutant", model: str = None):
    prompt = f"""
Tu es un assistant qui génère des présentations professionnelles.
Génère une présentation sur le thème : '{topic}'.
Niveau : {level}.
Réponds EXCLUSIVEMENT avec une liste JSON, sans texte supplémentaire, sans introduction, sans bloc de code.
Format attendu :
[
  {{
    \"title\": \"Titre du slide\",
    \"bullets\": [\"Point 1\", \"Point 2\", ...]
  }},
  ...
]
Chaque élément représente un slide. Utilise des titres clairs et des points synthétiques.
"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model if model else MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OPENROUTER_API_URL, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            # Remove code block markers if present
            if content.startswith("```)"):
                content = content.strip().strip("`").split("json")[-1].strip()
            slides = json.loads(content)
            return slides
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        raise

def get_template_path(design_name: str) -> str:
    """Get the path to the PowerPoint template file for the given design"""
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent.parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    template_files = {
        "Minimal": "minimal_template.pptx",  # Changed from .potx to .pptx
        "Corporate": "corporate_template.pptx", 
        "Colorful": "colorful_template.pptx"
    }
    
    template_file = template_files.get(design_name, "minimal_template.pptx")
    template_path = templates_dir / template_file
    
    # If template doesn't exist, return None to use default
    if not template_path.exists():
        return None
    
    return str(template_path)

def generate_presentation_pptx_with_template(slides, design: str = "Minimal") -> bytes:
    """Generate PPTX using a ready-made template file"""
    template_path = get_template_path(design)
    
    print(f"Looking for template: {template_path}")
    print(f"Template exists: {os.path.exists(template_path) if template_path else False}")
    
    if template_path and os.path.exists(template_path):
        # Use the template file
        print(f"Using template file: {template_path}")
        prs = Presentation(template_path)
    else:
        # Fallback to default template
        print("Using default template (no template file found)")
        prs = Presentation()
    
    # Add slides using the template's layout
    for idx, slide_data in enumerate(slides):
        # Use the first layout (usually title and content)
        slide_layout = prs.slide_layouts[1] if len(prs.slide_layouts) > 1 else prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        
        # Set title
        if slide.shapes.title:
            slide.shapes.title.text = slide_data.get('title', f"Slide {idx+1}")
        
        # Set content
        if len(slide.placeholders) > 1:
            tf = slide.placeholders[1].text_frame
            tf.clear()
            for bullet in slide_data.get('bullets', []):
                p = tf.add_paragraph()
                p.text = bullet
    
    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()

def generate_presentation_pptx(slides) -> bytes:
    prs = Presentation()
    from pptx.dml.color import RGBColor
    from pptx.util import Pt
    # For each slide in the list, create a slide
    for idx, slide_data in enumerate(slides):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255) if idx else RGBColor(34, 49, 63)
        # Title
        slide.shapes.title.text = slide_data.get('title', f"Slide {idx+1}")
        slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(36 if idx else 44)
        slide.shapes.title.text_frame.paragraphs[0].font.bold = True
        slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(34, 49, 63) if idx else RGBColor(255, 255, 255)
        # Bullets
        tf = slide.placeholders[1].text_frame
        tf.clear()
        for bullet in slide_data.get('bullets', []):
            p = tf.add_paragraph()
            p.text = bullet
            p.font.size = Pt(22)
            p.font.color.rgb = RGBColor(44, 62, 80) if idx else RGBColor(255, 255, 255)
        # Remove the first empty paragraph
        if tf.paragraphs and not tf.paragraphs[0].text:
            tf._element.remove(tf.paragraphs[0]._p)
    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()

def generate_course_pptx(title: str, outline: str, summary: str, raw_content: str) -> bytes:
    prs = Presentation()
    # --- Title Slide ---
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title or "Titre du cours"
    if slide.placeholders and len(slide.placeholders) > 1:
        slide.placeholders[1].text = summary or "Résumé"
    # Style title slide
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = RGBColor(34, 49, 63)  # dark blue
    slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(44)
    slide.shapes.title.text_frame.paragraphs[0].font.bold = True
    slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    if slide.placeholders and len(slide.placeholders) > 1:
        slide.placeholders[1].text_frame.paragraphs[0].font.size = Pt(28)
        slide.placeholders[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    # --- Outline Slide ---
    outline_slide = prs.slides.add_slide(prs.slide_layouts[1])
    outline_slide.shapes.title.text = "Plan détaillé"
    outline_slide.background.fill.solid()
    outline_slide.background.fill.fore_color.rgb = RGBColor(236, 240, 241)  # light gray
    outline_slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    outline_slide.shapes.title.text_frame.paragraphs[0].font.bold = True
    outline_slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(34, 49, 63)
    outline_slide.placeholders[1].text = outline or ""
    outline_slide.placeholders[1].text_frame.paragraphs[0].font.size = Pt(24)
    outline_slide.placeholders[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(44, 62, 80)

    # --- Summary Slide ---
    summary_slide = prs.slides.add_slide(prs.slide_layouts[1])
    summary_slide.shapes.title.text = "Résumé"
    summary_slide.background.fill.solid()
    summary_slide.background.fill.fore_color.rgb = RGBColor(236, 240, 241)
    summary_slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(36)
    summary_slide.shapes.title.text_frame.paragraphs[0].font.bold = True
    summary_slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(34, 49, 63)
    summary_slide.placeholders[1].text = summary or ""
    summary_slide.placeholders[1].text_frame.paragraphs[0].font.size = Pt(24)
    summary_slide.placeholders[1].text_frame.paragraphs[0].font.color.rgb = RGBColor(44, 62, 80)

    # --- Main Content Slides ---
    # Split raw_content into sections by double newlines or numbered headings
    import re
    sections = re.split(r'\n\s*\n|(?=^\d+\.)', raw_content, flags=re.MULTILINE)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Try to extract a heading (e.g., "1. Introduction")
        heading_match = re.match(r'^(\d+\.\s+.+)', section)
        if heading_match:
            heading = heading_match.group(1)
            content = section[len(heading):].strip()
        else:
            # If no heading, use a generic title
            heading = "Section"
            content = section
        # Create a new slide for this section
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor(255, 255, 255)
        slide.shapes.title.text = heading
        slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(32)
        slide.shapes.title.text_frame.paragraphs[0].font.bold = True
        slide.shapes.title.text_frame.paragraphs[0].font.color.rgb = RGBColor(34, 49, 63)
        # Split content into bullet points if possible
        bullets = [line.strip('-• ') for line in content.split('\n') if line.strip()]
        tf = slide.placeholders[1].text_frame
        tf.clear()
        for bullet in bullets:
            p = tf.add_paragraph()
            p.text = bullet
            p.font.size = Pt(22)
            p.font.color.rgb = RGBColor(44, 62, 80)
        # Remove the first empty paragraph
        if tf.paragraphs and not tf.paragraphs[0].text:
            tf._element.remove(tf.paragraphs[0]._p)
    # Save to bytes
    pptx_io = BytesIO()
    prs.save(pptx_io)
    return pptx_io.getvalue()
