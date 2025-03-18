from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from google.cloud import firestore
from typing import Annotated
import datetime

app = FastAPI()

# mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/template")

# init firestore client
db = firestore.Client()
votes_collection = db.collection("votes")


@app.get("/")
async def read_root(request: Request):
    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # Fetch all votes from Firestore
    votes = votes_collection.stream()

    # Process vote counts and recent votes
    tabs_count = 0
    spaces_count = 0
    recent_votes = []

    for vote in votes:
        vote_data = vote.to_dict()
        if vote_data.get("team") == "TABS":
            tabs_count += 1
        elif vote_data.get("team") == "SPACES":
            spaces_count += 1

        # Store recent votes (limit to last 10)
        recent_votes.append(vote_data)
    
    recent_votes = sorted(recent_votes, key=lambda v: v.get("time_cast", ""), reverse=True)[:10]

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
    return templates.TemplateResponse("index.html", {
        "request": request,
        "tabs_count": tabs_count,
        "spaces_count": spaces_count,
        "recent_votes": vote_data
    })


@app.post("/")
async def create_vote(team: Annotated[str, Form()]):
    if team not in ["TABS", "SPACES"]:
        raise HTTPException(status_code=400, detail="Invalid vote")

    # ====================================
    # ++++ START CODE HERE ++++
    # ====================================

    # Add the vote to Firestore
    vote_data = {
        "team": team,
        "time_cast": datetime.datetime.utcnow().isoformat()
    }
    votes_collection.add(vote_data)

    return {"detail": "Vote recorded successfully!"}

    # ====================================
    # ++++ STOP CODE ++++
    # ====================================
