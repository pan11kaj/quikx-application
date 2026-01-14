from fastapi import APIRouter,HTTPException,UploadFile,File,Form,WebSocket,WebSocketException,WebSocketDisconnect
from typing import Annotated
from fastapi.responses import HTMLResponse
import os
from typing import Dict
from sqlmodel import Session,select
from dotenv import load_dotenv
from ..db import engine,redis,redis_ready
from ..utils import isValidPrinter,generate_unique_file_id,get_no_of_pages
from ..db import redis
import aiofiles
import razorpay
import json
from ..configs.dataModels import QueueList
from ..models import Uploaded_Files,Users
from starlette.websockets import WebSocketState

router = APIRouter(prefix="/printers",tags=["printers"])

# all the payloads must contains a key called event
load_dotenv(dotenv_path="../.env")
RAZORPAY_ID = os.environ.get("RAZORPAY_ID")
RAZORPAY_SECRET = os.environ.get("RAZORPAY_SECRET")
razorpay_client = razorpay.Client(auth=(RAZORPAY_ID, RAZORPAY_SECRET))


# connection manager for the printer clients

class ConnectedClientPrinterManager:
    def __init__(self):
        # you have to use redis later
        self.active_connections: dict = {}
        self.active_clients: dict[str,list[WebSocket]] = {}
        self.queue:dict = self.init_queue()
        return None
    
    @staticmethod
    def init_queue():
        #data structure:
        """
        {
            printer_name:[]
        }
        
        """
        data = {

        }
        # await redis_ready.wait()
        # redis.lpush("queue",json.dumps(data))
        return data

    async def connect(self, license_id,websocket: WebSocket):
        await websocket.accept()
        self.active_connections[license_id] = websocket

    async def disconnect(self, license_id,websocket: WebSocket):
        self.active_connections.pop(license_id)
        if  websocket.client_state == WebSocketState.CONNECTED:

            await websocket.close()

    async def connect_client(self, license_id,websocket: WebSocket):
        await websocket.accept()
        if license_id not in self.active_clients:
            self.active_clients[license_id] = []
        self.active_clients[license_id].append(websocket)

    async def disconnect_client(self, license_id,websocket: WebSocket):
        self.active_clients[license_id].remove(websocket)
        if  websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
    
    async def send_personal_message(self, data, printer_name:str):
        await self.active_connections[printer_name].send_json(data)

    async def broadcast(self, message: str): # to all
        for connection in self.active_connections:
            await connection.send_text(message)
    async def broadcast_client(self, message: str,printer_name:str): # to all
        for connection in self.active_clients.keys():
            if self.active_clients[connection] == printer_name:
                await connection.send(message)
data = {
    "queues":str([{
        "file_id":"jobID"
    }]),
    "current_user":""
}




# @depricated
class QueueManager:
    def __init__(self):
        pass
    async def get_all_print_queues(self, printer_name:str):
        return await redis.hget(printer_name, "queues")
    async def get_current_user(self, printer_name:str):
        return await redis.hget(printer_name,"current_user")
    async def push_print_queue(self, printer_name:str,file_id:str, job_id:str):
        list_of_data =  await redis.hget(printer_name, "queues")
        old_queue = list(list_of_data)
        updated_queue = old_queue.append({file_id:job_id})
        await redis.hset(printer_name,"queues",str(updated_queue))
    async def pop_print_queue(self, printer_name:str,file_id:str):
        list_of_data =  await redis.hget(printer_name, "queues")
        old_queue = list(list_of_data)
        # updated_queue = old_queue.remove()


# initializing the managers
printers = ConnectedClientPrinterManager()


@router.post("/queue-controller/{client_license}")
async def queue_controller(client_license:str,data:QueueList):
    if (not isValidPrinter(client_license)):
        raise HTTPException(404, "Not a valid client")
    clients = printers.active_clients
    print(data.queue_list)
    # if not clients:
    #     for client in clients.keys():
    #         if(clients.get(client) == client_license):
    #             await client.send_json


###########################Connection of different printers client:
@router.websocket("/connection/{client_license}/{client_password}")
async def connect_to_server(websocket:WebSocket, client_license:str, client_password:str):
    await printers.connect(client_license, websocket)
    if (not isValidPrinter(client_license)):
        print("printer is not valid")
        await printers.disconnect(client_license,websocket)
        raise  WebSocketException(1008,"license is not valid")
    with Session(engine) as session:
        query = select(Users).where(Users.url_endpoint == client_license)
        user = session.exec(query).one_or_none()
        if(user == None):
            print("User not found")
            await printers.disconnect(client_license,websocket)
            raise  WebSocketException(1008,"license is not valid")
        else:
            if(user.license_password != client_password):
                await printers.disconnect(client_license,websocket)

                raise  WebSocketException(1008,"license is not valid")
    try:
        socket:WebSocket = printers.active_connections[client_license]
        
        while True:

            payload = await socket.receive_text()
            event = json.loads(payload).get("event")
            data:dict = json.loads(payload).get("data")
            match (event):
                case "queue_update":
                    printers.queue[client_license] = data.get("queue")
                    for ws in printers.active_clients[client_license]:
                        await ws.send_json({"queue":printers.queue[client_license]})

    except WebSocketDisconnect as e:
        print(e)
        await printers.disconnect(client_license,websocket)
    except Exception as e:
        print(e)
        # await printers.disconnect(client_license,websocket)
