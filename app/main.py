import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.middleware import global_exception_handler
from app.security import require_api_key
from app.routers.admin_router import router as admin_router
from app.routers.auth_router import router as auth_router
from app.routers.mavita_router import router as mavita_router
from app.routers.radiantglow_router import router as radiantglow_router


load_dotenv()

# Interactive docs list every route, so they are off unless RADIANTGLOW_API_DOCS_ENABLED=true
_docs = os.environ.get("RADIANTGLOW_API_DOCS_ENABLED", "").lower() == "true"
app = FastAPI(
    docs_url="/docs" if _docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if _docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_exception_handler(Exception, global_exception_handler)

# Every route requires the API key
# Admin routes use their own key (X-Admin-Key), not the client API key
app.include_router(admin_router)
# /api/auth/verify reports whether a key is valid, so it must be reachable without one
app.include_router(auth_router)
app.include_router(mavita_router, dependencies=[Depends(require_api_key)])
app.include_router(radiantglow_router, dependencies=[Depends(require_api_key)])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
