import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
YANDEX_API_KEY = os.getenv("YC_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YC_FOLDER_ID")


async def remove_file_from_index(index_id, file_to_delete_id):
    client = AsyncOpenAI(
        api_key=YANDEX_API_KEY,
        base_url="https://ai.api.cloud.yandex.net/v1",
        project=YANDEX_FOLDER_ID,
    )

    print("Удаляем один файл из поискового индекса...")
    
    deleted_file = await client.vector_stores.files.delete(
        file_to_delete_id,
        vector_store_id=index_id
    )
    
    print(f"Файл {file_to_delete_id} удален из индекса:", deleted_file)
    
