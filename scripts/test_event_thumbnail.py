from app.server.api_services_minimal import get_event_thumbnail

res = get_event_thumbnail(1)
print(type(res))
# If FileResponse, print the path attribute if available
try:
    print(res.path)
except Exception:
    print(res)
