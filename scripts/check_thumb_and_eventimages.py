from app.server.api_services_minimal import get_event_thumbnail, EventImagesRequest, get_event_images
import asyncio, json

r = get_event_thumbnail(1)
print('Thumbnail served:', getattr(r, 'path', 'no path attr'))
res = asyncio.run(get_event_images(EventImagesRequest(event_id=1, offset=0, limit=5)))
print('Event images result:')
print(json.dumps(res, indent=2))
