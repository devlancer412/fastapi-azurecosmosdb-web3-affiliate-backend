import azure.functions as func
import nest_asyncio

from app.init import app

nest_asyncio.apply()

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.AsgiMiddleware(app).handle(req, context)