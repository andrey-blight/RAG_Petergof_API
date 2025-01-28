import json
import httpx
import websockets
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.core import settings


async def send_http_request(artikul: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.PARSER_URL, json={"artikul": artikul})

        if response.status_code != 201:
            raise httpx.RequestError("Cannot get info")

        product_json = response.json()
        product_json["action"] = "trigger"
        print(product_json)

        uri = settings.WEB_SOCKET
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(product_json))

    except httpx.RequestError:
        pass


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

scheduler = AsyncIOScheduler(jobstores=jobstores)
