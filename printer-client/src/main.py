import win32api
import subprocess,json,threading
from dotenv import load_dotenv
import os,websockets,asyncio
from utils import list_printers,get_default_printer,download_file,print_file

load_dotenv()

l_id = os.environ.get("license_id")
password = os.environ.get("license_password")
server_name = os.environ.get("server_name")
printer = get_default_printer()
sumatra = r"D:\business logic of windows printer\src\SumatraPDF\SumatraPDF.exe"

#  standard data structure: {event, data}



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

# wensocket connection failed error is occuring it should be fixed

async def handler():
    uri = f"ws://localhost:8000/printers/connection/{l_id}/{password}"
    async with websockets.connect(uri=uri) as ws:
        queue_data = {
                                    "event":"queue_update",
                                   "data":{"queue":app.queue}
                                }
        await ws.send(json.dumps(queue_data))
        while True:
            try:
            
                payload = await ws.recv()
                queue_data = {
                                    "event":"queue_update",
                                    "data":{"queue":app.queue}
                                }
                event = json.loads(payload).get("event")
                data:dict = json.loads(payload).get("data")
                match (event):
                    case "file_send":
                        file_id = data.get("file_id")
                        extension = data.get("extension")
                        p = threading.Thread(target=app.download_file_event,args=(file_id,f"{file_id}.{extension}"))
                        p.start()
                    case "print_file":
                        file_id = data.get("file_id")
                        for pending_file in app.queue:
                            if pending_file.get("file_id") == file_id:
                                queue_data = {
                                    "event":"queue_update",
                                    "queue":app.queue
                                }
                                await ws.send(json.dumps(queue_data))

                                print_thread = threading.Thread(target=print_file,args=(printer,sumatra,f"./uploaded-files/{pending_file.get("file_name")}",ws,app))
                                # print_thread.start()
            except websockets.ConnectionClosed:
                print("connection closed, reconnecting...")
                await asyncio.sleep(3)
            except Exception as e:
                print("Error: ",e)
                await asyncio.sleep(3)
    
asyncio.run(handler())

# print_file(printer,sumatra,"./uploaded-files/blank.pdf")