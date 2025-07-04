from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import course

app = FastAPI(title="FormaIA Backend")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # update this with Streamlit/React URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(course.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FormaIA API!"}
