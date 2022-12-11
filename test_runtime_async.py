import time
import asyncio

async def say_after(delay, what):
    print(f"started say_after {delay} {what}")
    await asyncio.sleep(delay)
    print(what)

async def main():
    task1 = asyncio.create_task(
        say_after(2, "task1")
    )
    task2 = asyncio.create_task(
        say_after(4, "task2")
    )
    print(f"started at {time.strftime('%X')}")
    
    await task1
    await task2

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())