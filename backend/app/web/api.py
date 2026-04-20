import time
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import traffic, weather, prediction, cctv
from app.web.token_header import verify_token
from config import prop, logger

app = FastAPI(title="교통 혼잡 예측 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=prop['web']['allow_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed}ms)")
    return response


app.include_router(traffic.router, prefix="/api/traffic", tags=["traffic"], dependencies=[Depends(verify_token)])
app.include_router(weather.router, prefix="/api/weather", tags=["weather"], dependencies=[Depends(verify_token)])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"], dependencies=[Depends(verify_token)])
app.include_router(cctv.router, prefix="/api/cctv", tags=["cctv"], dependencies=[Depends(verify_token)])


@app.get("/")
def root():
    return {"status": "ok", "message": "교통 혼잡 예측 API"}
