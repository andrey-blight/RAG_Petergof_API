import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
YANDEX_API_KEY = os.getenv("YC_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YC_FOLDER_ID")


async def add_file_to_index(index_id, file_to_add_id):
    client = AsyncOpenAI(
        api_key=YANDEX_API_KEY,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=YANDEX_FOLDER_ID,
    )
    
    print("Добавляем один файл в существующий поисковый индекс...")
    
    await client.vector_stores.files.create(
        vector_store_id=index_id,
        file_id=file_to_add_id
    )
    
    print(f"Файл {file_to_add_id} добавлен в индекс:", index_id)