from fastapi import APIRouter, HTTPException
from backend.models.course_models import CourseRequest, CourseResponse
from backend.services.generator import generate_course_content, generate_qcm_content

router = APIRouter()

@router.post("/generate-course", response_model=CourseResponse)
async def generate_course(request: CourseRequest):
    try:
        ai_response = await generate_course_content(request.topic, request.level)
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
    return await generate_qcm_content(request.topic, request.level)
