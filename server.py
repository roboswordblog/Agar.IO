# This is what you should run. DO NOT GIVE THIS TO THE PLAYERS SO THAT THEY DONT HACK THE GAME AND MAKE EVERYONE TELEPORT EVERYWHERE.
import socket
import threading
import json
import time




HOST = "0.0.0.0"
PORT = 5555




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()




print("Server started...")




players = {}
connections = {}
lock = threading.Lock()


def handle_client(conn):
  player_id = None
  print("Client connected")




  try:
      while True:
          data = conn.recv(1024)
          if not data:
              break
          try:
              msg = json.loads(data.decode())
          except:
              continue

          pid = msg.get("playerid")
          if not pid:
              continue
            
          player_id = str(pid)

          with lock:
              # create ONLY ONCE
              if player_id not in players:
                  players[player_id] = {
                      "x": 400,
                      "y": 300,
                      "size": 50,
                      "color": (0,0,0)
                  }


              # STRICT update (no fallback spam)
              if "actualX" in msg and "actualY" in msg:
                  players[player_id]["x"] = msg["actualX"]
                  players[player_id]["y"] = msg["actualY"]
                  players[player_id]["size"] = msg["size"]
                  players[player_id]["color"] = msg["color"]


              connections[player_id] = conn




  except Exception as e:
      print("Client error:", e)
  print(f"Disconnected: {player_id}")

  with lock:
      if player_id:
          players.pop(player_id, None)
          connections.pop(player_id, None)

  conn.close()

def broadcast_loop():
  while True:
      with lock:
          try:
              data = json.dumps(players) + "\n"
          except:
              continue

          dead = []

          for pid, conn in connections.items():
              try:
                  conn.send(data.encode())
              except:
                  dead.append(pid)

          for pid in dead:
              connections.pop(pid, None)
              players.pop(pid, None)


      time.sleep(1 / 30)

threading.Thread(target=broadcast_loop, daemon=True).start()
while True:
  conn, addr = server.accept()
  threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
