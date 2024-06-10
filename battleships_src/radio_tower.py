from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

from third_deck import BattleshipGame  # Assuming 'third_deck.py' is your backend file

game = BattleshipGame()

@app.get("/")
async def get():
    html_content = """
    <html>
        <head>
            <title>Battleship</title>
        </head>
        <body>
            <h1>Battleships Game</h1>
            <div id="game">
                <button onclick="connectSerial()">Connect Serial</button>
                <button onclick="connectLan()">Connect LAN</button>
                <button onclick="connectWeb()">Connect Web</button>
                <div id="gameBoard"></div>
            </div>
            <script>
                var ws = new WebSocket("ws://" + location.host + "/ws");
                ws.onmessage = function(event) {
                    var gameElement = document.getElementById("gameBoard");
                    gameElement.innerHTML = event.data;
                };

                function connectSerial() {
                    ws.send(JSON.stringify({action: "connect", type: "serial"}));
                }

                function connectLan() {
                    ws.send(JSON.stringify({action: "connect", type: "lan"}));
                }

                function connectWeb() {
                    ws.send(JSON.stringify({action: "connect", type: "web"}));
                }

                function sendMove(row, col) {
                    ws.send(JSON.stringify({action: "move", row: row, col: col}));
                }

                function placeShip(row, col, size, orientation) {
                    ws.send(JSON.stringify({action: "place", row: row, col: col, size: size, orientation: orientation}));
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message = json.loads(data)
        if message["action"] == "connect":
            if message["type"] == "serial":
                # Implement serial connection
                await websocket.send_text("Serial connection selected.")
            elif message["type"] == "lan":
                # Implement LAN connection
                await websocket.send_text("LAN connection selected. Temporary test message.")
            elif message["type"] == "web":
                # Implement web connection
                await websocket.send_text("Web connection selected.")
        elif message["action"] == "move":
            player = game.get_current_player()
            row = message["row"]
            col = message["col"]
            hit = game.attack(player, row, col)
            game.switch_turn()
            await websocket.send_text(f"Player {player} attacked ({row}, {col}) and it was a {'hit' if hit else 'miss'}.")
        elif message["action"] == "place":
            player = game.get_current_player()
            row = message["row"]
            col = message["col"]
            size = message["size"]
            orientation = message["orientation"]
            success = game.place_ship(player, row, col, size, orientation)
            await websocket.send_text(f"Player {player} {'successfully placed' if success else 'failed to place'} a ship at ({row}, {col}).")
        else:
            await websocket.send_text("Unknown action.")