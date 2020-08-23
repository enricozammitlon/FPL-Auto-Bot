from fpl import FPL
import os

async def Connect(session):
    username=os.environ.get("USERNAME")
    password=os.environ.get("PASSWORD")
    # pylint: disable=too-many-function-args
    fpl = FPL(session)
    print("Logging in...")
    await fpl.login(email=username,password=password)
    print("Login Succeeded!")
    return fpl