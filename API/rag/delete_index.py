import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
YANDEX_API_KEY = os.getenv("YC_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YC_FOLDER_ID")


async def delete_index(index_id):
    client = AsyncOpenAI(
        api_key=YANDEX_API_KEY,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=YANDEX_FOLDER_ID,
    )

    deleted_store = await client.vector_stores.delete(index_id)
    print("Vector store удален:", deleted_store)

    return deleted_store
