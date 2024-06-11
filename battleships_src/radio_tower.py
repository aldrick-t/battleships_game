from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

scoreboard = {
    "player1_hits": 0,
    "player1_misses": 0,
    "player2_hits": 0,
    "player2_misses": 0
}

@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "scoreboard": scoreboard})

@app.get("/update_scoreboard")
async def update_scoreboard(player1_hits: int, player1_misses: int, player2_hits: int, player2_misses: int):
    global scoreboard
    scoreboard = {
        "player1_hits": player1_hits,
        "player1_misses": player1_misses,
        "player2_hits": player2_hits,
        "player2_misses": player2_misses
    }
    return {"message": "Scoreboard updated"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")