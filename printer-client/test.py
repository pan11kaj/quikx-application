import asyncio
import json
import websockets

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import BYE


SIGNALING_URL = "ws://localhost:8000/printers/queue/room1"

class EventSender:
    def __init__(self, channel):
        self.channel = channel

    def send_event(self, event_name: str, payload: dict):
        print(self.channel.readyState)
        if self.channel.readyState == "open":
            print("e")
            message = {
                "event": event_name,
                "payload": payload
            }
            self.channel.send(json.dumps(message))
            print(f"📤 Event sent: {event_name}")


async def run():
    pc = RTCPeerConnection()

    # Create data channel (sender-only client)
    channel = pc.createDataChannel("data")
    sender = EventSender(channel)

    @channel.on("open")
    def on_open():
        print("✅ DataChannel opened")
        channel.send(json.dumps({
            "from": "python",
            "message": "Hello from Python sender"
        }))
        sender.send_event("python_status",{"sy":"hi"})

    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
            if candidate:
                await ws.send(json.dumps({
            "type": "ice",
            "candidate": {
                "candidate": candidate.candidate,
                "sdpMid": candidate.sdpMid,
                "sdpMLineIndex": candidate.sdpMLineIndex
            }
        }))
            elif data["type"] == "ice":
                c = data["candidate"]

                await pc.addIceCandidate(
        RTCIceCandidate(
            candidate=c["candidate"],
            sdpMid=c["sdpMid"],
            sdpMLineIndex=c["sdpMLineIndex"],
        )
    )


    async with websockets.connect(SIGNALING_URL) as ws:
        print("Connected to signaling server")

        # Create offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        # Send offer (SEND ONLY)
        await ws.send(json.dumps({
            "type": "offer",
            "sdp": pc.localDescription.sdp
        }))
        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "answer":
                # ✅ IMPORTANT CHECK
                if pc.signalingState != "have-local-offer":
                    print("⚠️ Answer ignored, state:", pc.signalingState)
                    continue

                print("✅ Applying answer")
                await pc.setRemoteDescription(
                    RTCSessionDescription(
                        sdp=data["sdp"],
                        type="answer"
                    )
                )

            elif data["type"] == "ice":
                await pc.addIceCandidate(data["candidate"])


# if __name__ == "__main__":
#     asyncio.run(run())

import requests
# res = requests.post("http://localhost:8000/printers/queue-controller/12lr4ipekgwva8ls",json={"queue_list":[]})