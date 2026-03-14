# from fastapi import FastAPI
# from app.api import stocks, portfolios, news

# app = FastAPI(title="Weave API")

# app.include_router(stocks.router, prefix="/stocks")
# app.include_router(portfolios.router, prefix="/portfolios")
# app.include_router(news.router, prefix="/news")

# @app.get("/")
# def root():
#     return {"status": "Weave API running"}

"""New code below"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

# Import your routers
from app.api import stocks, portfolios, news

app = FastAPI(
    title="Weave API",
    description="Backend engine for the Weave Indian Equity Portfolio Platform",
    version="1.0.0"
)

# --- MIDDLEWARE ---

# 1. CORS Configuration: Essential for your frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Compression: Speeds up large JSON responses (like historical price data)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. Process Time Header: Useful for debugging performance
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- ROUTER INCLUSION ---

app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["Stocks"])
app.include_router(portfolios.router, prefix="/api/v1/portfolios", tags=["Portfolios"])
app.include_router(news.router, prefix="/api/v1/news", tags=["Intelligence"])

# --- ERROR HANDLING ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred.", "details": str(exc)},
    )

# --- ENDPOINTS ---

@app.get("/", tags=["Health"])
def root():
    """
    Service health check endpoint.
    """
    return {
        "status": "online",
        "platform": "Weave",
        "version": "1.0.0",
        "timestamp": time.time()
    }