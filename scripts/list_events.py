import asyncio
import json
from app.server.api_services_minimal import get_events

async def main():
    res = await get_events()
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
