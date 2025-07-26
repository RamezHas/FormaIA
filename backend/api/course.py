from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from backend.models.course_models import CourseRequest, CourseResponse
from backend.services.generator import generate_course_content, generate_qcm_content, generate_course_pptx, generate_presentation_slides, generate_presentation_pptx, generate_presentation_pptx_with_template

router = APIRouter()

@router.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest):
    try:
        ai_response = await generate_course_content(request.topic, request.level, request.model)
        # Parse AI response (assume response['choices'][0]['message']['content'] contains the text)
        content = ai_response['choices'][0]['message']['content']
        # Simple parsing (to be improved):
        lines = content.split('\n')
        title = lines[0] if lines else ""
        outline = "\n".join(lines[1:3]) if len(lines) > 2 else ""
        summary = "\n".join(lines[3:5]) if len(lines) > 4 else ""
        raw_content = content
        return CourseResponse(title=title, outline=outline, summary=summary, raw_content=raw_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-qcm")
async def generate_qcm(request: CourseRequest):
    return await generate_qcm_content(request.topic, request.level, request.model)

@router.post("/generate-course-pptx")
async def generate_course_pptx_endpoint(request: CourseRequest):
    try:
        ai_response = await generate_course_content(request.topic, request.level, request.model)
        content = ai_response['choices'][0]['message']['content']
        lines = content.split('\n')
        title = lines[0] if lines else ""
        outline = "\n".join(lines[1:3]) if len(lines) > 2 else ""
        summary = "\n".join(lines[3:5]) if len(lines) > 4 else ""
        raw_content = content
        pptx_bytes = generate_course_pptx(title, outline, summary, raw_content)
        pptx_io = BytesIO(pptx_bytes)
        pptx_io.seek(0)
        return StreamingResponse(pptx_io, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", headers={"Content-Disposition": f"attachment; filename=course_{request.topic}.pptx"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-presentation-pptx")
async def generate_presentation_pptx_endpoint(request: CourseRequest):
    try:
        slides = await generate_presentation_slides(request.topic, request.level, request.model)
        # Get design from request, default to "Minimal"
        design = getattr(request, 'design', 'Minimal')
        # Use template-based generation (falls back to design-based if no template file)
        pptx_bytes = generate_presentation_pptx_with_template(slides, design)
        pptx_io = BytesIO(pptx_bytes)
        pptx_io.seek(0)
        return StreamingResponse(
            pptx_io,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            headers={"Content-Disposition": f"attachment; filename=presentation_{request.topic}.pptx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-outline")
async def generate_outline(request: CourseRequest):
    # Prompt the LLM for a detailed outline only, with Introduction and Conclusion
    prompt = f"""
    Génère uniquement un plan détaillé de cours sur le thème suivant : '{request.topic}'.
    Niveau : {request.level}.
    Structure :
    - Le plan commence toujours par une section 'Introduction' et se termine par une section 'Conclusion'.
    - Entre les deux, ajoute 4 à 6 sections principales pertinentes pour le sujet.
    - Chaque section comporte 2 à 4 points clés en bullet points.
    - Utilise le style markdown, sans introduction, sans texte supplémentaire, sans bloc de code.
    Réponds en français.
    """
    try:
        ai_response = await generate_course_content(request.topic, request.level, request.model)
        content = ai_response['choices'][0]['message']['content']
        return {"outline": content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))