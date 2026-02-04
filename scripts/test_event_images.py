import asyncio
import json
from app.server.api_services_minimal import get_event_images, EventImagesRequest

async def main():
    print('Calling get_event_images for event 1...')
    res = await get_event_images(EventImagesRequest(event_id=1, offset=0, limit=5))
    print('Result:')
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    asyncio.run(main())
