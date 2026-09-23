import uvicorn
from fastapi import FastAPI

from gamenet import __version__
from gamenet.server.api.router import api_router
from gamenet.server.config import settings
from gamenet.server.db import run_migrations

app = FastAPI(
    title="GameNet Pro Server",
    version=__version__,
    description="Game-net management server — Source of Truth",
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    run_migrations()


def main() -> None:
    uvicorn.run(
        "gamenet.server.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.app_env == "development",
    )


if __name__ == "__main__":
    main()