@router.get("/")
def Index(printer_name:str):
    if(not isValidPrinter(printer_name)):
        raise HTTPException(status_code=404, detail="Printer not found with these address")
    return printer_name

@router.post("/upload")
async def upload_file_handler(printer_name:str,file:UploadFile):
    if(not isValidPrinter(printer_name)):
        raise HTTPException(status_code=404, detail="Printer not found with these address")
    # ext,no_of_pages = 

    upload_folder_path = os.environ.get("FILES_PATH")
    file_id   = generate_unique_file_id()
    extension = file.filename.rsplit(".")[len(file.filename.rsplit("."))-1]
    file_name = f"{upload_folder_path}/{file_id}.{extension}"
    print("hello world")

    async with aiofiles.open(file_name,"wb") as f:
        content = await file.read()
        await f.write(content)
    no_of_pages = get_no_of_pages(file_name)
    

    with Session(engine) as session:
        amount_for_user = session.exec(select(Users).where(Users.url_endpoint==printer_name)).one_or_none().amount_per_page
        print(amount_for_user)
        amount = amount_for_user*no_of_pages
        new_file = Uploaded_Files(file_id=file_id,amount=amount,status="FILE UPLOADED BUT NOT PRINTED",printer_name=printer_name,no_of_pages=no_of_pages)
        session.add(new_file)
        session.commit()
    try:
        payload = {

            "event":"file_send",
            
            "data":{
                "extension":extension,  

            "file_id":file_id
            }
        }
        await printers.send_personal_message(payload,printer_name)
        return {
                    "message": "File uploaded!!",
                    "no_of_pages":no_of_pages,
                    "amount":amount,
                    "id":file_id
                }
    except Exception as e:
        print(e)
        print("ksjdhgkjnsdfjkngkjsdnfkjgnjkdsfkjgjkdfskjgjdfkgjk")
        raise HTTPException(403, "Something went unexpected")
    

@router.post("/create-order/{amount}")
def create_order_for_razorpay(amount:int,printer_name:str):
    if(not isValidPrinter(printer_name)):
        raise HTTPException(409, "Unautorized Access")
    currency = "INR"
    order_data = {
        "amount": amount,
        "currency": currency
    }
    razorpay_order = razorpay_client.order.create(data=order_data)
    return {"order_id": razorpay_order['id'], "amount": amount}


@router.post('/verify/{file_id}/{amount}')
async def verify_signature(file_id: int,amount:int,printer_name:str, razorpay_payment_id: str, razorpay_order_id:str, razorpay_signature:str):
    if(not isValidPrinter(printer_name)):
        raise HTTPException(409, "Unautorized Access")
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
        payload = None
        with Session(engine) as session:
            query = select(Uploaded_Files).where(Uploaded_Files.file_id == int(file_id))
            file_uploaded = session.exec(query).one_or_none()

            file_uploaded.payment_id = razorpay_payment_id
            file_uploaded.status = "Payment done xerox is left"
            session.add(file_uploaded)
            session.commit()
            session.refresh(file_uploaded)

            payload = {
            "data":{
            "file_id":file_id},
            "event":"print_file",
        }
        print(payload)
        if payload != None:
            await printers.send_personal_message(payload,printer_name)
       
        return {
            "file_id":file_id,
            "event":"successful"}
    except razorpay.errors.SignatureVerificationError:
        return {
            "data": None,
            "error": "Signature verification failed"
        }, 400

@router.post("/check-valid-printer")
def check_valid_printer(printer_name:str):
    if not isValidPrinter(printer_name):
        raise HTTPException(404,"not found");
    return {
        "valid":True
    }

#client side code for the websocket print queues:
@router.websocket("/queue-clients")
async def queue_clients(printer_name:str,socket:WebSocket):
    await printers.connect_client(printer_name,socket)
    if not isValidPrinter(printer_name):
        print("printer is not valid")
        await printers.disconnect_client(printer_name,socket)
        raise  WebSocketException(1008,"license is not valid")
    try:
        while True:
            d = await socket.receive_text()
    except WebSocketDisconnect as e:
        print("DISCOENN")
        await printers.disconnect_client(printer_name,socket)
    except Exception as e:
        await printers.disconnect_client(printer_name,socket)
# queue manager

# rooms: Dict[str, list[WebSocket]] = {}


# @router.websocket("/queue/{room_id}")
# async def websocket_endpoint(ws: WebSocket, room_id: str):
#     await ws.accept()

#     if room_id not in rooms:
#         rooms[room_id] = []

#     rooms[room_id].append(ws)

#     try:
#         while True:
#             data = await ws.receive_text()

#             # relay message to other peers in the room
#             for peer in rooms[room_id]:
#                 if peer != ws:
#                     await peer.send_text(data)

#     except WebSocketDisconnect:
#         rooms[room_id].remove(ws)

#         if not rooms[room_id]:
#             del rooms[room_id]



######################websocket connection related task here
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/printers/connection/emp8g5t125giy6r3/sadfsdgf`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""





# use your auth tech here


@router.get("/test")
async def get():
    return HTMLResponse(html)


@router.get("/test-2")
async def get2():
    return ""