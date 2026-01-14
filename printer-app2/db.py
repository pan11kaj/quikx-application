from sqlmodel import create_engine,SQLModel
from dotenv import load_dotenv
import redis.asyncio as aredis
import asyncio
import os

load_dotenv()
databse_uri = os.environ.get("DATABASE_URI")
redis_connection_url = os.environ.get("REDIS_URL")
engine = create_engine(databse_uri, echo=True)

redis:aredis.Redis|None = None

redis_ready = asyncio.Event()



def init_db():
    global redis
    r = aredis.from_url(redis_connection_url, encoding='utf-8', decode_responses=True)
    redis = r
    redis_ready.set()
    print("redis connected")
    SQLModel.metadata.create_all(engine)