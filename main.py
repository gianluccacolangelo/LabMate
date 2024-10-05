from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from correspondentai import CorrespondentAI
from user import User

app = FastAPI()

# Initialize CorrespondentAI with your LLM API key
ai = CorrespondentAI(llm_api_key='your_api_key_here')

class UserCreate(BaseModel):
    name: str
    email: str
    interests: List[str]
    sites_of_interest: List[str]

@app.get("/")
def read_root():
    return {"users": [{"name": user.name, "email": user.email} for user in ai.users]}

@app.post("/users/")
def add_user(user: UserCreate):
    new_user = User(user.name, user.email, user.interests, user.sites_of_interest)
    ai.add_user(new_user)
    return {"message": "User added successfully"}

@app.post("/run_report/")
def run_report():
    result = ai.run_weekly_report()
    return {"message": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)