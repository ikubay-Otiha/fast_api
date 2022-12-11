import time

def say_after(delay, what):
    print(f"started say_after {delay} {what}")
    time.sleep(delay)
    print(what)

def main():
    print(f"started at {time.strftime('%X')}")
    say_after(2, "task1")
    say_after(4, "task2")

    print(f"finished at {time.strftime('%X')}")

main()