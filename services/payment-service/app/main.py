import os
import sys
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from app.infrastructure.database import close_pool, create_pool, initialize_database
from app.interfaces.router import router

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/app_db"
)
ASYNC_PG_DSN = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool(app, ASYNC_PG_DSN)
    await initialize_database(app.state.db_pool)
    yield
    await close_pool(app)


# Basic JSON logging setup
def _setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


_setup_logging()


app = FastAPI(title="payment-service", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)

# Metrics
request_count = Counter(
    "payment_service_requests_total", "Total requests", ["method", "endpoint"]
)


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    response = await call_next(request)
    return response


app.include_router(router, tags=["payments"])
