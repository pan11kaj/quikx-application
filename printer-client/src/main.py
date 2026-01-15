import json,threading
from dotenv import load_dotenv
import os,websockets,asyncio
import cups
from utils import list_printers,get_default_printer,download_file,print_file
load_dotenv()

# job_listener.start()
l_id = os.environ.get("license_id")
password = os.environ.get("license_password")
server_name = os.environ.get("server_name")

class mainThreadHandler:
    def __init__(self, server_name):
        self.server_name = server_name
        self.queue = []
    def download_file_event(self, file_id, file_name):
        data = {
            "file_id":file_id,
            "downloaded":False,
            "file_name":file_name
        }
        self.queue.append(data)
        
        print(app.queue)
        if(download_file(app.server_name,file_name)):
            for item in self.queue:
                if item.get("file_id") == file_id:
                    item["downloaded"] = True
                    print("done for id",file_id)
                    print(self.queue)
                    break

app = mainThreadHandler(server_name=server_name)

print(l_id,password)
async def handler():
    uri = f"ws://127.0.0.1:8000/printers/connection/{l_id}/{password}"
    app.loop = asyncio.get_running_loop()  # store event loop for thread-safe sends
    
    while True:
        try:
            # parameters for the heart beat condition(inside loop because of reconnection)
            async with websockets.connect(uri=uri, ping_interval=20, ping_timeout=10) as ws:
                app.ws = ws  # store current websocket on app
                queue_data = {
                    "event":"queue_update",
                    "data":{"queue":app.queue}
                }
                await ws.send(json.dumps(queue_data))
                print("CONNECTED")
                
                while True:
                    payload = await ws.recv()
                    queue_data = {
                        "event":"queue_update",
                        "data":{"queue":app.queue}
                    }
                    event = json.loads(payload).get("event")
                    data:dict = json.loads(payload).get("data")
                    print(event)
                    match (event):
                        case "file_send":
                            file_id = data.get("file_id")
                            extension = data.get("extension")
                            p = threading.Thread(target=app.download_file_event,args=(file_id,f"{file_id}.{extension}"))
                            p.start()
                        case "print_file":
                            file_id = data.get("file_id") # file id is integer
                            for pending_file in app.queue:
                                if pending_file.get("file_id") == file_id:
                                    queue_data = {
                                        "event":"queue_update",
                                        "data":{"queue":app.queue}
                                    }
                                    await ws.send(json.dumps(queue_data))
                                    files_path = os.environ.get("upload_file_path")
                                    print_thread = threading.Thread(target=print_file,args=(file_id,f"{files_path}{pending_file.get('file_name')}",app,ws),daemon=True)
                                    print_thread.start()
                    await asyncio.sleep(0)
        
        except websockets.ConnectionClosed:
            print("Connection closed, reconnecting in 3 seconds...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Error: {e}, reconnecting in 3 seconds...")
            await asyncio.sleep(3)
    
asyncio.run(handler())
