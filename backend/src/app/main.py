from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, employees, tickets

app = FastAPI(title="Expense Tracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段放开，生产请收敛
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
app.include_router(employees.router, prefix="/employees", tags=["employees"])


@app.get("/health")
async def health():
    return {"status": "ok"}
