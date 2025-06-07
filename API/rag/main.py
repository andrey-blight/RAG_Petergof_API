import faiss
import numpy as np
import pickle
import sys
import os
import asyncio
from time import time
from yandex_cloud_ml_sdk import YCloudML
from dotenv import load_dotenv
import aiobotocore.session
import io
import re
from .get_data import get_lists

load_dotenv()

YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY_OCR")
BUCKET_NAME = "markup-baket"
RAG_PATH = "data/rag"


def preprocess_text(text):
    text = re.sub(r"[^\w\s]", "", text).lower()
    return text.split()


async def download_pickle_object(s3_client, key):
    response = await s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
    async with response["Body"] as stream:
        data = await stream.read()
    return pickle.load(io.BytesIO(data))


async def get_answer(index_name, question):
    session = aiobotocore.session.get_session()
    async with session.create_client(
            "s3",
            region_name="ru-central1",
            endpoint_url="https://storage.yandexcloud.net",
            aws_secret_access_key=SECRET_KEY,
            aws_access_key_id=ACCESS_KEY,
    ) as s3_client:

        indices, top_bm25_indices = await get_lists(index_name, question)
        metadata_key = f"{RAG_PATH}/metadata_{index_name}.pkl"
        chunks_key = f"{RAG_PATH}/chunks_{index_name}.pkl"

        metadata, chunks = await asyncio.gather(
            download_pickle_object(s3_client, metadata_key),
            download_pickle_object(s3_client, chunks_key)
        )

    t = time()
    result = ""
    for i, idx in enumerate(indices):
        if idx < len(chunks):
            result += f"Текст {i + 1}:\nФайл: {metadata[idx][0]}, страница: {metadata[idx][1]}\nТекст: {chunks[idx]}\n\n"

    top_k = 18
    for i, idx in enumerate(top_bm25_indices):
        result += f"Текст {top_k + i + 1} (BM25):\nФайл: {metadata[idx]}\nТекст: {chunks[idx]}\n\n"

    print("Forming result:", time() - t)
    t = time()

    messages = [
        {
            "role": "user",
            "text": f"Вы ассистируете научного руководителя музейного комплекса Петергоф. "
                    f"Ниже вам дан контекст, откуда брать информацию. Разрешено брать сразу несколько текстов. "
                    f"Отвечайте на вопросы, которые он задает. Игнорируйте контекст, если считаете его нерелевантным. "
                    f"Ответь на вопрос: {question}. Вместе с ответом также напишите название файла и страницу, "
                    f"откуда была взята информация.\nКонтекст:\n" + result,
        },
    ]

    sdk = YCloudML(
        folder_id=YC_FOLDER_ID,
        auth=YC_API_KEY,
    )

    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None,
                                         lambda: sdk.models.completions("yandexgpt").configure(temperature=0.2).run(
                                             messages))

    print("YaGPT time:", time() - t)
    return answer[0].text


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Недостаточно параметров запуска")
        sys.exit(1)

    index_name = sys.argv[1]
    question = sys.argv[2]

    asyncio.run(get_answer(index_name, question))