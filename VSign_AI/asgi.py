import os
from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount
from stgcn_api import app as fastapi_app
from starlette.middleware.cors import CORSMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django_app = get_asgi_application()

# Add CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount FastAPI vào /api
application = Starlette(routes=[
    Mount("/api", app=fastapi_app),
    Mount("/", app=django_app),
])
