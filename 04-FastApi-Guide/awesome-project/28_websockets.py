"""28 - WebSockets: real-time chat rooms over one connection.

A WebSocket is one long-lived connection instead of one HTTP request per
message — the server can push to the client whenever something happens.
This example is a small chat: join a room, send a message, everyone in
the room sees it.

Run:   fastapi dev 28_websockets.py     -> http://127.0.0.1:8000/
Try:   open http://127.0.0.1:8000/ in two browser tabs and chat with
       yourself, or:  wscat -c ws://127.0.0.1:8000/ws/general
Test:  see the TestClient snippet at the bottom of this file.

What you learn here:
  - @app.websocket + WebSocket: accept, receive_text, send_text
  - A ConnectionManager: keep the live sockets per room, broadcast
  - Disconnects are normal: WebSocketDisconnect, always clean up
  - One process only: rooms live in memory, so a second server process
    would not see them — use Redis pub/sub to scale past one process
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="28 - WebSockets")


class ConnectionManager:
    """Live sockets, grouped by room. One instance, in memory."""

    def __init__(self) -> None:
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str) -> None:
        await websocket.accept()
        self.rooms.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room: str) -> None:
        self.rooms[room].remove(websocket)
        if not self.rooms[room]:
            del self.rooms[room]

    async def broadcast(self, message: str, room: str) -> None:
        for socket in self.rooms.get(room, []):
            await socket.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{room}")
async def chat_room(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(f"[{room}] {message}", room)
    except WebSocketDisconnect:
        # A closed tab is not an error — just stop sending to it.
        manager.disconnect(websocket, room)


@app.get("/", response_class=HTMLResponse)
def demo_page() -> str:
    """Tiny demo page: pick a room, type a message, watch it arrive."""
    return """
    <!doctype html><html><body>
    <h1>28 - WebSocket chat</h1>
    <input id="room" value="general">
    <input id="text" placeholder="message">
    <button onclick="send()">Send</button>
    <ul id="log"></ul>
    <script>
      let ws;
      function connect() {
        if (ws) ws.close();
        ws = new WebSocket(`ws://${location.host}/ws/${document.getElementById('room').value}`);
        ws.onmessage = (e) => {
          const li = document.createElement('li');
          li.textContent = e.data;
          document.getElementById('log').appendChild(li);
        };
      }
      document.getElementById('room').addEventListener('change', connect);
      function send() {
        if (ws && ws.readyState === 1) ws.send(document.getElementById('text').value);
      }
      connect();
    </script></body></html>
    """


# Test it without a browser — TestClient speaks WebSocket too:
#   from fastapi.testclient import TestClient
#   client = TestClient(app)
#   with client.websocket_connect("/ws/general") as ws1, \\
#           client.websocket_connect("/ws/general") as ws2:
#       ws1.send_text("hello")
#       assert ws2.receive_text() == "[general] hello"
#   # ws1's message reached ws2: the broadcast works, and both
#   # connections closed cleanly when the `with` blocks ended.
