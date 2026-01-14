# import redis.asyncio as aredis
# import json
# import asyncio




# async def se():
#     r = aredis.from_url('redis://localhost:6379/0', encoding='utf-8', decode_responses=True)

#     data = {
#         "current_job":"1",
#         "jobs":str([])
#     }
#     await r.hset("abcd",mapping=data)
#     d = await r.hget("abcd","jobs")
#     print(d,type(d))

# asyncio.run(se())


def generator_func():
    num = 0
    yield num 
    num+=1

num = generator_func()

print(next(num))
# print(next(num))