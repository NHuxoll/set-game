from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from app.game_manager import GameManager

app = FastAPI(title="Set Game API")
gm = GameManager()

# ----------------------
# Request Models
# ----------------------

class JoinRequest(BaseModel):
    name: str

class SubmitRequest(BaseModel):
    player: str
    cards: List[int]
    elapsed_time: float


# ----------------------
# Lobby
# ----------------------

@app.post("/lobby/join", status_code=200)
def join_lobby(req: JoinRequest):
    try:
        gm.join_lobby(req.name)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    return gm.get_state()

@app.post("/lobby/start")
def start_game():
    try:
        gm.start_game()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return gm.get_state()


# ----------------------
# Game
# ----------------------

@app.get("/game/state")
def get_state():
    return gm.get_state()

@app.post("/game/submit")
def submit_set(req: SubmitRequest):
    if gm.state != "running":
        raise HTTPException(status_code=400, detail="Game not running")

    success = gm.submit_set(req.player, req.cards, req.elapsed_time)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid submission")

    winner = gm.try_resolve_round()
    return {
        "success": True,
        "winner": winner,
        "state": gm.get_state()
    }
