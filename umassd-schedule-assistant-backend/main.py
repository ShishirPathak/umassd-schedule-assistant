from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not found in environment variables")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

app = FastAPI()

# Allow requests from frontend (adjust origin in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for input validation
class AskRequest(BaseModel):
    question: str
    summarizedTimetableContent: str

class SummaryRequest(BaseModel):
    timetableContent: str


@app.post("/ask")
async def ask_gemini(request: AskRequest):
    try:
        est = pytz.timezone("America/New_York")
        now = datetime.now(est)

        current_day = now.strftime("%A")
        yesterday = (now - timedelta(days=1)).strftime("%A")
        tomorrow = (now + timedelta(days=1)).strftime("%A")

        prompt = f"""
You are a friendly timetable assistant operating in Eastern Time (EST/EDT). 
Current date and time (EST): {now.strftime("%Y-%m-%d %I:%M %p")}
Current day: {current_day}
Yesterday was: {yesterday}
Tomorrow will be: {tomorrow}

You have a narrative-like class schedule (summarized timetable content) for the user. Use this context to respond accurately to the user's questions:

{request.summarizedTimetableContent}

Response Guidelines:
- Be concise and friendly in your responses.
- Use full names for days of the week (e.g., use "Friday" instead of "FR").
- If the user asks about classes on any day, list the classes in the order they are scheduled to occur.
- For questions like "When is my next class?", "What is my next class?", "Where is my next class?", and "When is my next class going to start?", provide the relevant details based on the next scheduled class.
- If a class has ended, state: "This class is no longer in session. The last class was on [Month Day, Year]."
- If no classes are found for a specific day, respond with: "You don't have any classes scheduled for {current_day}."
- Avoid listing sources or specific timestamps like "in 30 minutes".

Question: {request.question}
"""

        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summarize")
async def summarize_timetable(request: SummaryRequest):
    try:
        prompt = f"""
You are an AI assistant tasked with transforming the provided ics file content into a narrative of the user's class schedule.

Imagine you're telling a story about the user's semester. Start with the class name from the SUMMARY field, then introduce the
class title from the DESCRIPTION field. Describe when the class begins, using the DTSTART field (in EST).
Explain how long each class lasts, when the class ends using the UNTIL field in RRULE, how often it meets using FREQ and BYDAY fields.
Mention the location and instructor (from DESCRIPTION).

Ignore any classes that ended before today.

ICS Content:
{request.timetableContent}
"""

        response = model.generate_content(prompt)
        return {"summary": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
