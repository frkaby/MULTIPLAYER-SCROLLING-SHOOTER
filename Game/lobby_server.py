# lobby_server.py
import socket
from _thread import *
import pickle

server = "localhost"
port = 5556

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(5)
print("Lobby Server Started")

lobbies = []

def handle_client(conn):
    global lobbies
    conn.send(pickle.dumps(lobbies))
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            if not data:
                print("Disconnected")
                break
            action, payload = data
            if action == "ADD":
                lobbies.append({"game": payload, "players": [{"username": payload["username"], "ready": False}], "messages": [], "started": False})
            elif action == "GET":
                conn.sendall(pickle.dumps(lobbies))
            elif action == "JOIN":
                for lobby in lobbies:
                    if lobby["game"]["game_name"] == payload["game_name"]:
                        lobby["players"].append({"username": payload["username"], "ready": False})
            elif action == "LEAVE":
                for lobby in lobbies:
                    if lobby["game"]["game_name"] == payload["game_name"]:
                        lobby["players"] = [player for player in lobby["players"] if player["username"] != payload["username"]]
                        if not lobby["players"]:  # Remove lobby if empty
                            lobbies.remove(lobby)
            elif action == "MESSAGE":
                for lobby in lobbies:
                    if lobby["game"]["game_name"] == payload["game_name"]:
                        lobby["messages"].append(payload["message"])
            elif action == "READY":
                for lobby in lobbies:
                    if lobby["game"]["game_name"] == payload["game_name"]:
                        for player in lobby["players"]:
                            if player["username"] == payload["username"]:
                                player["ready"] = payload["ready"]
            elif action == "START":
                for lobby in lobbies:
                    if lobby["game"]["game_name"] == payload["game_name"]:
                        lobby["started"] = True
                        for player in lobby["players"]:
                            # Oyun başlangıcı mesajını her bir oyuncuya gönder
                            conn.sendall(pickle.dumps(("START_GAME", None)))
            conn.sendall(pickle.dumps(lobbies))
        except:
            break
    print("Lost connection")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    start_new_thread(handle_client, (conn,))
