from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.__internal import Function
from config import cfg

class Init(Function):

    def __init__(self, error):
        if cfg.has_unset():
            error(f"Cannot start with unset variables: {cfg.has_unset()}")

    def Bootstrap(self, app: FastAPI):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )