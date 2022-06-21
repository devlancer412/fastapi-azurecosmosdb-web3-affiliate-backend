from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.__internal import Function


class Init(Function):

    def __init__(self, _):
        ...

    def Bootstrap(self, app: FastAPI):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )