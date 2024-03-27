import websocket
import json

def send_json_request(ws,request):
    ws.send(json.dumps(request))

def receive_json_response(ws):
    response = ws.recv()
    if resposne:
        return json_loads(response)

ws = websocket.websocket()
ws.connect("wss://gateway.discord.gg/?v=6&encoding=json")
heartbeat_interval = receive_json_response(ws)["d"]["heartbeat_interval"]

token = "dfadfasdfadfadfasdf"

payload = {
    "op": 2,
    "d": {
        "token": token,
        "intents":513,
        "properties":{
            "$os":"linux",
            "$browser": "chrome",
            "device": "pc",
        }
    }
}
send_json_request(ws, payload)

while True:
    event = receive_json_response(ws)
    try:
        content = event['d']['conent']
        author = event['d']['username']
        print(f'{author}:{content}')
    except:
        pass