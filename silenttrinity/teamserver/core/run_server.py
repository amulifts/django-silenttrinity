# silenttrinity/silenttrinity/teamserver/core/run_server.py

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the core package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.server import TeamServer

async def main():
    server = TeamServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())